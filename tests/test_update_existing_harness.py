from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "bin" / "tdd-agent-harness"
CURRENT_TDD_CYCLE = (REPO_ROOT / "scripts" / "tdd-cycle").read_text()
CURRENT_TDD_HARNESS = (REPO_ROOT / "TDD_HARNESS.md").read_text()


class UpdateExistingHarnessTests(unittest.TestCase):
    def run_cli(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(CLI), *args],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if check and result.returncode != 0:
            self.fail(
                "CLI command failed\n"
                f"args: {args}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        return result

    def make_old_harness(self, root: Path) -> None:
        (root / "scripts").mkdir()
        (root / "scripts" / "tdd-cycle").write_text("#!/usr/bin/env python3\nprint('old runner')\n")
        (root / "scripts" / "check").write_text("#!/usr/bin/env bash\necho custom check\n")
        (root / "scripts" / "test-target").write_text("#!/usr/bin/env bash\necho custom target\n")
        (root / "AGENTS.md").write_text("# Custom Agents\n")
        (root / "harness.json").write_text('{"custom": true}\n')
        (root / "SPEC.md").write_text("# Custom Spec\n")
        (root / "TODO.md").write_text("# Custom Todo\n")
        (root / ".gitignore").write_text("dist/\n")

    def test_update_refreshes_managed_runner_and_preserves_project_owned_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.make_old_harness(target)

            result = self.run_cli("update", str(target), "--no-doctor")

            self.assertIn("updated <target>/scripts/tdd-cycle", result.stdout)
            self.assertIn("updated <target>/TDD_HARNESS.md", result.stdout)
            self.assertIn("kept project-owned <target>/scripts/check", result.stdout)
            self.assertIn("kept project-owned <target>/scripts/test-target", result.stdout)
            self.assertIn("kept project-owned <target>/AGENTS.md", result.stdout)
            self.assertIn("Update complete.", result.stdout)
            self.assertIn("Managed files updated: 2", result.stdout)
            self.assertIn("Project-owned files preserved: 6", result.stdout)
            self.assertIn("Doctor: skipped", result.stdout)
            self.assertEqual((target / "scripts" / "tdd-cycle").read_text(), CURRENT_TDD_CYCLE)
            self.assertEqual((target / "TDD_HARNESS.md").read_text(), CURRENT_TDD_HARNESS)
            self.assertEqual((target / "scripts" / "check").read_text(), "#!/usr/bin/env bash\necho custom check\n")
            self.assertEqual((target / "scripts" / "test-target").read_text(), "#!/usr/bin/env bash\necho custom target\n")
            self.assertEqual((target / "AGENTS.md").read_text(), "# Custom Agents\n")
            self.assertEqual((target / "harness.json").read_text(), '{"custom": true}\n')
            self.assertIn(".agent/\n", (target / ".gitignore").read_text())
            mode = (target / "scripts" / "tdd-cycle").stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)

    def test_update_dry_run_does_not_modify_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.make_old_harness(target)
            original_runner = (target / "scripts" / "tdd-cycle").read_text()
            original_gitignore = (target / ".gitignore").read_text()

            result = self.run_cli("update", str(target), "--dry-run", "--no-doctor")

            self.assertIn("would update <target>/scripts/tdd-cycle", result.stdout)
            self.assertIn("would update <target>/TDD_HARNESS.md", result.stdout)
            self.assertIn("Update preview complete.", result.stdout)
            self.assertIn("Managed files to update: 2", result.stdout)
            self.assertIn("Project-owned files preserved: 6", result.stdout)
            self.assertIn("Doctor: skipped", result.stdout)
            self.assertEqual((target / "scripts" / "tdd-cycle").read_text(), original_runner)
            self.assertFalse((target / "TDD_HARNESS.md").exists())
            self.assertEqual((target / ".gitignore").read_text(), original_gitignore)

    def test_update_can_append_agents_router_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.make_old_harness(target)

            result = self.run_cli("update", str(target), "--append-agents", "--no-doctor")

            agents = (target / "AGENTS.md").read_text()
            self.assertIn("appended TDD Harness Mode router to AGENTS.md", result.stdout)
            self.assertIn("# Custom Agents", agents)
            self.assertIn("read `TDD_HARNESS.md` and follow it", agents)
            self.assertNotIn("## Required TDD Sequence", agents)

    def test_install_appends_router_and_copies_detailed_harness_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text("# Existing Project Rules\n\nKeep these.\n")

            result = self.run_cli("install", str(target), "--append-agents", "--no-doctor")

            agents = (target / "AGENTS.md").read_text()
            self.assertIn("appended TDD Harness Mode section to AGENTS.md", result.stdout)
            self.assertIn("# Existing Project Rules", agents)
            self.assertIn("read `TDD_HARNESS.md` and follow it", agents)
            self.assertNotIn("## Required TDD Sequence", agents)
            self.assertEqual((target / "TDD_HARNESS.md").read_text(), CURRENT_TDD_HARNESS)

    def test_update_summary_reports_passed_doctor_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.make_old_harness(target)

            result = self.run_cli("update", str(target))

            self.assertIn("Running doctor...", result.stdout)
            self.assertIn("Update complete.", result.stdout)
            self.assertIn("Doctor: passed", result.stdout)

    def test_update_rejects_directory_without_existing_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            result = self.run_cli("update", str(target), "--no-doctor", check=False)

            self.assertEqual(result.returncode, 66)
            self.assertIn("does not look like an installed TDD harness", result.stderr)


if __name__ == "__main__":
    unittest.main()
