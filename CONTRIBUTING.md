# Engineering guide

> Current workflow authority: [AGENTS.md](AGENTS.md) and the [artifact lifecycle](docs/artifact-maintenance.md). Concise issue #16 close-out replaces historical per-session 12-part reports. Source checks do not imply native, ISO, security or physical acceptance.

Wilsof is a safety-bounded desktop prototype. Prefer a small, reviewed change with direct evidence over a broad rewrite.

## Before changing code

Hermes owns the [artifact lifecycle and end-of-sprint cleanup](docs/artifact-maintenance.md):
Develop → Test → Deliver → Preserve essential evidence → Clean up → Continue.
Every session records actual storage used/reclaimed, protected artifacts,
remaining candidates, active/parked branches and PRs, and Daily Driver blockers.
Cleanup requires exact successful-workflow manifests, read-only planning and an
explicit approved target set; it never restarts paused automation or authorizes
a privileged build. Reuse unchanged test evidence and avoid redundant reports.

- Read the relevant Issue, comments, current branch/worktree state and this guide.
- Reuse the appropriate active branch; create a short-lived branch only for independently reviewable work. Never overwrite another worker's changes.
- Reconcile completed PRs/issues before unrelated work; archive verified source refs before authorized branch retirement.
- Trace the runtime path and check history before treating reported behavior as a defect.
- Keep a single source of truth for a user-facing shortcut, setting or deployment manifest.

## Implementation rules

- Keep components cohesive; make inputs, outputs and ownership explicit.
- Validate untrusted or environment-derived inputs at the boundary. Quote shell expansions, avoid `eval`, preserve command failures and make errors actionable.
- Treat absence separately from failure. Do not hide errors or return success after a failed operation.
- Bound user-triggered work and leave cancellation/cleanup predictable.
- Keep UI/session code unprivileged. A privileged script must state its target, guards and rollback/recovery path.
- Deployment must manage only Wilsof-owned paths, preserve user settings, back up replacements and validate generated configuration before enabling it.
- Do not add credentials, private host details or destructive defaults to the repository.

## Required evidence

Run the checks below before requesting review. Add a focused regression test for each fixed behavior; test a relevant failure mode as well as success. Use temporary directories and mocks for destructive or system operations.

    python3 -m pytest -q
    python3 -c "import ast, pathlib; ast.parse(pathlib.Path('bin/wilsof-profile').read_text())"
    shellcheck --exclude=SC1091 --shell=sh bin/wilsof-doctor bin/wilsof-help bin/wilsof-lock bin/wilsof-search bin/wilsof-vm-test-binds scripts/bootstrap-desktop.sh scripts/build-iso.sh scripts/install-user-config.sh scripts/preflight-arch.sh scripts/preflight-fedora.sh
    shellcheck --shell=bash automation/wilsof-github-worker.sh scripts/install-arch-test-vm.sh iso/profiledef.sh
    python3 -m json.tool config/wilsof-shortcuts.json >/dev/null
    python3 -m json.tool config/dms/settings-template.json >/dev/null
    python3 -m json.tool config/dms/wilsof-theme.json >/dev/null
    git diff --check

Record commands and results in the PR. State the tested commit and any deployed revision separately.

The standalone M1 profile CLI and its headless safety/recovery contract are documented in [Profile State](docs/product/WILSOF_PROFILE_STATE.md). Run focused checks with `python3 -m pytest tests/test_profile.py tests/test_profile_integrity.py tests/test_profile_boundaries.py -q`. M1 changes no desktop provisioning or running session.

## Session close-out and GitHub reporting

Follow the [concise reporting standard](docs/development-reporting.md): retain private receipts, publish verified source changes on the existing delivery branch, and update the sole current dashboard (#16). Answer what works, what is broken, release blockers, next technical action and owner intervention. No report-only branch, repeated full report or duplicate status file. Verify external writes by exact read-back.

This is synchronous normal close-out, not authorization to start a scheduler, worker, new QA round, test, VM, ISO build or installer. For documentation-only reporting, use factual/text/link/diff and sensitive-content checks; do not rerun the application checks above merely to fill the report. Existing review and acceptance boundaries remain. Do not start the next recommended task automatically.

## Review boundary

Review complete execution paths, including installer/configuration deployment, user-setting preservation and session lifecycle. Do not merge, release, deploy, alter repository settings, format disks or perform power/session actions as part of this project workflow.

GUI appearance, physical keyboard routing, password unlock, real idle timeout and login/reboot persistence require a physical client or VM console. Record those as unperformed until directly verified; text checks, CI and file hashes are not substitutes.
