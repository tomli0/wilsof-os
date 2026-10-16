# Bounded GitHub workflow

GitHub Issues are the task queue and GitHub pull requests/issues are the durable evidence source for Wilsof work. This workflow uses the existing Hermes cron scheduler and existing serialized worker pattern; it does not create a second worker platform.

## Current operating mode

The scheduler runs one project-scoped, model-free queue check every hour. The check makes no model call when the queue is empty, rejected, paused, blocked, or ready for review. It never deploys, merges, releases, builds an ISO, logs out, reboots, locks a session, suspends, or performs a power action.

Automatic model execution is disabled. Hermes can report provider-wide OpenRouter spend, but that value is neither atomic nor attributable to an individual task/run and cannot reliably enforce a shared USD 5/day ceiling across manual and scheduled starts. The same supervisor therefore refuses `--model-start`; enabling it would violate the budget requirement.

The daily cap remains USD 5 as the approval boundary. Existing lower provider/account limits remain in effect. A later model-enabled design must first prove an atomic shared ledger/reservation that covers both manual and scheduled runs before this setting can change.

## Selecting a task

A candidate must meet all of the following:

1. It is an open GitHub Issue in `tomli0/wilsof-os`.
2. It has the `hermes-approved` label.
3. It has an Issue comment authored by `tomli0` containing the exact marker:

   `<!-- hermes-approved -->`

The label alone is insufficient. The marker is intentionally checked with GitHub's reported comment author, so public comments, issue bodies, and comments by other accounts cannot authorize work. Tasks tagged blocked or ready-for-review are not relabelled as candidates and are not retried by the queue scanner.

## Limits and coordination

- One worker and one task at a time; an advisory `flock` protects both manual and scheduled checks.
- A future model-enabled runner must impose a 45-minute wall-clock limit and persist at most two failed attempts per issue before setting it blocked. The model-free supervisor does not consume retries.
- `flock` is released automatically if a process dies; no stale PID lock needs manual deletion.
- `--pause` and `--stop` persist control state. `--resume` clears it. The cron job can additionally be paused/resumed through Hermes.
- A run started while another check or a declared manual development session owns the same lock exits as `SKIPPED_BUSY`.

## Operator commands

The scheduler script is installed at `~/.hermes/scripts/wilsof-github-worker.sh` and its cron job id is recorded by `hermes cron list`.

```
# Status and queue scan (manual; no model is started)
~/.hermes/scripts/wilsof-github-worker.sh --status
~/.hermes/scripts/wilsof-github-worker.sh

# Explicitly confirm that automatic model start is disabled
~/.hermes/scripts/wilsof-github-worker.sh --model-start

# Pause, stop, resume the project worker
~/.hermes/scripts/wilsof-github-worker.sh --pause
~/.hermes/scripts/wilsof-github-worker.sh --stop
~/.hermes/scripts/wilsof-github-worker.sh --resume

# Inspect, manually queue, pause, resume or stop the existing Hermes schedule
hermes cron list
hermes cron run <job-id>
hermes cron pause <job-id>
hermes cron resume <job-id>
```

`hermes cron run` invokes the same script and lock as the hourly schedule. It remains model-free. Do not run a separate worker while an active manual implementation session is changing this repository.

## Checkpoint and evidence rules

Any future model-enabled task must write a concise repository checkpoint with issue number, branch, base SHA, tested SHA, deployment SHA (if any), commands/results, blocker/review state, and explicit human checks. Update the Issue and PR with the same evidence. Never describe deployed, tested, or merged revisions as interchangeable.

Physical keyboard routing, local-password unlock, visual acceptance, actual five-minute idle lock, suspend behavior, and graphical persistence are human/VM-console checks unless separately recorded with evidence. The worker must leave those checks unclaimed.
