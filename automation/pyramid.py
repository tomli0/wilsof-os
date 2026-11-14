#!/usr/bin/env python3
"""Small host-only execution checkpoint. Never runs commands or grants authority."""
import contextlib
import copy
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

MAX_STATE_BYTES = 1024 * 1024


def approval_map(records):
    result = {}
    for record in records:
        if (not isinstance(record, dict) or not isinstance(record.get("id"), str)
                or not record["id"] or record["id"] in result
                or record.get("status") not in {"required", "satisfied"}
                or not isinstance(record.get("reason"), str) or not record["reason"]):
            raise ValueError("invalid/duplicate approval record")
        result[record["id"]] = record["status"]
    return result


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def select(state):
    # Rankings are estimates, not a claim of measured efficiency.
    from fractions import Fraction
    if state.get("recovery", {}).get("required"):
        return {"action": "RECONCILE_RECOVERY", "task": None, "workstream": None}
    tasks = {t["id"]: t for t in state["tasks"]}
    completed = {t["id"] for t in state["completed_tasks"]
                 if t["id"] not in tasks or t["input_identity"] == tasks[t["id"]]["input_identity"]}
    for attempt in state["attempts"]:
        if attempt["result"] == "RUNNING":
            task = tasks[attempt["task"]]
            return {"action": "RECONCILE", "task": task["id"],
                    "workstream": task["workstream"], "attempt": attempt["id"]}
    attempted = {a["task"] for a in state["attempts"]
                 if a.get("input_identity", tasks[a["task"]]["input_identity"]) == tasks[a["task"]]["input_identity"]}
    blockers = {b["id"] for b in state["current_blockers"]}
    approvals = approval_map(state["required_owner_approvals"])
    candidates = []
    reasons = {}
    for task in tasks.values():
        name = task["id"]
        if name in completed:
            continue
        missing = (["prior attempt requires explicit repair/reconciliation"] if name in attempted else [])
        missing += ["dependency:" + d for d in task["depends_on"] if d not in completed]
        missing += ["blocker:" + b for b in task["blockers"] if b in blockers]
        missing += ["approval:" + a for a in task["approvals"] if approvals.get(a) != "satisfied"]
        if missing:
            reasons[name] = missing
            continue
        score = Fraction(5 * task["impact"] + 3 * task["unblocks"],
                         (task["minutes"] + 5) * (1 + task["risk"] + task["cost"]))
        candidates.append((score, name, task))
    if candidates:
        _, name, task = sorted(candidates, key=lambda row: (-row[0], row[1]))[0]
        return {"action": "EXECUTE", "task": name, "workstream": task["workstream"]}
    return {"action": "BLOCKED" if reasons else "REVIEW_MILESTONE",
            "task": None, "workstream": None, "reasons": reasons}


def validate(state):
    required = {"schema", "objective", "current_milestone", "last_verified_source_commit",
                "last_accepted_iso", "current_blockers", "required_owner_approvals",
                "evidence_refs", "completed_tasks", "attempts", "tasks"}
    optional = {"last_update_utc", "active_workstream", "next_executable_task", "authorities", "integrations", "repairs", "recovery"}
    if not isinstance(state, dict) or not required <= state.keys() or state.keys() - required - optional:
        raise ValueError("invalid state fields")
    if type(state["schema"]) is not int or state["schema"] != 1:
        raise ValueError("unsupported state schema; preserve bytes")
    import re
    if not re.fullmatch(r"[0-9a-f]{40}", state["last_verified_source_commit"]):
        raise ValueError("invalid source commit")
    for key in ("current_blockers", "required_owner_approvals", "evidence_refs", "completed_tasks", "attempts", "tasks"):
        if not isinstance(state[key], list):
            raise ValueError("invalid state list: " + key)
    approval_map(state["required_owner_approvals"])
    if "recovery" in state and (not isinstance(state["recovery"], dict) or type(state["recovery"].get("required")) is not bool):
        raise ValueError("invalid recovery barrier")
    tasks = {}
    for task in state["tasks"]:
        fields = {"id", "workstream", "impact", "unblocks", "minutes", "risk", "cost",
                  "depends_on", "blockers", "approvals", "action", "input_identity"}
        if not isinstance(task, dict) or set(task) != fields or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", task["id"]) or task["id"] in tasks:
            raise ValueError("invalid/duplicate task")
        if task["workstream"] not in {"Product", "QA", "Infrastructure"}:
            raise ValueError("invalid workstream")
        for key in ("impact", "unblocks", "risk", "cost", "minutes"):
            if type(task[key]) is not int or not (0 <= task[key] <= (10000 if key == "minutes" else 5)):
                raise ValueError("invalid task estimate")
        for key in ("depends_on", "blockers", "approvals"):
            if not isinstance(task[key], list) or any(not isinstance(x, str) for x in task[key]):
                raise ValueError("invalid task prerequisites")
        if not task["input_identity"] or not task["action"]:
            raise ValueError("task requires input identity and action")
        tasks[task["id"]] = task
    completed = {t["id"] for t in state["completed_tasks"]}
    if len({(t["id"], t["input_identity"]) for t in state["completed_tasks"]}) != len(state["completed_tasks"]):
        raise ValueError("duplicate completed task")
    def visit(name, trail):
        if name in trail:
            raise ValueError("cyclic task dependency")
        for dep in tasks[name]["depends_on"]:
            if dep not in tasks and dep not in completed:
                raise ValueError("unknown dependency")
            if dep in tasks:
                visit(dep, trail | {name})
    for name in tasks:
        visit(name, set())
    ids = set()
    for attempt in state["attempts"]:
        if attempt["id"] in ids or attempt["task"] not in tasks or attempt["result"] not in {"RUNNING", "PASS", "FAIL", "INTERRUPTED", "BLOCKED"}:
            raise ValueError("invalid attempt history")
        ids.add(attempt["id"])
    if sum(a["result"] == "RUNNING" for a in state["attempts"]) > 1:
        raise ValueError("competing active attempts")
    return state


def decode(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


class Store:
    def __init__(self, path):
        self.path = Path(path).absolute()
        self.previous = self.path.with_suffix(self.path.suffix + ".prev")

    @contextlib.contextmanager
    def lock(self):
        parent = self.path.parent
        parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if parent.resolve() != parent or parent.stat().st_uid != os.getuid() or parent.stat().st_mode & 0o077:
            raise ValueError("state parent must be canonical, private and owned by caller")
        fd = os.open(parent / ".lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_uid != os.getuid() or st.st_mode & 0o077:
                raise ValueError("unsafe state lock")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        finally:
            os.close(fd)

    def raw(self, path):
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            st = os.fstat(stream.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_uid != os.getuid() or st.st_mode & 0o077 or st.st_size > MAX_STATE_BYTES:
                raise ValueError("unsafe/oversized state file")
            return stream.read()

    def read(self):
        return validate(decode(self.raw(self.path)))

    def atomic(self, path, data):
        fd, name = tempfile.mkstemp(prefix=".checkpoint-", dir=self.path.parent)
        # On failure retain the private temporary as diagnostic evidence.
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)

    def save(self, state, previous=None):
        state = copy.deepcopy(validate(state))
        chosen = select(state)
        state.update(last_update_utc=utc(), active_workstream=chosen["workstream"],
                     next_executable_task=chosen["task"] if chosen["action"] == "EXECUTE" else None)
        data = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode()
        if len(data) > MAX_STATE_BYTES:
            raise ValueError("serialized checkpoint exceeds reader limit; both snapshots preserved")
        if previous is not None:
            self.atomic(self.previous, previous)
        self.atomic(self.path, data)
        return state

    def initialize(self, state):
        with self.lock():
            if self.path.exists() or self.path.is_symlink():
                raise ValueError("state exists; reconcile instead of reinitializing")
            return self.save(state)

    def change(self, expected, operation):
        with self.lock():
            old = self.raw(self.path)
            if hashlib.sha256(old).hexdigest() != expected:
                raise ValueError("stale checkpoint; reread before updating")
            state = validate(decode(old))
            operation(state)
            return self.save(state, old)

    def observe(self, changes, expected):
        allowed = {"current_blockers", "required_owner_approvals", "evidence_refs", "last_verified_source_commit"}
        if not set(changes) <= allowed:
            raise ValueError("observation cannot rewrite history/tasks/image acceptance")
        return self.change(expected, lambda state: state.update(changes))

    def begin(self, task, expected):
        import uuid
        def operation(state):
            selected = select(state)
            if selected["action"] != "EXECUTE" or selected["task"] != task:
                raise ValueError("task is not next executable; reconcile rather than replay")
            state["attempts"].append({"id": uuid.uuid4().hex, "task": task,
                                      "input_identity": next(t["input_identity"] for t in state["tasks"] if t["id"] == task),
                                      "result": "RUNNING", "started_utc": utc()})
        return self.change(expected, operation)

    def finish(self, receipt, expected):
        receipt = Path(receipt).absolute()
        raw_receipt = receipt.read_bytes()
        data = decode(raw_receipt)
        if data["result"] not in {"PASS", "FAIL", "INTERRUPTED", "BLOCKED"}:
            raise ValueError("invalid terminal result")
        if type(data["exit_code"]) is not int or not data["milestone_advance"]:
            raise ValueError("missing actual exit/milestone review")
        if data["result"] == "PASS" and (data["exit_code"] != 0 or data["review_accepted"] is not True):
            raise ValueError("successful command alone is not accepted work")
        if not data["evidence"]:
            raise ValueError("evidence required even for failure")
        for ref in data["evidence"]:
            path = Path(ref["path"])
            if not path.is_absolute() or path.resolve(strict=True) != path or not path.is_file() or path.stat().st_nlink != 1 or digest(path) != ref["sha256"]:
                raise ValueError("changed or unsafe evidence")
        binding = {"path": str(receipt), "sha256": hashlib.sha256(raw_receipt).hexdigest()}
        if digest(receipt) != binding["sha256"]:
            raise ValueError("receipt changed after parse")
        def operation(state):
            active = [a for a in state["attempts"] if a["result"] == "RUNNING"]
            if len(active) != 1 or active[0]["id"] != data["attempt"] or active[0]["task"] != data["task"]:
                raise ValueError("receipt does not match running attempt")
            active[0].update(result=data["result"], exit_code=data["exit_code"],
                             finished_utc=utc(), receipt=binding)
            if data["result"] == "PASS":
                task = next(t for t in state["tasks"] if t["id"] == data["task"])
                state["completed_tasks"].append({"id": task["id"], "input_identity": task["input_identity"],
                                                "evidence": [binding], "finished_utc": utc()})
        return self.change(expected, operation)

    def repair(self, path, expected):
        data = decode(Path(path).read_bytes())
        if not data["reason"] or not data["input_identity"] or digest(data["evidence"]["path"]) != data["evidence"]["sha256"]:
            raise ValueError("repair requires documented changed input and verified evidence")
        def operation(state):
            if any(a["result"] == "RUNNING" for a in state["attempts"]):
                raise ValueError("reconcile running work first")
            task = next((t for t in state["tasks"] if t["id"] == data["task"]), None)
            if task is None or task["input_identity"] == data["input_identity"]:
                raise ValueError("repair must identify changed inputs, not repeat unchanged work")
            state.setdefault("repairs", []).append(dict(data, previous_input=task["input_identity"], at_utc=utc()))
            task["input_identity"] = data["input_identity"]
        return self.change(expected, operation)

    def recover(self, expected):
        import uuid
        with self.lock():
            broken = self.raw(self.path)
            if hashlib.sha256(broken).hexdigest() != expected:
                raise ValueError("stale checkpoint")
            try:
                parsed = decode(broken)
            except ValueError:
                parsed = None
            if isinstance(parsed, dict) and parsed.get("schema") not in (None, 1):
                raise ValueError("unknown schema is not corruption; preserve rather than downgrade")
            try:
                validate(parsed)
            except (ValueError, KeyError, TypeError):
                pass
            else:
                raise ValueError("valid state cannot be rolled back with recover")
            previous_raw = self.raw(self.previous)
            previous = validate(decode(previous_raw))
            archive = self.path.with_name(self.path.name + ".corrupt-" + uuid.uuid4().hex)
            self.atomic(archive, broken)
            previous["recovery"] = {"required": True, "at_utc": utc(),
                                    "restored_snapshot_sha256": hashlib.sha256(previous_raw).hexdigest(),
                                    "corrupt": {"path": str(archive), "sha256": hashlib.sha256(broken).hexdigest()}}
            return self.save(previous)

    def reconcile_recovery(self, path, expected):
        import uuid
        data = decode(Path(path).read_bytes())
        if not data["reason"] or digest(data["evidence"]["path"]) != data["evidence"]["sha256"]:
            raise ValueError("recovery reconciliation requires verified native evidence/reason")
        def operation(state):
            if not state.get("recovery", {}).get("required"):
                raise ValueError("no recovery barrier")
            completed = {(c["id"], c["input_identity"]) for c in state["completed_tasks"]}
            pending = {t["id"]: t for t in state["tasks"] if (t["id"], t["input_identity"]) not in completed}
            if set(data["dispositions"]) != set(pending):
                raise ValueError("reconcile every restored unfinished task, not just one")
            for name, task in pending.items():
                disposition = data["dispositions"][name]
                attempted = any(a["task"] == name and a.get("input_identity") == task["input_identity"] for a in state["attempts"])
                if disposition not in {"NOT_STARTED", "RETAIN"} or (disposition == "NOT_STARTED" and attempted):
                    raise ValueError("cannot erase known attempts or assume lost work never started")
                if disposition == "RETAIN" and not attempted:
                    state["attempts"].append({"id": uuid.uuid4().hex, "task": name,
                                              "input_identity": task["input_identity"], "result": "INTERRUPTED",
                                              "exit_code": None, "exit_scope": "checkpoint recovery quarantine; native exit unknown",
                                              "finished_utc": utc(), "receipt": data["evidence"]})
            state["recovery"].update(required=False, reconciliation=data)
        return self.change(expected, operation)


def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=Path(__file__).resolve().parent / ".pyramid/state.json")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "observe"):
        sub = commands.add_parser(name)
        sub.add_argument("--input", type=Path, required=True)
        if name == "observe":
            sub.add_argument("--expected", required=True)
    for name in ("status", "next"):
        commands.add_parser(name)
    for name in ("begin", "finish", "repair", "recover", "reconcile-recovery"):
        sub = commands.add_parser(name)
        sub.add_argument("--expected", required=True)
        if name != "recover":
            sub.add_argument("value")
    args = parser.parse_args()
    store = Store(args.state)
    try:
        if args.command == "init":
            out = store.initialize(decode(args.input.read_bytes()))
        elif args.command == "observe":
            out = store.observe(decode(args.input.read_bytes()), args.expected)
        elif args.command == "begin":
            out = store.begin(args.value, args.expected)
        elif args.command == "finish":
            out = store.finish(args.value, args.expected)
        elif args.command == "repair":
            out = store.repair(args.value, args.expected)
        elif args.command == "recover":
            out = store.recover(args.expected)
        elif args.command == "reconcile-recovery":
            out = store.reconcile_recovery(args.value, args.expected)
        else:
            raw = store.raw(store.path)
            state = validate(decode(raw))
            out = select(state) if args.command == "next" else {"sha256": hashlib.sha256(raw).hexdigest(), "state": state, "selection": select(state)}
        print(json.dumps(out, indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print("REFUSED: " + str(exc) + "; preserve checkpoint/temporaries and reconcile", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
