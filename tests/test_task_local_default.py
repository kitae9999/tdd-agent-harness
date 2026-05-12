from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TDD_CYCLE = REPO_ROOT / "scripts" / "tdd-cycle"
ROOT_AGENTS = REPO_ROOT / "AGENTS.md"
ROOT_TDD_HARNESS = REPO_ROOT / "TDD_HARNESS.md"


class TaskLocalDefaultTests(unittest.TestCase):
    def run_cycle(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(TDD_CYCLE), *args],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            self.fail(
                "tdd-cycle command failed\n"
                f"args: {args}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        return result

    def write_templates(self, cwd: Path) -> None:
        (cwd / "SPEC.md").write_text("# Root Spec Template\n\nUse me as a template.\n")
        (cwd / "TODO.md").write_text("# Root Todo Template\n\nUse me as a template.\n")

    def test_start_defaults_to_task_local_state_and_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            self.write_templates(cwd)

            result = self.run_cycle(cwd, "start", "--id", "Checkout Flow", "--reset")

            task_dir = cwd / ".agent" / "tasks" / "checkout-flow"
            self.assertIn("Task: Checkout Flow", result.stdout)
            self.assertIn("Spec: .agent/tasks/checkout-flow/SPEC.md", result.stdout)
            self.assertIn("Todo: .agent/tasks/checkout-flow/TODO.md", result.stdout)
            self.assertTrue((task_dir / "state.json").exists())
            self.assertTrue((task_dir / "SPEC.md").exists())
            self.assertTrue((task_dir / "TODO.md").exists())
            self.assertTrue((task_dir / "logs").is_dir())
            self.assertFalse((cwd / ".agent" / "tdd-state.json").exists())
            self.assertEqual((task_dir / "SPEC.md").read_text(), (cwd / "SPEC.md").read_text())
            self.assertEqual((task_dir / "TODO.md").read_text(), (cwd / "TODO.md").read_text())

            state = json.loads((task_dir / "state.json").read_text())
            self.assertEqual(state["task_id"], "Checkout Flow")
            self.assertEqual(state["spec"], ".agent/tasks/checkout-flow/SPEC.md")
            self.assertEqual(state["todo"], ".agent/tasks/checkout-flow/TODO.md")

    def test_paths_prints_task_local_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            self.write_templates(cwd)

            self.run_cycle(cwd, "start", "--id", "Checkout Flow", "--reset")
            result = self.run_cycle(cwd, "paths", "--task", "Checkout Flow")

            self.assertIn("Task: Checkout Flow", result.stdout)
            self.assertIn("Spec: .agent/tasks/checkout-flow/SPEC.md", result.stdout)
            self.assertIn("Todo: .agent/tasks/checkout-flow/TODO.md", result.stdout)
            self.assertIn("State: .agent/tasks/checkout-flow/state.json", result.stdout)
            self.assertIn("Logs: .agent/tasks/checkout-flow/logs", result.stdout)
            self.assertIn("Report: .agent/tasks/checkout-flow/report.md", result.stdout)

    def test_agents_policy_is_router_not_full_harness_policy(self) -> None:
        agents = ROOT_AGENTS.read_text()
        tdd_harness = ROOT_TDD_HARNESS.read_text()

        self.assertIn("Do not apply TDD Harness Mode by default.", agents)
        self.assertIn("read `TDD_HARNESS.md` and follow it", agents)
        self.assertNotIn("Required TDD Sequence", agents)
        self.assertNotIn("Use test-driven development. The expected output", agents)

        self.assertIn("TDD Harness Mode is active only when the developer explicitly asks", tdd_harness)
        self.assertIn("## Required TDD Sequence", tdd_harness)
        self.assertIn("./scripts/tdd-cycle done --task <task-id>", tdd_harness)


if __name__ == "__main__":
    unittest.main()
