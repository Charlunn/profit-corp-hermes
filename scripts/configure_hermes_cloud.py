#!/usr/bin/env python3
"""Shortcut configurator for Hermes cloud delivery.

This script keeps secrets in local operator files only:
- ~/.hermes/config.yaml
- ~/.hermes/profiles/<role>/config.yaml
- .claude/settings.local.json
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_CONFIG = ROOT_DIR / "config" / "hermes.config.yaml.example"
CLAUDE_SETTINGS = ROOT_DIR / ".claude" / "settings.local.json"
LOCAL_REPORT = ROOT_DIR / ".hermes" / "cloud-config-summary.json"
PROFILES = ["ceo", "scout", "cmo", "arch", "accountant"]
SECRET_KEYS = {
    "api_key",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_API_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "VERCEL_TOKEN",
    "SUPABASE_SERVICE_ROLE_KEY",
    "PAYPAL_CLIENT_SECRET",
}
LOCAL_ENV_KEYS = [
    "NEXT_PUBLIC_SUPABASE_URL",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "NEXT_PUBLIC_PAYPAL_CLIENT_ID",
    "PAYPAL_CLIENT_SECRET",
    "PAYPAL_ENVIRONMENT",
    "APPROVED_DELIVERY_GITHUB_OWNER",
    "APPROVED_DELIVERY_GITHUB_REPO",
    "VERCEL_TEAM",
    "VERCEL_PROJECT",
    "VERCEL_TOKEN",
]
def log(message: str) -> None:
    print(f"[configure-cloud] {message}")


def warn(message: str) -> None:
    print(f"[configure-cloud] WARN: {message}")


def prompt(name: str, default: str = "", *, secret: bool = False, required: bool = False) -> str:
    suffix = f" [{default}]" if default and not secret else ""
    while True:
        if secret:
            value = getpass.getpass(f"{name}{suffix}: ").strip()
        else:
            value = input(f"{name}{suffix}: ").strip()
        if not value:
            value = default
        if value or not required:
            return value
        warn(f"{name} is required.")


def yes_no(question: str, default: bool = True) -> bool:
    label = "Y/n" if default else "y/N"
    answer = input(f"{question} [{label}] ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def hermes_home() -> Path:
    raw = os.environ.get("HERMES_HOME")
    if raw:
        return Path(raw).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".hermes"
    return Path.home() / ".hermes"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        warn(f"Invalid JSON ignored: {path}")
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_local_env() -> dict[str, str]:
    payload = read_json(CLAUDE_SETTINGS)
    env = payload.get("env", {})
    local = {str(k): str(v) for k, v in env.items()} if isinstance(env, dict) else {}
    for key, value in os.environ.items():
        if value.strip():
            local.setdefault(key, value.strip())
    return local


def redact(key: str, value: str) -> str:
    if not value:
        return ""
    if key in SECRET_KEYS or key.endswith("_KEY") or key.endswith("_TOKEN") or key.endswith("_SECRET"):
        return "[configured]"
    return value


def command_status(command: list[str]) -> dict[str, str]:
    if not shutil.which(command[0]):
        return {"status": "missing", "detail": command[0]}
    try:
        result = subprocess.run(command, cwd=ROOT_DIR, capture_output=True, text=True, check=False, encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"status": "error", "detail": str(exc)}
    detail = " ".join((result.stdout or result.stderr or "").split())[:220]
    return {"status": "ok" if result.returncode == 0 else "needs_attention", "detail": detail}


def render_model_config(default_model: str, provider: str, base_url: str, api_key: str) -> str:
    return "\n".join(
        [
            "model:",
            f'  default: "{default_model}"',
            f'  provider: "{provider}"',
            f'  base_url: "{base_url}"',
            f'  api_key: "{api_key}"',
        ]
    )


def replace_model_block(text: str, block: str) -> str:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("model:")), None)
    if start is None:
        return block.rstrip() + "\n\n" + text.rstrip() + "\n"
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        line = lines[idx]
        if line and not line.startswith((" ", "\t")) and ":" in line:
            end = idx
            break
    merged = lines[:start] + block.splitlines() + lines[end:]
    return "\n".join(merged).rstrip() + "\n"


def write_hermes_configs(model_block: str, *, apply_profiles: bool) -> list[str]:
    home = hermes_home()
    home.mkdir(parents=True, exist_ok=True)
    template = TEMPLATE_CONFIG.read_text(encoding="utf-8")
    written: list[str] = []

    config_path = home / "config.yaml"
    config_text = config_path.read_text(encoding="utf-8") if config_path.exists() else template
    config_path.write_text(replace_model_block(config_text, model_block), encoding="utf-8")
    written.append(str(config_path))

    if not apply_profiles:
        return written

    for profile in PROFILES:
        profile_dir = home / "profiles" / profile
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_template = ROOT_DIR / "profiles" / profile / "config.yaml.example"
        target = profile_dir / "config.yaml"
        base = target.read_text(encoding="utf-8") if target.exists() else profile_template.read_text(encoding="utf-8")
        target.write_text(replace_model_block(base, model_block), encoding="utf-8")
        written.append(str(target))
    return written


def update_claude_settings(values: dict[str, str]) -> None:
    payload = read_json(CLAUDE_SETTINGS)
    env = payload.get("env", {})
    if not isinstance(env, dict):
        env = {}
    for key, value in values.items():
        if value:
            env[key] = value
    payload["env"] = env
    write_json(CLAUDE_SETTINGS, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure local Hermes cloud delivery credentials and providers.")
    parser.add_argument("--no-profile-apply", action="store_true", help="Only write ~/.hermes/config.yaml, not role profile configs.")
    parser.add_argument("--skip-checks", action="store_true", help="Do not probe gh/vercel/supabase/claude auth status.")
    args = parser.parse_args()

    local_env = load_local_env()
    log(f"Project root: {ROOT_DIR}")
    log("Secrets will be written only to local ignored/operator config files.")

    default_model = prompt("Hermes default model", local_env.get("HERMES_MODEL", "gpt-5.2"), required=True)
    provider = prompt("Hermes provider", local_env.get("HERMES_PROVIDER", "custom"), required=True)
    base_url = prompt("Hermes provider base_url", local_env.get("HERMES_BASE_URL", ""), required=True)
    api_key = prompt("Hermes provider api_key", local_env.get("HERMES_API_KEY", ""), secret=True, required=True)
    apply_profiles = not args.no_profile_apply and yes_no("Apply this Hermes provider/model to all role profiles?", True)

    claude_base_url = prompt("Claude Code relay base URL", local_env.get("ANTHROPIC_BASE_URL", base_url), required=True)
    claude_key_default = local_env.get("ANTHROPIC_API_KEY") or local_env.get("ANTHROPIC_AUTH_TOKEN") or local_env.get("CLAUDE_CODE_API_KEY", "")
    claude_key = prompt("Claude Code relay api_key/token", claude_key_default, secret=True, required=True)
    claude_model = prompt("Claude Code model", local_env.get("ANTHROPIC_MODEL") or local_env.get("CLAUDE_CODE_MODEL", default_model), required=True)

    env_updates: dict[str, str] = {
        "HERMES_MODEL": default_model,
        "HERMES_PROVIDER": provider,
        "HERMES_BASE_URL": base_url,
        "HERMES_API_KEY": api_key,
        "ANTHROPIC_BASE_URL": claude_base_url,
        "ANTHROPIC_API_KEY": claude_key,
        "ANTHROPIC_AUTH_TOKEN": claude_key,
        "ANTHROPIC_MODEL": claude_model,
        "CLAUDE_CODE_PROVIDER": "custom",
        "CLAUDE_CODE_MODEL": claude_model,
    }

    if yes_no("Configure deployment env values for Supabase/GitHub/Vercel now?", True):
        for key in LOCAL_ENV_KEYS:
            secret = key in SECRET_KEYS or key.endswith("_TOKEN") or key.endswith("_SECRET") or key == "SUPABASE_SERVICE_ROLE_KEY"
            default = local_env.get(key, "")
            value = prompt(key, default, secret=secret, required=False)
            if value:
                env_updates[key] = value

    model_block = render_model_config(default_model, provider, base_url, api_key)
    written_configs = write_hermes_configs(model_block, apply_profiles=apply_profiles)
    update_claude_settings(env_updates)

    checks = {}
    if not args.skip_checks:
        checks = {
            "gh_auth": command_status(["gh", "auth", "status"]),
            "vercel_auth": command_status(["vercel", "whoami"]),
            "supabase_cli": command_status(["supabase", "--version"]),
            "claude_code": command_status(["claude", "--version"]),
            "hermes": command_status(["hermes", "--version"]),
        }

    report = {
        "ok": True,
        "hermes_home": str(hermes_home()),
        "written_configs": written_configs,
        "claude_settings": str(CLAUDE_SETTINGS),
        "configured_env": {key: redact(key, value) for key, value in sorted(env_updates.items())},
        "checks": checks,
    }
    write_json(LOCAL_REPORT, report)

    log(f"Wrote Hermes config(s): {len(written_configs)}")
    log(f"Updated local Claude settings: {CLAUDE_SETTINGS}")
    log(f"Wrote non-secret summary: {LOCAL_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
