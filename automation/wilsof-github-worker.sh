#!/usr/bin/env bash
# Project-scoped GitHub queue supervisor for Wilsof OS.
# Model starts are gated by OpenRouter's provider-enforced key budget.
set -Eeuo pipefail

readonly REPO="${WILSOF_REPOSITORY:-tomli0/wilsof-os}"
readonly OWNER="tomli0"
readonly ROOT="${WILSOF_WORKER_STATE_DIR:-${HERMES_HOME:-$HOME/.hermes}/cron/wilsof-github-worker}"
readonly LOCK_DIR="$ROOT/lock"
readonly LOCK_FILE="$LOCK_DIR/run.lock"
readonly CONTROL_FILE="$ROOT/control.json"
readonly ATTEMPTS_FILE="$ROOT/attempts.json"
readonly MAX_ATTEMPTS="2"
readonly WORK_SESSION_SECONDS="2700"
mkdir -p "$LOCK_DIR"

usage() {
  cat <<'EOF'
Usage: wilsof-github-worker.sh [--status|--pause|--resume|--stop|--lock-probe]

Without an option, checks the approved GitHub queue and starts one bounded model
session only when OpenRouter confirms the active API key has an enforced budget
with positive remaining capacity. The API key is never printed.
EOF
}

read_control() {
  if [[ -f "$CONTROL_FILE" ]]; then
    python3 - "$CONTROL_FILE" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception as exc:
    raise SystemExit(f"FAILED: invalid control state: {exc}")
if not isinstance(data, dict):
    raise SystemExit("FAILED: invalid control state: expected object")
print("1" if data.get("paused", False) else "0")
print("1" if data.get("stop_requested", False) else "0")
PY
  else
    printf '0\n0\n'
  fi
}

write_control() {
  local paused=$1 stop_requested=$2
  python3 - "$CONTROL_FILE" "$paused" "$stop_requested" <<'PY'
import json, os, sys, tempfile
path, paused, stopped = sys.argv[1:]
os.makedirs(os.path.dirname(path), exist_ok=True)
fd, tmp = tempfile.mkstemp(prefix="control.", dir=os.path.dirname(path))
with os.fdopen(fd, "w") as f:
    json.dump({"paused": paused == "1", "stop_requested": stopped == "1"}, f, sort_keys=True)
    f.write("\n")
os.replace(tmp, path)
PY
}

openrouter_budget() {
  # Test-only simulation: a dry run never starts a model, so a simulated OK is
  # harmless there. Live runs (WILSOF_DRY_RUN unset) always hit the real gate.
  if [[ "${WILSOF_DRY_RUN:-0}" == "1" && "${WILSOF_BUDGET_SIMULATED_OK:-0}" == "1" ]]; then
    printf 'OPENROUTER_BUDGET_OK: simulated for dry-run tests.\n'
    return 0
  fi
  python3 - "${HERMES_HOME:-$HOME/.hermes}" <<'PY'
import json, os, pathlib, sys, urllib.request
home = pathlib.Path(sys.argv[1])
key = os.environ.get("OPENROUTER_API_KEY")
if not key:
    env = home / ".env"
    if env.exists():
        for raw in env.read_text().splitlines():
            line = raw.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
if not key:
    print("OPENROUTER_BUDGET_DENIED: API key unavailable.")
    raise SystemExit(2)
try:
    req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.load(response).get("data", {})
except Exception as exc:
    print(f"OPENROUTER_BUDGET_DENIED: key budget check failed ({exc}).")
    raise SystemExit(2)
effective = data.get("effective_budget")
limit = data.get("limit")
remaining = data.get("limit_remaining")
if not effective or limit is None or remaining is None:
    print("OPENROUTER_BUDGET_DENIED: no active provider-enforced key cost limit is reported.")
    raise SystemExit(3)
if float(effective.get("remaining_usd", 0)) <= 0 or float(remaining) <= 0:
    print("OPENROUTER_BUDGET_DENIED: provider-enforced budget has no remaining capacity.")
    raise SystemExit(4)
print("OPENROUTER_BUDGET_OK: " + json.dumps({
    "limit_usd": limit,
    "remaining_usd": remaining,
    "period": data.get("limit_reset"),
    "resets_at": effective.get("resets_at"),
    "effective_scope": effective.get("scope"),
}, sort_keys=True))
PY
}

attempt_count() {
  python3 - "$ATTEMPTS_FILE" "$1" <<'PY'
import json, pathlib, sys
p, issue = pathlib.Path(sys.argv[1]), sys.argv[2]
try: data = json.loads(p.read_text())
except FileNotFoundError: data = {}
except Exception as exc: raise SystemExit(f"FAILED: invalid attempts state: {exc}")
print(int(data.get(issue, 0)))
PY
}

record_failed_attempt() {
  python3 - "$ATTEMPTS_FILE" "$1" <<'PY'
import json, os, pathlib, sys, tempfile
p, issue = pathlib.Path(sys.argv[1]), sys.argv[2]
p.parent.mkdir(parents=True, exist_ok=True)
try: data = json.loads(p.read_text())
except FileNotFoundError: data = {}
data[issue] = int(data.get(issue, 0)) + 1
fd, tmp = tempfile.mkstemp(prefix="attempts.", dir=p.parent)
with os.fdopen(fd, "w") as f: json.dump(data, f, sort_keys=True); f.write("\n")
os.replace(tmp, p)
print(data[issue])
PY
}

clear_attempts() {
  python3 - "$ATTEMPTS_FILE" "$1" <<'PY'
import json, os, pathlib, sys, tempfile
p, issue = pathlib.Path(sys.argv[1]), sys.argv[2]
try: data = json.loads(p.read_text())
except FileNotFoundError: raise SystemExit(0)
data.pop(issue, None)
fd, tmp = tempfile.mkstemp(prefix="attempts.", dir=p.parent)
with os.fdopen(fd, "w") as f: json.dump(data, f, sort_keys=True); f.write("\n")
os.replace(tmp, p)
PY
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then usage; exit 0; fi
if [[ "${1:-}" == "--status" ]]; then
  mapfile -t control < <(read_control)
  printf 'STATUS: model_start=enabled provider_budget_gate=openrouter-key-limit paused=%s stop_requested=%s max_failed_attempts=%s work_session_seconds=%s\n' "${control[0]}" "${control[1]}" "$MAX_ATTEMPTS" "$WORK_SESSION_SECONDS"
  openrouter_budget || true
  exit 0
fi
if [[ "${1:-}" == "--lock-probe" ]]; then
  exec 9>"$LOCK_FILE"
  if flock -n 9; then printf 'LOCK_ACQUIRED\n'; exit 0; fi
  printf 'LOCK_BUSY\n'; exit 75
fi
if [[ "${1:-}" == "--pause" ]]; then write_control 1 0; printf 'PAUSED: queue checks and model starts disabled.\n'; exit 0; fi
if [[ "${1:-}" == "--resume" ]]; then write_control 0 0; printf 'RESUMED: next eligible queue check may start one model session.\n'; exit 0; fi
if [[ "${1:-}" == "--stop" ]]; then write_control 1 1; printf 'STOP_REQUESTED: no new work will start.\n'; exit 0; fi
if [[ $# -ne 0 ]]; then usage >&2; exit 64; fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  printf 'SKIPPED_BUSY: another Wilsof worker or manual session owns %s.\n' "$LOCK_FILE"
  exit 0
fi
mapfile -t control < <(read_control)
if [[ "${control[1]}" == "1" ]]; then printf 'STOP_REQUESTED: queue check not run.\n'; exit 0; fi
if [[ "${control[0]}" == "1" ]]; then printf 'PAUSED: queue check not run.\n'; exit 0; fi

issues=$(gh issue list --repo "$REPO" --state open --label hermes-approved --limit 100 --json number,title,labels)
selected=$(python3 - "$issues" <<'PY'
import json, sys
for item in sorted(json.loads(sys.argv[1]), key=lambda candidate: candidate["number"]):
    if "hermes-approved" in {x["name"] for x in item.get("labels", [])}:
        print(item["number"]); break
PY
)
if [[ -z "$selected" ]]; then printf 'NO_ELIGIBLE_BACKLOG: no open hermes-approved issue. No model started.\n'; exit 0; fi
comments=$(gh api "repos/$REPO/issues/$selected/comments?per_page=100")
if ! python3 - "$comments" "$OWNER" <<'PY'
import json, sys
comments, owner = json.loads(sys.argv[1]), sys.argv[2]
raise SystemExit(0 if any(c.get("user", {}).get("login") == owner and "<!-- hermes-approved -->" in (c.get("body") or "") for c in comments) else 1)
PY
then
  printf 'REJECTED_UNVERIFIED_APPROVAL: issue #%s has no exact owner approval marker from %s. No model started.\n' "$selected" "$OWNER"; exit 0
fi
failed=$(attempt_count "$selected")
if (( failed >= MAX_ATTEMPTS )); then printf 'REJECTED_MAX_ATTEMPTS: issue #%s has %s failed attempts. No model started.\n' "$selected" "$failed"; exit 0; fi
budget=$(openrouter_budget) || { printf '%s\n' "$budget"; exit 0; }
printf '%s\n' "$budget"
if [[ "${WILSOF_DRY_RUN:-0}" == "1" ]]; then printf 'MODEL_START_READY: issue #%s passed all gates (dry run).\n' "$selected"; exit 0; fi
prompt="Work only on GitHub issue #$selected in $REPO. You are the single bounded worker. Work for at most 45 minutes. Preserve repository safety rules, do not merge/deploy/release or perform power/session actions, and leave durable issue/PR checkpoint evidence. Stop and report blockers or checks requiring a physical client."
if timeout --foreground "${WORK_SESSION_SECONDS}s" hermes chat -q "$prompt"; then
  clear_attempts "$selected"
  printf 'MODEL_COMPLETED: issue #%s completed within the bounded session.\n' "$selected"
else
  failures=$(record_failed_attempt "$selected")
  printf 'MODEL_FAILED: issue #%s failed; recorded failed attempt %s/%s.\n' "$selected" "$failures" "$MAX_ATTEMPTS"
  exit 1
fi
