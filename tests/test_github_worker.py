"""Contract tests for the project-scoped GitHub queue supervisor."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "automation" / "wilsof-github-worker.sh"

STATUS_IN_PROGRESS = "47fc9ee4"
STATUS_READY = "61e4505c"
STATUS_BLOCKED = "1229321a"
STATUS_IN_REVIEW = "35324bed"
STATUS_DONE = "98236657"


class GitHubWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="wilsof-worker-")
        self.root = Path(self.temp.name)
        self.state = self.root / "state"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.comments = "[]"
        self.issues = "[]"
        self.project_items = json.dumps(
            {"items": [{"id": "ITEM", "content": {"type": "Issue", "number": 42},
                        "repository": "https://github.com/tomli0/wilsof-os",
                        "fieldValues": {"nodes": []}}],
             "totalCount": 1}
        )
        self.prs = "[]"
        self.fake_hermes_exit = 0
        gh = self.bin / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys\n"
            "argv = ' '.join(sys.argv)\n"
            "if 'item-edit' in argv:\n"
            "    with open(os.environ['FAKE_PROJECT_LOG'], 'a') as f:\n"
            "        f.write(argv + '\\n')\n"
            "    sys.exit(0)\n"
            "if 'item-list' in argv:\n"
            "    print(os.environ['FAKE_PROJECT_ITEMS']); sys.exit(0)\n"
            "if 'pr list' in argv:\n"
            "    print(os.environ['FAKE_PRS']); sys.exit(0)\n"
            "if 'issue list' in argv:\n"
            "    print(os.environ['FAKE_ISSUES']); sys.exit(0)\n"
            "print(os.environ['FAKE_COMMENTS'])\n"
        )
        gh.chmod(0o755)
        hermes = self.bin / "hermes"
        hermes.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys\n"
            "with open(os.environ['FAKE_HERMES_LOG'], 'a') as f:\n"
            "    f.write(' '.join(sys.argv) + '\\n')\n"
            "sys.exit(int(os.environ.get('FAKE_HERMES_EXIT', '0')))\n"
        )
        hermes.chmod(0o755)
        timeout = self.bin / "timeout"
        timeout.write_text(
            "#!/usr/bin/env python3\n"
            "import subprocess, sys\n"
            "sys.exit(subprocess.run(sys.argv[2:]).returncode)\n"
        )
        timeout.chmod(0o755)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_worker(
        self, *args: str, dry_run: bool = True, budget_sim: bool = False, test_mode: bool = False,
        session_outcome: str = "success",
    ) -> subprocess.CompletedProcess[str]:
        (self.root / "fake-project.log").touch()
        (self.root / "fake-hermes.log").touch()
        env = os.environ | {
            "WILSOF_WORKER_STATE_DIR": str(self.state),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "FAKE_ISSUES": self.issues,
            "FAKE_COMMENTS": self.comments,
            "FAKE_PROJECT_ITEMS": self.project_items,
            "FAKE_PRS": self.prs,
            "FAKE_PROJECT_LOG": str(self.root / "fake-project.log"),
            "FAKE_HERMES_LOG": str(self.root / "fake-hermes.log"),
            "FAKE_HERMES_EXIT": str(self.fake_hermes_exit),
            "HERMES_HOME": str(self.root / "empty-hermes-home"),
            "OPENROUTER_API_KEY": "",
        }
        for var in ("WILSOF_DRY_RUN", "WILSOF_BUDGET_SIMULATED_OK", "WILSOF_TEST_MODE"):
            env.pop(var, None)
        if dry_run:
            env["WILSOF_DRY_RUN"] = "1"
        if budget_sim:
            env["WILSOF_BUDGET_SIMULATED_OK"] = "1"
        if test_mode:
            env["WILSOF_TEST_MODE"] = "1"
            env["WILSOF_TEST_SESSION_OUTCOME"] = session_outcome
        return subprocess.run([str(SCRIPT), *args], text=True, capture_output=True, env=env)

    def project_edits(self) -> list[str]:
        log = self.root / "fake-project.log"
        if not log.exists():
            return []
        return [line for line in log.read_text().splitlines() if line]

    def edited_options(self) -> list[str]:
        return [line.rsplit(" ", 1)[-1] for line in self.project_edits()]

    def candidate(self, number: int = 42) -> None:
        self.issues = json.dumps([{"number": number, "title": "candidate", "labels": [{"name": "hermes-approved"}]}])

    def approved(self) -> None:
        self.comments = json.dumps([{"user": {"login": "tomli0"}, "body": "<!-- hermes-approved -->"}])

    def test_empty_queue_makes_no_model_start(self) -> None:
        result = self.run_worker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("NO_ELIGIBLE_BACKLOG", result.stdout)
        self.assertIn("No model started", result.stdout)

    def test_invalid_approval_is_rejected(self) -> None:
        self.candidate()
        self.comments = json.dumps([{"user": {"login": "someone"}, "body": "<!-- hermes-approved -->"}])
        result = self.run_worker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REJECTED_UNVERIFIED_APPROVAL", result.stdout)

    def test_valid_owner_approval_reaches_model_start_gate(self) -> None:
        self.candidate()
        self.approved()
        result = self.run_worker(budget_sim=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODEL_START_READY", result.stdout)

    def test_budget_gate_requires_explicit_test_simulation(self) -> None:
        source = SCRIPT.read_text()
        self.assertIn('WILSOF_TEST_MODE:-0}" == "1") && "${WILSOF_BUDGET_SIMULATED_OK:-0', source)
        self.candidate()
        self.approved()
        # Live mode with no key: the real budget gate must run and refuse,
        # even when the test simulation flag is set.
        result = self.run_worker(dry_run=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("MODEL_START_READY", result.stdout)
        self.assertIn("OPENROUTER_BUDGET_DENIED: API key unavailable.", result.stdout)

    def test_status_reports_provider_budget_and_session_limits(self) -> None:
        result = self.run_worker("--status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("model_start=enabled", result.stdout)
        self.assertIn("max_failed_attempts=2", result.stdout)
        self.assertIn("work_session_seconds=2700", result.stdout)

    def test_pause_stop_and_resume(self) -> None:
        self.assertIn("PAUSED", self.run_worker("--pause").stdout)
        self.assertIn("PAUSED", self.run_worker().stdout)
        self.assertIn("RESUMED", self.run_worker("--resume").stdout)
        self.assertIn("STOP_REQUESTED", self.run_worker("--stop").stdout)
        self.assertIn("STOP_REQUESTED", self.run_worker().stdout)

    def test_concurrent_lock_probe_is_exclusive(self) -> None:
        lock_dir = self.state / "lock"
        lock_dir.mkdir(parents=True)
        held = subprocess.Popen(["flock", str(lock_dir / "run.lock"), "sleep", "2"])
        try:
            result = self.run_worker("--lock-probe")
            self.assertEqual(result.returncode, 75)
            self.assertIn("LOCK_BUSY", result.stdout)
        finally:
            held.wait(timeout=5)

    def test_stale_lock_is_not_persistent(self) -> None:
        lock_dir = self.state / "lock"
        lock_dir.mkdir(parents=True)
        (lock_dir / "run.lock").write_text("stale pid data\n")
        result = self.run_worker("--lock-probe")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("LOCK_ACQUIRED", result.stdout)

    def test_documented_limits_are_present(self) -> None:
        source = SCRIPT.read_text()
        docs = (ROOT / "docs" / "github-workflow.md").read_text()
        self.assertIn('readonly MAX_ATTEMPTS="2"', source)
        self.assertIn('readonly WORK_SESSION_SECONDS="2700"', source)
        self.assertIn("openrouter.ai/api/v1/key", source)
        self.assertIn("45-minute", docs)
        self.assertIn("hermes-approved", docs)
        self.assertIn("<!-- hermes-approved -->", docs)

    # --- Project synchronization -------------------------------------------

    def test_dry_run_does_not_change_board_status(self) -> None:
        self.candidate()
        self.approved()
        result = self.run_worker(budget_sim=True)
        self.assertIn("MODEL_START_READY", result.stdout)
        self.assertEqual(self.project_edits(), [])

    def test_completed_session_with_open_pr_marks_in_review(self) -> None:
        self.candidate()
        self.approved()
        self.prs = json.dumps([{"number": 7, "headRefName": "issue-42-candidate", "title": "work", "body": ""}])
        result = self.run_worker(dry_run=False, budget_sim=True, test_mode=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODEL_COMPLETED", result.stdout)
        self.assertIn("marked In review", result.stdout)
        self.assertIn(STATUS_IN_REVIEW, self.edited_options())
        self.assertNotIn(STATUS_READY, self.edited_options())
        self.assertNotIn(STATUS_DONE, self.edited_options())

    def test_completed_session_without_pr_keeps_board_status(self) -> None:
        self.candidate()
        self.approved()
        self.prs = "[]"
        result = self.run_worker(dry_run=False, budget_sim=True, test_mode=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODEL_COMPLETED", result.stdout)
        self.assertIn("no open PR found", result.stdout)
        self.assertNotIn(STATUS_READY, self.edited_options())
        self.assertNotIn(STATUS_IN_REVIEW, self.edited_options())

    def test_failed_session_below_max_attempts_does_not_touch_status(self) -> None:
        self.candidate()
        self.approved()
        result = self.run_worker(dry_run=False, budget_sim=True, test_mode=True, session_outcome="failure")
        self.assertEqual(result.returncode, 1)
        self.assertIn("MODEL_FAILED", result.stdout)
        self.assertNotIn(STATUS_READY, self.edited_options())
        self.assertNotIn(STATUS_BLOCKED, self.edited_options())

    def test_failed_session_at_max_attempts_marks_blocked(self) -> None:
        self.candidate()
        self.approved()
        # Seed one already-recorded failed attempt so this run reaches the max.
        (self.state / "attempts.json").parent.mkdir(parents=True, exist_ok=True)
        (self.state / "attempts.json").write_text('{"42": 1}')
        result = self.run_worker(dry_run=False, budget_sim=True, test_mode=True, session_outcome="failure")
        self.assertEqual(result.returncode, 1)
        self.assertIn("2/2", result.stdout)
        self.assertIn(STATUS_BLOCKED, self.edited_options())
        self.assertNotIn(STATUS_READY, self.edited_options())

    def test_test_mode_never_starts_a_model(self) -> None:
        self.candidate()
        self.approved()
        result = self.run_worker(dry_run=False, budget_sim=True, test_mode=True)
        self.assertIn("MODEL_COMPLETED", result.stdout)
        self.assertEqual((self.root / "fake-hermes.log").read_text(), "")

    def test_board_status_does_not_authorize_or_block_execution(self) -> None:
        self.candidate()
        self.approved()
        self.project_items = json.dumps(
            {"items": [{"id": "ITEM", "content": {"type": "Issue", "number": 42},
                        "repository": "https://github.com/tomli0/wilsof-os",
                        "fieldValues": {"nodes": [{"name": "✅ Done"}]}}], "totalCount": 1}
        )
        result = self.run_worker(budget_sim=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODEL_START_READY", result.stdout)

    def test_project_lookup_is_repository_scoped(self) -> None:
        self.candidate()
        self.approved()
        # Same issue number in a different repository must not be edited.
        self.project_items = json.dumps(
            {"items": [{"id": "OTHER", "content": {"type": "Issue", "number": 42},
                        "repository": "https://github.com/tomli0/other-repo",
                        "fieldValues": {"nodes": []}}], "totalCount": 1}
        )
        self.prs = json.dumps([{"number": 7, "headRefName": "issue-42-candidate", "title": "w", "body": ""}])
        result = self.run_worker(dry_run=False, budget_sim=True, test_mode=True)
        self.assertIn("could not mark issue #42 in review", result.stdout)
        self.assertEqual(self.project_edits(), [])

    def test_board_status_alone_does_not_authorize(self) -> None:
        self.issues = "[]"
        self.comments = "[]"
        self.project_items = json.dumps(
            {"items": [{"id": "ITEM", "content": {"type": "Issue", "number": 42},
                        "repository": "https://github.com/tomli0/wilsof-os",
                        "fieldValues": {"nodes": [{"name": "📋 Ready"}]}}], "totalCount": 1}
        )
        result = self.run_worker()
        self.assertIn("NO_ELIGIBLE_BACKLOG", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)