# Engineering guide

Wilsof is a safety-bounded desktop prototype. Prefer a small, reviewed change with direct evidence over a broad rewrite.

## Before changing code

- Read the relevant Issue, comments, current branch/worktree state and this guide.
- Work in an isolated branch or worktree. Do not overwrite another worker's changes.
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
    shellcheck --exclude=SC1091 --shell=sh bin/wilsof-doctor bin/wilsof-help bin/wilsof-lock bin/wilsof-search bin/wilsof-vm-test-binds scripts/bootstrap-desktop.sh scripts/build-iso.sh scripts/install-user-config.sh scripts/preflight-arch.sh scripts/preflight-fedora.sh
    shellcheck --shell=bash automation/wilsof-github-worker.sh scripts/install-arch-test-vm.sh iso/profiledef.sh
    python3 -m json.tool config/wilsof-shortcuts.json >/dev/null
    python3 -m json.tool config/dms/settings-template.json >/dev/null
    python3 -m json.tool config/dms/wilsof-theme.json >/dev/null
    git diff --check

Record commands and results in the PR. State the tested commit and any deployed revision separately.

## Session close-out and GitHub reporting

Every Hermes session, including blocked or documentation-only work, follows the [reporting standard](docs/development-reporting.md): update the checkpoint, write the full 12-part [Markdown report](docs/templates/DEVELOPMENT_REPORT_TEMPLATE.md), commit/push to the authorized branch with remote read-back, update the relevant status issue (#16), and finish with the direct GitHub report link in the terminal. Keep historical evidence separate from new verification. Preserve secrets and private host details locally. If publication is blocked, retain the complete local report and state exactly what was not published.

This is synchronous normal close-out, not authorization to start a scheduler, worker, new QA round, test, VM, ISO build or installer. For documentation-only reporting, use factual/text/link/diff and sensitive-content checks; do not rerun the application checks above merely to fill the report. Existing review and acceptance boundaries remain. Do not start the next recommended task automatically.

## Review boundary

Review complete execution paths, including installer/configuration deployment, user-setting preservation and session lifecycle. Do not merge, release, deploy, alter repository settings, format disks or perform power/session actions as part of this project workflow.

GUI appearance, physical keyboard routing, password unlock, real idle timeout and login/reboot persistence require a physical client or VM console. Record those as unperformed until directly verified; text checks, CI and file hashes are not substitutes.
