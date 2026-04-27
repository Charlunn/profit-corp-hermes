import json
import shutil
import tempfile
import unittest
from pathlib import Path
import importlib.util


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "validate_delivery_handoff.py"
STAGE_ORDER = [
    ("design", "design-specialist", ".hermes/stage-handoffs/01-design.md"),
    ("development", "development-specialist", ".hermes/stage-handoffs/02-development.md"),
    ("testing", "testing-specialist", ".hermes/stage-handoffs/03-testing.md"),
    ("git versioning", "git-versioning-specialist", ".hermes/stage-handoffs/04-git-versioning.md"),
    ("release readiness", "release-readiness-specialist", ".hermes/stage-handoffs/05-release-readiness.md"),
]
FINAL_ARTIFACT = ".hermes/FINAL_DELIVERY.md"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeliveryRunReplayTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_workspace_fixture(self) -> Path:
        workspace_root = Path(tempfile.mkdtemp(prefix="delivery-replay-workspace-"))
        self.addCleanupPath(workspace_root)
        workspace = workspace_root / "lead-capture"
        hermes_dir = workspace / ".hermes"
        (hermes_dir / "stage-handoffs").mkdir(parents=True, exist_ok=True)
        manifest = {
            "run_id": "delivery-lead-capture-001",
            "workspace_name": "lead-capture",
            "scope_status": "approved-brief-only",
            "stage_order": [stage for stage, _, _ in STAGE_ORDER],
            "stages": [
                {"stage": stage, "role": role, "artifact": artifact}
                for stage, role, artifact in STAGE_ORDER
            ],
            "authority_stream": ".hermes/delivery-events.jsonl",
            "latest_status_path": ".hermes/DELIVERY_STATUS.md",
        }
        (hermes_dir / "delivery-run-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return workspace

    def stage_handoff_markdown(self, run_id: str, role: str, stage: str, next_stage: str) -> str:
        return "\n".join(
            [
                "# 阶段交接",
                "",
                "## 1) Stage Summary",
                f"- `run_id`: {run_id}",
                f"- `role`: {role}",
                f"- `stage`: {stage}",
                "- `scope_status`: approved-brief-only",
                f"- `summary`: {stage} complete",
                "",
                "## 2) Outputs Produced",
                "- 产物 1：artifact",
                "- 产物 2：notes",
                "- 产物 3：checks",
                "",
                "## 3) Evidence Links",
                "- 链接 1：evidence://1",
                "- 链接 2：evidence://2",
                "- 链接 3：evidence://3",
                "",
                "## 4) Gate Decision",
                "- `gate_decision`: PASS",
                "- `reason`: all checks green",
                "",
                "## 5) Open Risks",
                "- 风险项：none",
                "- 影响范围：contained",
                "- 缓解建议：monitor",
                "",
                "## 6) Next Stage Input",
                f"- `next_stage`: {next_stage}",
                "- 下一阶段需要的输入：handoff package",
                "- 注意事项：preserve authority stream",
                "",
            ]
        )

    def final_delivery_markdown(self, run_id: str) -> str:
        return "\n".join(
            [
                "# 最终交付",
                "",
                "## 1) End-to-end Summary",
                f"- `run_id`: {run_id}",
                "- `role`: release-readiness-specialist",
                "- `stage`: release readiness",
                "- `scope_status`: approved-brief-only",
                "- 目标完成情况：done",
                "- 关键改动摘要：validated handoff chain",
                "",
                "## 2) Impact Surface",
                "- UI：landing page",
                "- API：checkout route",
                "- DB：lead_capture_leads",
                "- 权限：no change",
                "- 日志与观测：delivery events verified",
                "",
                "## 3) Test & Verification Evidence",
                "- 主路径验证：pass",
                "- 失败路径验证：pass",
                "- 回归验证：pass",
                "- 证据链接：evidence://release",
                "",
                "## 4) Gate Status Snapshot",
                "- 分层依赖：PASS",
                "- lint/format/type-check：PASS",
                "- 测试证据：PASS",
                "- 日志规范：PASS",
                "- 回滚方案：PASS",
                "",
                "## 5) Rollback Plan",
                "- 回滚触发条件：critical regression",
                "- 回滚步骤：revert release commit",
                "- 回滚验证：rerun smoke tests",
                "",
                "## 6) Release Recommendation",
                "- 建议：可发布",
                "- 风险等级：low",
                "- 说明：ready for handoff",
                "",
            ]
        )

    def write_valid_run(self, workspace: Path) -> None:
        run_id = "delivery-lead-capture-001"
        events = []
        for index, (stage, role, artifact) in enumerate(STAGE_ORDER):
            next_stage = STAGE_ORDER[index + 1][0] if index + 1 < len(STAGE_ORDER) else "none"
            (workspace / artifact).write_text(
                self.stage_handoff_markdown(run_id, role, stage, next_stage),
                encoding="utf-8",
            )
            events.append(
                {
                    "run_id": run_id,
                    "workspace_name": "lead-capture",
                    "role": role,
                    "stage": stage,
                    "action": "stage_completed",
                    "artifact": artifact,
                    "timestamp": f"2026-04-27T10:{index:02d}:00Z",
                    "outcome": "pass",
                    "gate_status": "open",
                    "scope_status": "approved-brief-only",
                }
            )
        (workspace / FINAL_ARTIFACT).write_text(self.final_delivery_markdown(run_id), encoding="utf-8")
        events.append(
            {
                "run_id": run_id,
                "workspace_name": "lead-capture",
                "role": "release-readiness-specialist",
                "stage": "release readiness",
                "action": "final_delivery_validated",
                "artifact": FINAL_ARTIFACT,
                "timestamp": "2026-04-27T10:10:00Z",
                "outcome": "pass",
                "gate_status": "open",
                "scope_status": "approved-brief-only",
            }
        )
        (workspace / ".hermes" / "delivery-events.jsonl").write_text(
            "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
            encoding="utf-8",
        )

    def test_team05_replay_succeeds_with_complete_ordered_handoffs_and_events(self) -> None:
        validate_delivery_handoff = load_module("validate_delivery_handoff", SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        self.write_valid_run(workspace)

        result = validate_delivery_handoff.validate_delivery_run(workspace)
        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["validated_stage_order"], [stage for stage, _, _ in STAGE_ORDER])
        self.assertEqual(result["final_artifact"], FINAL_ARTIFACT)
        self.assertEqual(result["authority_stream"], ".hermes/delivery-events.jsonl")
        self.assertIn("release readiness", result["validated_stage_order"])

    def test_team05_missing_handoff_section_fails_validation(self) -> None:
        validate_delivery_handoff = load_module("validate_delivery_handoff", SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        self.write_valid_run(workspace)

        broken_handoff = workspace / ".hermes" / "stage-handoffs" / "03-testing.md"
        broken_handoff.write_text(
            broken_handoff.read_text(encoding="utf-8").replace("## 4) Gate Decision\n- `gate_decision`: PASS\n- `reason`: all checks green\n\n", ""),
            encoding="utf-8",
        )

        result = validate_delivery_handoff.validate_delivery_run(workspace)
        self.assertFalse(result["ok"])
        self.assertIn("Gate Decision", result["error"])
        self.assertIn("03-testing.md", result["error"])

    def test_team05_skipped_stage_order_or_missing_final_artifact_fails_replay(self) -> None:
        validate_delivery_handoff = load_module("validate_delivery_handoff", SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        self.write_valid_run(workspace)

        events_path = workspace / ".hermes" / "delivery-events.jsonl"
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        skipped = [event for event in events if event["stage"] != "testing"]
        events_path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in skipped) + "\n", encoding="utf-8")
        (workspace / FINAL_ARTIFACT).unlink()

        result = validate_delivery_handoff.validate_delivery_run(workspace)
        self.assertFalse(result["ok"])
        self.assertTrue("testing" in result["error"] or "FINAL_DELIVERY.md" in result["error"])


if __name__ == "__main__":
    unittest.main()
