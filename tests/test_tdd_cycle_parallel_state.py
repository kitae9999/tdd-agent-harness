from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TDD_CYCLE = REPO_ROOT / "scripts" / "tdd-cycle"


class ParallelStateTests(unittest.TestCase):
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

    def read_state(self, cwd: Path, slug: str) -> dict:
        return json.loads((cwd / ".agent" / "tasks" / slug / "state.json").read_text())

    def test_parallel_tasks_use_distinct_state_logs_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)

            self.run_cycle(cwd, "start", "--id", "Alpha Task", "--reset")
            self.run_cycle(cwd, "start", "--id", "Beta Task", "--reset")

            self.assertTrue((cwd / ".agent" / "tasks" / "alpha-task" / "state.json").exists())
            self.assertTrue((cwd / ".agent" / "tasks" / "beta-task" / "state.json").exists())
            self.assertFalse((cwd / ".agent" / "tdd-state.json").exists())

            self.run_cycle(
                cwd,
                "plan",
                "--task",
                "Alpha Task",
                "--summary",
                "alpha plan",
                "--test-command",
                "alpha-test",
                "--playwright",
                "not-applicable",
            )
            self.run_cycle(
                cwd,
                "plan",
                "--task",
                "Beta Task",
                "--summary",
                "beta plan",
                "--test-command",
                "beta-test",
                "--playwright",
                "not-applicable",
            )

            self.run_cycle(
                cwd,
                "red",
                "--task",
                "Alpha Task",
                "--",
                sys.executable,
                "-c",
                "raise SystemExit(1)",
            )
            self.run_cycle(cwd, "review", "--task", "Alpha Task")

            alpha = self.read_state(cwd, "alpha-task")
            beta = self.read_state(cwd, "beta-task")

            self.assertEqual(alpha["task_id"], "Alpha Task")
            self.assertEqual(beta["task_id"], "Beta Task")
            self.assertIn("alpha plan", json.dumps(alpha))
            self.assertIn("beta plan", json.dumps(beta))
            self.assertNotIn("beta plan", json.dumps(alpha))
            self.assertNotIn("alpha plan", json.dumps(beta))

            red_event = next(event for event in alpha["events"] if event["phase"] == "red")
            self.assertTrue(red_event["log_file"].startswith(".agent/tasks/alpha-task/logs/"))
            self.assertTrue((cwd / ".agent" / "tasks" / "alpha-task" / "report.md").exists())
            self.assertFalse((cwd / ".agent" / "report.md").exists())

            status = self.run_cycle(cwd, "status", "--task", "Beta Task")
            self.assertEqual(json.loads(status.stdout)["task_id"], "Beta Task")

    def test_default_state_path_is_task_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)

            self.run_cycle(cwd, "start", "--id", "default-task", "--reset")

            self.assertFalse((cwd / ".agent" / "tdd-state.json").exists())
            self.assertTrue((cwd / ".agent" / "tasks" / "default-task" / "state.json").exists())


if __name__ == "__main__":
    unittest.main()
