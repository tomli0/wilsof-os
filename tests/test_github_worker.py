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


class GitHubWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="wilsof-worker-")
        self.root = Path(self.temp.name)
        self.state = self.root / "state"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.comments = "[]"
        self.issues = "[]"
        gh = self.bin / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys\n"
            "print(os.environ['FAKE_COMMENTS'] if '/comments' in ' '.join(sys.argv) else os.environ['FAKE_ISSUES'])\n"
        )
        gh.chmod(0o755)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_worker(self, *args: str, dry_run: bool = True, budget_sim: bool = False) -> subprocess.CompletedProcess[str]:
        env = os.environ | {
            "WILSOF_WORKER_STATE_DIR": str(self.state),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "FAKE_ISSUES": self.issues,
            "FAKE_COMMENTS": self.comments,
            "HERMES_HOME": str(self.root / "empty-hermes-home"),
            "OPENROUTER_API_KEY": "",
        }
        env.pop("WILSOF_BUDGET_SIMULATED_OK", None)
        if dry_run:
            env["WILSOF_DRY_RUN"] = "1"
        if budget_sim:
            env["WILSOF_BUDGET_SIMULATED_OK"] = "1"
        return subprocess.run([str(SCRIPT), *args], text=True, capture_output=True, env=env)

    def candidate(self) -> None:
        self.issues = json.dumps([{"number": 42, "title": "candidate", "labels": [{"name": "hermes-approved"}]}])

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
        self.comments = json.dumps([{"user": {"login": "tomli0"}, "body": "<!-- hermes-approved -->"}])
        result = self.run_worker(budget_sim=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODEL_START_READY", result.stdout)

    def test_budget_gate_requires_explicit_dry_run_simulation(self) -> None:
        source = SCRIPT.read_text()
        self.assertIn('WILSOF_DRY_RUN:-0}" == "1" && "${WILSOF_BUDGET_SIMULATED_OK:-0', source)
        self.candidate()
        self.comments = json.dumps([{"user": {"login": "tomli0"}, "body": "<!-- hermes-approved -->"}])
        # Live mode with no key: the real budget gate must run and refuse,
        # even when the dry-run simulation flag is set.
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
