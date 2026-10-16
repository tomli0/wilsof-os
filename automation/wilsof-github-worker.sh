#!/usr/bin/env bash
# Project-scoped, model-free GitHub queue supervisor for Wilsof OS.
# It deliberately does not invoke Hermes or any model: a reliable per-task,
# cross-session USD cap cannot be enforced with the available provider usage API.
set -Eeuo pipefail

readonly REPO="${WILSOF_REPOSITORY:-tomli0/wilsof-os}"
readonly OWNER="tomli0"
readonly ROOT="${WILSOF_WORKER_STATE_DIR:-${HERMES_HOME:-$HOME/.hermes}/cron/wilsof-github-worker}"
readonly LOCK_DIR="$ROOT/lock"
readonly LOCK_FILE="$LOCK_DIR/run.lock"
readonly CONTROL_FILE="$ROOT/control.json"
readonly DAILY_CAP_USD="5"
readonly MAX_ATTEMPTS="2"
mkdir -p "$LOCK_DIR"

usage() {
  cat <<'EOF'
Usage: wilsof-github-worker.sh [--status|--pause|--resume|--stop|--lock-probe]

Without an option, performs a model-free GitHub queue check. A candidate must:
  * be open;
  * have the hermes-approved label; and
  * contain a GitHub issue comment authored by tomli0 with the exact marker
    <!-- hermes-approved -->.

The worker never starts a model. It prints a clear refusal for --model-start,
because a reliable per-task daily USD cap is not available from this runtime.
EOF
}

read_control() {
  if [[ -f "$CONTROL_FILE" ]]; then
    python3 - "$CONTROL_FILE" <<'PY'
import json, sys
p = sys.argv[1]
try:
    data = json.load(open(p))
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

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then usage; exit 0; fi
if [[ "${1:-}" == "--status" ]]; then
  mapfile -t control < <(read_control)
  printf 'STATUS: model_start=disabled daily_cap_usd=%s paused=%s stop_requested=%s max_attempts=%s\n' "$DAILY_CAP_USD" "${control[0]}" "${control[1]}" "$MAX_ATTEMPTS"
  exit 0
fi
if [[ "${1:-}" == "--lock-probe" ]]; then
  exec 9>"$LOCK_FILE"
  if flock -n 9; then printf 'LOCK_ACQUIRED\n'; exit 0; fi
  printf 'LOCK_BUSY\n'; exit 75
fi
if [[ "${1:-}" == "--pause" ]]; then write_control 1 0; printf 'PAUSED: queue checks disabled.\n'; exit 0; fi
if [[ "${1:-}" == "--resume" ]]; then write_control 0 0; printf 'RESUMED: next queue check may run.\n'; exit 0; fi
if [[ "${1:-}" == "--stop" ]]; then write_control 1 1; printf 'STOP_REQUESTED: no new work will start.\n'; exit 0; fi
if [[ "${1:-}" == "--model-start" ]]; then
  printf 'MODEL_START_DISABLED: reliable per-task USD %s/day enforcement is unavailable; only model-free queue checks are enabled.\n' "$DAILY_CAP_USD"
  exit 0
fi
if [[ $# -ne 0 ]]; then usage >&2; exit 64; fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  printf 'SKIPPED_BUSY: another Wilsof queue check or manual session owns %s.\n' "$LOCK_FILE"
  exit 0
fi

mapfile -t control < <(read_control)
if [[ "${control[1]}" == "1" ]]; then
  printf 'STOP_REQUESTED: queue check not run.\n'
  exit 0
fi
if [[ "${control[0]}" == "1" ]]; then
  printf 'PAUSED: queue check not run.\n'
  exit 0
fi

# Fetch only labelled candidates. No model is invoked for an empty or rejected queue.
issues=$(gh issue list --repo "$REPO" --state open --label hermes-approved --limit 100 --json number,title,labels)
selected=$(python3 - "$issues" <<'PY'
import json, sys
items = json.loads(sys.argv[1])
for item in items:
    labels = {x["name"] for x in item.get("labels", [])}
    if "hermes-approved" in labels:
        print(item["number"])
        break
PY
)
if [[ -z "$selected" ]]; then
  printf 'NO_ELIGIBLE_BACKLOG: no open hermes-approved issue. No model started.\n'
  exit 0
fi

comments=$(gh api "repos/$REPO/issues/$selected/comments?per_page=100")
if ! python3 - "$comments" "$OWNER" <<'PY'
import json, sys
comments, owner = json.loads(sys.argv[1]), sys.argv[2]
marker = "<!-- hermes-approved -->"
raise SystemExit(0 if any(c.get("user", {}).get("login") == owner and marker in (c.get("body") or "") for c in comments) else 1)
PY
then
  printf 'REJECTED_UNVERIFIED_APPROVAL: issue #%s has hermes-approved but no exact owner approval marker from %s. No model started.\n' "$selected" "$OWNER"
  exit 0
fi

printf 'ELIGIBLE_TASK: issue #%s passed label and owner-marker checks; automatic model execution remains disabled because the USD %s/day cap is not reliably enforceable.\n' "$selected" "$DAILY_CAP_USD"
