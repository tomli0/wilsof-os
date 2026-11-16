"""Host-only orchestration controls; never image/native acceptance."""
import importlib.util
import json
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "automation/pyramid.py"


def api():
    assert MODULE.exists(), "missing persistent Pyramid state implementation"
    spec = importlib.util.spec_from_file_location("pyramid", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed():
    return {
        "schema": 1,
        "objective": "Stable secure maintainable Wilsof OS; preserve Omarchy",
        "current_milestone": {"id": "corrected-rc2", "mandatory_tests": 59,
                              "image_source": "a" * 40, "status": "NOT BUILT"},
        "last_verified_source_commit": "b" * 40,
        "last_accepted_iso": None,
        "current_blockers": [],
        "required_owner_approvals": [],
        "evidence_refs": [],
        "completed_tasks": [],
        "attempts": [],
        "tasks": [task("verify-handoff")],
    }


def task(name, **changes):
    value = {"id": name, "workstream": "QA", "impact": 5, "unblocks": 5,
             "minutes": 5, "risk": 0, "cost": 0, "depends_on": [],
             "blockers": [], "approvals": [], "action": "Inspect retained input",
             "input_identity": "fixture-v1"}
    value.update(changes)
    return value


def test_atomic_checkpoint_and_previous_snapshot(tmp_path):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    original = store.read()
    assert original["next_executable_task"] == "verify-handoff"
    store.observe({"current_blockers": [{"id": "sudo", "reason": "password required"}]},
                  p.digest(store.path))
    assert json.loads(store.previous.read_text()) == original
    assert store.read()["current_blockers"][0]["id"] == "sudo"
    assert store.path.stat().st_mode & 0o777 == 0o600
    assert store.path.parent.stat().st_mode & 0o777 == 0o700


def test_dependency_permission_failure_and_cost_aware_selection():
    p = api()
    s = seed()
    s["tasks"] = [task("cleanup"), task("build", blockers=["sudo"]),
                  task("accept", depends_on=["build"]),
                  task("slow-audit", minutes=100), task("handoff", minutes=2)]
    s["completed_tasks"] = [{"id": "cleanup", "input_identity": "fixture-v1", "evidence": []}]
    s["current_blockers"] = [{"id": "sudo", "reason": "normal authentication required"}]
    assert p.select(s)["task"] == "handoff"
    s["attempts"] = [{"task": "handoff", "result": "FAIL", "id": "retained-failure"}]
    assert p.select(s)["task"] == "slow-audit"
    s["completed_tasks"].append({"id": "slow-audit", "input_identity": "fixture-v1", "evidence": []})
    assert p.select(s)["action"] == "BLOCKED"
    s["attempts"].append({"task": "handoff", "result": "RUNNING", "id": "in-flight"})
    assert p.select(s) == {"action": "RECONCILE", "task": "handoff", "workstream": "QA", "attempt": "in-flight"}


def test_pending_owner_approval_excludes_highest_score():
    p = api()
    s = seed()
    s["tasks"] = [task("build", approvals=["admin"]), task("safe-check", impact=1)]
    s["required_owner_approvals"] = [{"id": "admin", "status": "required", "reason": "separate gate"}]
    assert p.select(s)["task"] == "safe-check"


def receipt(p, root, attempt, result="PASS", exit_code=0):
    evidence = root / (attempt["id"] + ".log")
    evidence.write_text("actual harmless command output\n")
    data = {"attempt": attempt["id"], "task": attempt["task"], "result": result,
            "exit_code": exit_code, "review_accepted": result == "PASS",
            "milestone_advance": "Retained input checked; no ISO acceptance inferred",
            "evidence": [{"path": str(evidence), "sha256": p.digest(evidence)}]}
    path = root / (attempt["id"] + ".json")
    path.write_text(json.dumps(data))
    return path


def test_resume_failure_preservation_and_no_completed_replay(tmp_path):
    p = api()
    s = seed()
    s["tasks"].append(task("next-check", impact=1))
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(s)
    running = store.begin("verify-handoff", p.digest(store.path))
    attempt = running["attempts"][-1]
    # A new Store is a new process/session: in-flight work is reconciled, not rerun.
    resumed = p.Store(store.path)
    assert p.select(resumed.read())["action"] == "RECONCILE"
    with pytest.raises(ValueError):
        resumed.begin("verify-handoff", p.digest(store.path))
    done = resumed.finish(receipt(p, tmp_path, attempt, "FAIL", 17), p.digest(store.path))
    assert done["attempts"][-1]["result"] == "FAIL"
    assert done["attempts"][-1]["exit_code"] == 17
    assert p.select(done)["task"] == "next-check"
    second = resumed.begin("next-check", p.digest(store.path))["attempts"][-1]
    done = resumed.finish(receipt(p, tmp_path, second), p.digest(store.path))
    assert done["completed_tasks"][0]["id"] == "next-check"
    assert done["attempts"][0]["result"] == "FAIL"
    with pytest.raises(ValueError):
        resumed.begin("next-check", p.digest(store.path))
    assert p.select(done)["action"] == "BLOCKED"


@pytest.mark.parametrize("defect", ["tamper", "wrong-attempt", "nonzero-pass", "unreviewed"])
def test_finish_refuses_invalid_evidence_and_preserves_running_state(tmp_path, defect):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    attempt = store.begin("verify-handoff", p.digest(store.path))["attempts"][-1]
    r = receipt(p, tmp_path, attempt)
    data = json.loads(r.read_text())
    if defect == "tamper":
        Path(data["evidence"][0]["path"]).write_text("changed")
    elif defect == "wrong-attempt":
        data["attempt"] = "not-the-running-attempt"
    elif defect == "nonzero-pass":
        data["exit_code"] = 1
    else:
        data["review_accepted"] = False
    r.write_text(json.dumps(data))
    before = store.path.read_bytes()
    with pytest.raises(ValueError):
        store.finish(r, p.digest(store.path))
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("defect", ["schema", "missing", "duplicate-task", "bool-score", "cycle", "unknown-dependency"])
def test_bad_state_refused_before_write(tmp_path, defect):
    p = api()
    s = seed()
    if defect == "schema":
        s["schema"] = True
    elif defect == "missing":
        del s["last_accepted_iso"]
    elif defect == "duplicate-task":
        s["tasks"].append(s["tasks"][0].copy())
    elif defect == "bool-score":
        s["tasks"][0]["impact"] = True
    elif defect == "cycle":
        s["tasks"][0]["depends_on"] = ["verify-handoff"]
    else:
        s["tasks"][0]["depends_on"] = ["unknown"]
    store = p.Store(tmp_path / "private" / "state.json")
    with pytest.raises(ValueError):
        store.initialize(s)
    assert not store.path.exists()


def test_corruption_explicit_recovery_and_failed_rename(tmp_path, monkeypatch):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    original = store.path.read_bytes()
    replace = p.os.replace
    def fail(source, destination):
        if Path(destination) == store.path:
            raise OSError("injected final replacement failure")
        replace(source, destination)
    monkeypatch.setattr(p.os, "replace", fail)
    with pytest.raises(OSError):
        store.observe({"current_blockers": []}, p.digest(store.path))
    assert store.path.read_bytes() == original == store.previous.read_bytes()
    assert list(store.path.parent.glob(".checkpoint-*"))
    monkeypatch.setattr(p.os, "replace", replace)
    store.path.write_bytes(b"{broken")
    with pytest.raises(ValueError):
        store.read()
    store.recover(p.digest(store.path))
    assert store.read()["tasks"] == seed()["tasks"]
    corrupt = list(store.path.parent.glob("state.json.corrupt-*"))
    assert len(corrupt) == 1 and corrupt[0].read_bytes() == b"{broken"


def test_real_cli_checkpoint_lifecycle_and_stale_write(tmp_path):
    import subprocess
    p = api()
    path = tmp_path / "private" / "state.json"
    data = tmp_path / "seed.json"
    data.write_text(json.dumps(seed()))
    def cli(*args):
        return subprocess.run(["python3", str(MODULE), "--state", str(path), *args],
                              capture_output=True, text=True, timeout=10)
    initialized = cli("init", "--input", str(data))
    assert initialized.returncode == 0, initialized.stderr
    selected = cli("next")
    assert json.loads(selected.stdout)["task"] == "verify-handoff"
    sha = p.digest(path)
    started = cli("begin", "verify-handoff", "--expected", sha)
    assert started.returncode == 0, started.stderr
    stale = cli("begin", "verify-handoff", "--expected", sha)
    assert stale.returncode != 0
    assert "stale" in stale.stderr
    status = cli("next")
    assert json.loads(status.stdout)["action"] == "RECONCILE"


def test_explicit_repair_requires_new_input_and_preserves_failed_attempt(tmp_path):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    attempt = store.begin("verify-handoff", p.digest(store.path))["attempts"][-1]
    store.finish(receipt(p, tmp_path, attempt, "FAIL", 17), p.digest(store.path))
    failure = store.read()["attempts"][0].copy()
    repair = tmp_path / "repair.json"
    repair.write_text(json.dumps({"task": "verify-handoff", "input_identity": "fixture-v2",
                                 "reason": "Actual input corrected after inspection", "evidence": failure["receipt"]}))
    store.repair(repair, p.digest(store.path))
    assert p.select(store.read())["task"] == "verify-handoff"
    assert store.read()["attempts"][0] == failure
    next_attempt = store.begin("verify-handoff", p.digest(store.path))["attempts"][-1]
    done = store.finish(receipt(p, tmp_path, next_attempt), p.digest(store.path))
    assert done["attempts"][0]["result"] == "FAIL"
    assert done["attempts"][1]["result"] == "PASS"


def test_receipt_replacement_race_refused(tmp_path, monkeypatch):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    attempt = store.begin("verify-handoff", p.digest(store.path))["attempts"][-1]
    r = receipt(p, tmp_path, attempt)
    read = Path.read_bytes
    def raced(path):
        data = read(path)
        if path == r:
            path.write_text('{"changed":"after receipt parse"}')
        return data
    monkeypatch.setattr(Path, "read_bytes", raced)
    with pytest.raises(ValueError):
        store.finish(r, p.digest(store.path))
    assert store.read()["attempts"][0]["result"] == "RUNNING"


def test_real_killed_writer_retains_checkpoint_and_serializes(tmp_path):
    import subprocess
    import sys
    import time
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    old = store.path.read_bytes()
    marker = tmp_path / "writer-ready"
    code = '''import runpy,sys,pathlib,os
p=runpy.run_path(sys.argv[1]); store=p['Store'](sys.argv[2]); replace=os.replace
'''
    code += '''def barrier(source,destination):
 if pathlib.Path(destination)==store.path:
  pathlib.Path(sys.argv[3]).write_text('ready')
  sys.stdin.buffer.read(1)
 replace(source,destination)
os.replace=barrier
store.observe({'current_blockers':[]},p['digest'](store.path))
'''
    child = subprocess.Popen([sys.executable, "-c", code, str(MODULE), str(store.path), str(marker)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 5
        while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        assert marker.exists(), child.communicate(timeout=1)
        with pytest.raises(BlockingIOError):
            store.observe({"current_blockers": []}, p.digest(store.path))
        child.kill()
        child.communicate(timeout=5)
        assert store.path.read_bytes() == old == store.previous.read_bytes()
        orphans = {x.name: x.read_bytes() for x in store.path.parent.glob(".checkpoint-*")}
        assert orphans
        store.observe({"current_blockers": []}, p.digest(store.path))
        assert all((store.path.parent / name).read_bytes() == data for name, data in orphans.items())
    finally:
        if child.poll() is None:
            child.kill()
        child.communicate(timeout=5)


@pytest.mark.parametrize("defect", ["leaf-symlink", "lock-symlink", "hardlink", "parent-symlink"])
def test_unsafe_checkpoint_paths_refused(tmp_path, defect):
    import os
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    other = tmp_path / "other"
    if defect == "leaf-symlink":
        store.path.rename(other)
        store.path.symlink_to(other)
    elif defect == "lock-symlink":
        (store.path.parent / ".lock").unlink()
        other.write_text("sentinel")
        (store.path.parent / ".lock").symlink_to(other)
    elif defect == "hardlink":
        os.link(store.path, other)
    else:
        alternate = tmp_path / "link"
        alternate.symlink_to(store.path.parent, target_is_directory=True)
        store = p.Store(alternate / "state.json")
    with pytest.raises((ValueError, OSError)):
        store.observe({"current_blockers": []}, "0" * 64)


def test_corruption_after_begin_cannot_replay_restored_pending_task(tmp_path):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    store.begin("verify-handoff", p.digest(store.path))
    store.path.write_bytes(b"{corrupt after durable begin; native work may be live")
    recovered = store.recover(p.digest(store.path))
    assert p.select(recovered)["action"] == "RECONCILE_RECOVERY"
    with pytest.raises(ValueError):
        store.begin("verify-handoff", p.digest(store.path))
    reconciliation = tmp_path / "reconciliation.json"
    proof = tmp_path / "reconciled-native-evidence.log"
    proof.write_text("Synthetic external workload reconciled; retained rather than replayed")
    reconciliation.write_text(json.dumps({"dispositions": {"verify-handoff": "RETAIN"},
                                         "reason": "Lost attempt conservatively quarantined",
                                         "evidence": {"path": str(proof), "sha256": p.digest(proof)}}))
    done = store.reconcile_recovery(reconciliation, p.digest(store.path))
    assert p.select(done)["action"] == "BLOCKED"
    assert done["attempts"][-1]["result"] == "INTERRUPTED"
    assert done["recovery"]["reconciliation"]["evidence"]["path"] == str(proof)


def test_oversized_update_preserves_main_and_previous(tmp_path):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    store.observe({"current_blockers": []}, p.digest(store.path))
    main, previous = store.path.read_bytes(), store.previous.read_bytes()
    with pytest.raises(ValueError):
        store.observe({"evidence_refs": ["x" * 1024 * 1024]}, p.digest(store.path))
    assert store.path.read_bytes() == main
    assert store.previous.read_bytes() == previous


@pytest.mark.parametrize("records", [
    [{"id": "admin", "status": "required", "reason": "pending"},
     {"id": "admin", "status": "satisfied", "reason": "contradiction"}],
    [{"id": "admin", "status": True, "reason": "bad type"}],
    [{"id": "admin", "status": "unknown", "reason": "bad status"}],
    [{"id": "admin", "status": "satisfied"}],
])
def test_malformed_or_duplicate_approvals_refused(tmp_path, records):
    p = api()
    s = seed()
    s["tasks"][0]["approvals"] = ["admin"]
    s["required_owner_approvals"] = records
    store = p.Store(tmp_path / "private" / "state.json")
    with pytest.raises(ValueError):
        store.initialize(s)
    assert not store.path.exists()


def test_future_schema_is_not_corruption_rollback(tmp_path):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    store.observe({"current_blockers": []}, p.digest(store.path))
    future = store.read()
    future["schema"] = 2
    store.path.write_text(json.dumps(future))
    raw = store.path.read_bytes()
    with pytest.raises(ValueError):
        store.recover(p.digest(store.path))
    assert store.path.read_bytes() == raw


@pytest.mark.parametrize("mode", ["not-started", "known-running", "incomplete", "tamper"])
def test_recovery_reconciliation_requires_complete_actual_disposition(tmp_path, mode):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    store.initialize(seed())
    attempt = store.begin("verify-handoff", p.digest(store.path))["attempts"][-1]
    if mode == "known-running":
        store.observe({"current_blockers": []}, p.digest(store.path))
    store.path.write_bytes(b"{broken")
    store.recover(p.digest(store.path))
    proof = tmp_path / "proof"
    proof.write_text("External deterministic reconciliation evidence for fixture only")
    data = {"reason": "fixture workload inspected", "dispositions": {"verify-handoff": "NOT_STARTED"},
            "evidence": {"path": str(proof), "sha256": p.digest(proof)}}
    if mode == "incomplete":
        data["dispositions"] = {}
    if mode == "tamper":
        proof.write_text("changed")
    path = tmp_path / "reconcile.json"
    path.write_text(json.dumps(data))
    if mode == "not-started":
        reconciled = store.reconcile_recovery(path, p.digest(store.path))
        assert p.select(reconciled)["action"] == "EXECUTE"
    else:
        before = store.path.read_bytes()
        with pytest.raises(ValueError):
            store.reconcile_recovery(path, p.digest(store.path))
        assert store.path.read_bytes() == before
        if mode == "known-running":
            data["dispositions"]["verify-handoff"] = "RETAIN"
            path.write_text(json.dumps(data))
            reconciled = store.reconcile_recovery(path, p.digest(store.path))
            assert p.select(reconciled)["action"] == "RECONCILE"
            assert reconciled["attempts"][0]["id"] == attempt["id"]


def test_oversized_initialization_and_extra_fields_never_write(tmp_path):
    p = api()
    store = p.Store(tmp_path / "private" / "state.json")
    s = seed()
    s["objective"] = "x" * 1024 * 1024
    with pytest.raises(ValueError):
        store.initialize(s)
    assert not store.path.exists() and not store.previous.exists()
    s = seed()
    s["surprise"] = True
    with pytest.raises(ValueError):
        store.initialize(s)
    assert not store.path.exists()
