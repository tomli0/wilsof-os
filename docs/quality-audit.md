# Engineering quality audit

Audited revision: `d4cb093` (`main`), 2026-10-16.

This is a code and automated-test review, not a claim of GUI or physical-client validation.

## Fixed in this change

### High: validation did not cover every executable shell path

Evidence: `.github/workflows/validate.yml` ran `sh -n` over a subset of files. It omitted `bin/wilsof-doctor` and the Bash queue supervisor, while `scripts/install-arch-test-vm.sh` has a Bash shebang. Applying `sh -n` indiscriminately also rejects valid Bash syntax. A local reproduction of the README's old blanket `sh -n` command failed on the Python help renderer and Bash worker.

Implication: a syntax or shell-portability regression in a user-facing diagnostic or queue-control path could reach review without CI signal.

Resolution: CI now installs ShellCheck and checks every executable shell file with its declared shell dialect; the reproduction commands are documented in `CONTRIBUTING.md`.

## Findings retained as bounded follow-ups

### Medium: user-config installation is not transactional

Evidence: `scripts/install-user-config.sh` backs up known Wilsof-owned paths before copying files, then invokes `dms setup` and enables user units. It validates the generated entrypoint, but a failure after one or more copies can leave a partial configuration. Backups are available under `~/.local/state/wilsof-os/backups`, but rollback is manual.

Implication: an interrupted deployment can require recovery from backups.

Follow-up: design a staged install with a manifest and explicit restore command; test interruption at each activation boundary. Do not implement it without a real target-VM test because DMS owns part of the generated state.

### Medium: physical session behavior remains unverified here

Evidence: `README.md` and `docs/github-workflow.md` already distinguish static checks from physical keyboard routing, PAM unlock, idle lock and graphical persistence.

Implication: CI cannot establish real desktop behavior.

Follow-up: use the approved VM console/client to verify those paths and attach dated visual/human evidence; do not claim this audit validates them.

### Low: historical Fedora bootstrap remains in the tree

Evidence: `scripts/bootstrap-desktop.sh` is guarded to Fedora 44, while the active prototype direction is Arch.

Implication: two platform paths increase maintenance and dependency review surface.

Follow-up: owner should decide whether to retain it as documented history or move it to an archived area after checking any active consumers.
