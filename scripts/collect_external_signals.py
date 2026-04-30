#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

ROOT_DIR = Path(__file__).resolve().parent.parent
EXTERNAL_DIR = ROOT_DIR / "assets" / "shared" / "external_intelligence"
SOURCES_PATH = EXTERNAL_DIR / "SOURCES.yaml"
LATEST_SUMMARY_PATH = EXTERNAL_DIR / "LATEST_SUMMARY.md"
HISTORY_DIR = EXTERNAL_DIR / "history"
RAW_DIR = EXTERNAL_DIR / "raw"
SIGNALS_PATH = HISTORY_DIR / "signals.jsonl"
RUNS_PATH = HISTORY_DIR / "runs.jsonl"
NORMALIZATION_VERSION = "1"
USER_AGENT = "profit-corp-hermes-external-intelligence/1.0"


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self._skip_depth = 0
        self._texts = []
        self.meta_description = ""
        self.canonical_url = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            if name == "description" and attrs_dict.get("content"):
                self.meta_description = attrs_dict["content"].strip()
        if tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            if rel == "canonical" and attrs_dict.get("href"):
                self.canonical_url = attrs_dict["href"].strip()

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title = f"{self.title} {text}".strip()
            return
        if self._skip_depth:
            return
        self._texts.append(text)

    def evidence_text(self, limit=800):
        joined = " ".join(self._texts)
        return joined[:limit].strip()


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value):
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return value.strip("-") or "source"


def minimal_yaml_load(path):
    sources = []
    current = None
    in_dedupe = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "sources:":
            continue
        if stripped.startswith("version:"):
            continue
        if line.startswith("  - id:"):
            if current:
                sources.append(current)
            current = {"id": stripped.split(":", 1)[1].strip(), "dedupe_key_fields": []}
            in_dedupe = False
            continue
        if current is None:
            continue
        if stripped == "dedupe_key_fields:":
            in_dedupe = True
            continue
        if in_dedupe and stripped.startswith("- "):
            current.setdefault("dedupe_key_fields", []).append(stripped[2:].strip())
            continue
        in_dedupe = False
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip().strip('"')
            if value.lower() == "false":
                current[key] = False
            elif value.lower() == "true":
                current[key] = True
            elif value.isdigit():
                current[key] = int(value)
            else:
                current[key] = value
    if current:
        sources.append(current)
    return {"sources": sources}


def load_sources():
    if yaml is not None:
        with SOURCES_PATH.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    else:
        data = minimal_yaml_load(SOURCES_PATH)
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise ValueError("SOURCES.yaml must contain a top-level 'sources' list")
    return data["sources"]


def validate_source(source):
    required = [
        "id",
        "category",
        "kind",
        "display_name",
        "base_url",
        "collection_method",
        "enabled",
        "poll_window_hours",
        "dedupe_key_fields",
        "notes",
    ]
    missing = [key for key in required if key not in source]
    if missing:
        raise ValueError(f"Source {source.get('id', '<unknown>')} missing keys: {', '.join(missing)}")
    if source["category"] not in {"trend", "competitor", "complaint"}:
        raise ValueError(f"Source {source['id']} has invalid category: {source['category']}")
    if source["kind"] not in {"rss", "page", "search"}:
        raise ValueError(f"Source {source['id']} has unsupported kind: {source['kind']}")
    if not isinstance(source["dedupe_key_fields"], list) or not source["dedupe_key_fields"]:
        raise ValueError(f"Source {source['id']} must define dedupe_key_fields as a non-empty list")
    return source


def fetch_url(url):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "")
        final_url = response.geturl()
    return body, content_type, final_url


def signal_id_for(url, title, published_at):
    basis = f"{url}|{title}|{published_at}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def parse_rss_items(body, fallback_url):
    root = ET.fromstring(body)
    items = []
    channel_items = root.findall("./channel/item")
    atom_entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    if channel_items:
        for item in channel_items:
            title = (item.findtext("title") or "Untitled RSS Item").strip()
            link = (item.findtext("link") or fallback_url).strip()
            published_at = (item.findtext("pubDate") or item.findtext("date") or "").strip()
            summary = (item.findtext("description") or title).strip()
            items.append({
                "title": title,
                "url": link or fallback_url,
                "published_at": published_at,
                "summary": re.sub(r"<[^>]+>", " ", summary),
                "evidence_text": re.sub(r"<[^>]+>", " ", summary),
                "entities": [],
                "tags": ["rss"],
                "language": "unknown",
                "confidence": "medium",
            })
    elif atom_entries:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in atom_entries:
            title = (entry.findtext("atom:title", default="Untitled Atom Entry", namespaces=ns) or "Untitled Atom Entry").strip()
            link_el = entry.find("atom:link", ns)
            link = fallback_url
            if link_el is not None and link_el.attrib.get("href"):
                link = link_el.attrib["href"].strip()
            published_at = (
                entry.findtext("atom:updated", default="", namespaces=ns)
                or entry.findtext("atom:published", default="", namespaces=ns)
            ).strip()
            summary = (
                entry.findtext("atom:summary", default="", namespaces=ns)
                or entry.findtext("atom:content", default=title, namespaces=ns)
            ).strip()
            items.append({
                "title": title,
                "url": link,
                "published_at": published_at,
                "summary": summary,
                "evidence_text": summary,
                "entities": [],
                "tags": ["rss"],
                "language": "unknown",
                "confidence": "medium",
            })
    return items


def parse_search_results(body_text, final_url, display_name):
    parser = VisibleTextParser()
    parser.feed(body_text)
    evidence_text = parser.evidence_text(limit=4000)
    title = parser.title or display_name or final_url
    normalized = re.sub(r"\s+", " ", evidence_text).strip()

    def clean_candidate(text):
        cleaned = re.sub(r"\b(?:authored by|via|hours ago|hour ago|minutes ago|minute ago|days ago|day ago|comments?|caches|archive\.org|ghostarchive|login|search|active|recent)\b", " ", text, flags=re.I)
        cleaned = re.sub(r"\|+", " ", cleaned)
        cleaned = re.sub(r"\b\d+\b", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -|")
        return cleaned[:180].strip()

    candidates = []
    seen = set()

    question_matches = re.findall(r"([A-Z0-9☶][^?]{8,160}\?)", normalized)
    keyword_matches = re.findall(
        r"([A-Z0-9☶][^.?!]{8,180}\b(?:problem|problems|issue|issues|hard|difficult|slow|broken|hate|pain|struggle|wish|need|friction|why)\b[^.?!]{0,80})",
        normalized,
        flags=re.I,
    )

    for raw in question_matches + keyword_matches:
        candidate = clean_candidate(raw)
        key = candidate.lower()
        if len(candidate) < 20 or key in seen:
            continue
        seen.add(key)
        candidates.append(candidate)

    if not candidates:
        chunks = [chunk.strip() for chunk in re.split(r"(?<=[.!?。！？])\s+", normalized) if chunk.strip()]
        for chunk in chunks:
            candidate = clean_candidate(chunk)
            key = candidate.lower()
            if len(candidate) < 20 or key in seen:
                continue
            seen.add(key)
            candidates.append(candidate)
            if len(candidates) >= 5:
                break

    if not candidates:
        candidates = [title]

    items = []
    for index, candidate in enumerate(candidates[:5], start=1):
        items.append({
            "title": candidate[:80],
            "url": final_url,
            "published_at": "",
            "summary": candidate[:280],
            "evidence_text": candidate,
            "entities": [],
            "tags": ["search", "pain-signal"],
            "language": "unknown",
            "confidence": "medium" if "?" in candidate or re.search(r"\b(problem|issue|hard|difficult|pain|struggle|wish|need|why)\b", candidate, re.I) else "low",
        })
    return items


def ensure_dirs():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def load_existing_signal_ids():
    ids = set()
    if not SIGNALS_PATH.exists():
        return ids
    with SIGNALS_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            signal_id = payload.get("signal_id")
            if signal_id:
                ids.add(signal_id)
    return ids


def write_jsonl(path, rows):
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_latest_summary(run_meta, rows):
    sections = {
        "trend": [],
        "competitor": [],
        "complaint": [],
    }
    for row in rows:
        sections.setdefault(row["source_category"], []).append(row)

    def render_section(title, category):
        items = sections.get(category, [])
        if not items:
            return f"## {title}\n- No new signals this run."
        lines = [f"## {title}"]
        for item in items[:10]:
            published = item.get("published_at") or item.get("collected_at") or "unknown"
            lines.append(
                f"- **{item['title']}** ({published}) — {item['url']}\n"
                f"  - source_id: `{item['source_id']}`\n"
                f"  - summary: {item['summary'] or item['evidence_text'][:200] or 'No summary'}"
            )
        return "\n".join(lines)

    failed_sources = run_meta.get("failed_sources", [])
    failed_source_text = ", ".join(failed_sources) if failed_sources else "none"
    content = "\n\n".join([
        "# Latest External Intelligence Summary",
        "## Run Metadata\n"
        f"- **run_id**: {run_meta['run_id']}\n"
        f"- **started_at**: {run_meta['started_at']}\n"
        f"- **completed_at**: {run_meta['completed_at']}\n"
        f"- **new_signal_count**: {run_meta['new_signal_count']}\n"
        f"- **duplicate_signal_count**: {run_meta['duplicate_signal_count']}\n"
        f"- **failed_source_count**: {run_meta['failed_source_count']}\n"
        f"- **failed_sources**: {failed_source_text}",
        "## Normalized Signal Schema\n"
        "- `signal_id`\n"
        "- `source_id`\n"
        "- `source_category`\n"
        "- `collected_at`\n"
        "- `published_at`\n"
        "- `title`\n"
        "- `summary`\n"
        "- `url`\n"
        "- `evidence_text`\n"
        "- `entities`\n"
        "- `tags`\n"
        "- `language`\n"
        "- `confidence`\n"
        "- `raw_artifact_path`\n"
        "- `normalization_version`",
        render_section("Trend Signals", "trend"),
        render_section("Competitor Signals", "competitor"),
        render_section("Complaint Signals", "complaint"),
    ])
    LATEST_SUMMARY_PATH.write_text(content + "\n", encoding="utf-8")


def persist_raw(source_id, payload, timestamp):
    source_dir = RAW_DIR / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    raw_path = source_dir / f"{timestamp}.json"
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return raw_path.relative_to(ROOT_DIR).as_posix()


def normalize_item(item, source, raw_artifact_path, collected_at):
    published_at = item.get("published_at", "")
    url = item.get("url") or source.get("base_url") or ""
    title = item.get("title") or source["display_name"]
    return {
        "signal_id": signal_id_for(url, title, published_at),
        "source_id": source["id"],
        "source_category": source["category"],
        "collected_at": collected_at,
        "published_at": published_at,
        "title": title,
        "summary": item.get("summary", ""),
        "url": url,
        "evidence_text": item.get("evidence_text", ""),
        "entities": item.get("entities", []),
        "tags": item.get("tags", []),
        "language": item.get("language", "unknown"),
        "confidence": item.get("confidence", "low"),
        "raw_artifact_path": raw_artifact_path,
        "normalization_version": NORMALIZATION_VERSION,
    }


def collect_source(source, args, existing_ids, new_rows, run_meta):
    if not source.get("base_url"):
        raise ValueError(f"Source {source['id']} has empty base_url")
    fetched_at = now_iso()
    body, content_type, final_url = fetch_url(source["base_url"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    body_text = body.decode("utf-8", errors="replace")
    raw_payload = {
        "source_id": source["id"],
        "source_category": source["category"],
        "kind": source["kind"],
        "fetched_at": fetched_at,
        "requested_url": source["base_url"],
        "final_url": final_url,
        "content_type": content_type,
        "body": body_text,
    }

    raw_artifact_path = f"assets/shared/external_intelligence/raw/{source['id']}/{timestamp}.json"
    if not args.dry_run:
        raw_artifact_path = persist_raw(source["id"], raw_payload, timestamp)

    if source["kind"] == "rss":
        items = parse_rss_items(body, final_url)
    elif source["kind"] == "search":
        items = parse_search_results(body_text, final_url, source["display_name"])
    else:
        items = [parse_page_item(body_text, final_url, source["display_name"])]

    if not items:
        run_meta["empty_source_count"] += 1
        return

    for item in items:
        normalized = normalize_item(item, source, raw_artifact_path, fetched_at)
        if normalized["signal_id"] in existing_ids:
            run_meta["duplicate_signal_count"] += 1
            continue
        existing_ids.add(normalized["signal_id"])
        new_rows.append(normalized)
        run_meta["new_signal_count"] += 1


def filter_sources(sources, source_id=None):
    filtered = []
    for source in sources:
        validate_source(source)
        if source_id and source["id"] != source_id:
            continue
        if not source.get("enabled", False):
            continue
        filtered.append(source)
    if filtered:
        return filtered

    fallback_candidates = [
        os.environ.get("HERMES_DISCOVERY_SEARCH_URL", "").strip(),
        "https://lobste.rs/",
        "https://news.ycombinator.com/",
    ]
    fallback_sources = []
    for index, url in enumerate([candidate for candidate in fallback_candidates if candidate], start=1):
        fallback_sources.append({
            "id": f"web-discovery-default-{index}",
            "category": "complaint",
            "kind": "search",
            "display_name": f"Web Discovery Default {index}",
            "base_url": url,
            "collection_method": "search",
            "enabled": True,
            "poll_window_hours": 24,
            "dedupe_key_fields": ["url", "title", "published_at"],
            "notes": "Fallback live discovery seed when no explicit sources are enabled.",
        })
    return fallback_sources


def main():
    parser = argparse.ArgumentParser(description="Collect and normalize external intelligence signals.")
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source-id")
    args = parser.parse_args()

    if not SOURCES_PATH.exists():
        print(f"Missing source registry: {SOURCES_PATH}", file=sys.stderr)
        return 1

    ensure_dirs()
    try:
        sources = load_sources()
        enabled_sources = filter_sources(sources, source_id=args.source_id)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    run_started = now_iso()
    existing_ids = load_existing_signal_ids()
    new_rows = []
    run_meta = {
        "run_id": datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ"),
        "started_at": run_started,
        "completed_at": None,
        "window_hours": args.window_hours,
        "source_filter": args.source_id or "all",
        "processed_source_count": 0,
        "new_signal_count": 0,
        "duplicate_signal_count": 0,
        "failed_source_count": 0,
        "failed_sources": [],
        "empty_source_count": 0,
        "dry_run": args.dry_run,
    }

    for source in enabled_sources:
        try:
            collect_source(source, args, existing_ids, new_rows, run_meta)
            run_meta["processed_source_count"] += 1
        except Exception as exc:
            run_meta["failed_source_count"] += 1
            run_meta["failed_sources"].append(source["id"])
            print(f"[collect] {source['id']} failed: {exc}", file=sys.stderr)

    run_meta["completed_at"] = now_iso()

    if not args.dry_run:
        if new_rows:
            write_jsonl(SIGNALS_PATH, new_rows)
        write_jsonl(RUNS_PATH, [run_meta])
        write_latest_summary(run_meta, new_rows)

    print(json.dumps({
        "run_id": run_meta["run_id"],
        "processed_source_count": run_meta["processed_source_count"],
        "new_signal_count": run_meta["new_signal_count"],
        "duplicate_signal_count": run_meta["duplicate_signal_count"],
        "failed_source_count": run_meta["failed_source_count"],
        "signals_path": str(SIGNALS_PATH.relative_to(ROOT_DIR)).replace("\\", "/"),
        "runs_path": str(RUNS_PATH.relative_to(ROOT_DIR)).replace("\\", "/"),
        "dry_run": args.dry_run,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
