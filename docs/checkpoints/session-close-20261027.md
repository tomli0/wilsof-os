# Controlled session close — 2026-10-27

This is a recovery checkpoint, not authorization to continue development.
No new agent, VM, ISO build or installation test was started during close-out.
README and PRs #32/#33 were not edited, merged or overridden.

## Completed

- Existing Hypridle patch applies exactly to upstream v0.1.8 commit
  `e5c01af0842bd66617f7004568df9406111d6e80`.
- A full native Arch verification package was built in a separate isolated
  root, exit0: `hypridle-0.1.8-2.1-x86_64.pkg.tar.zst`.
- Packaged executable version/help, ELF and library resolution passed.
  Package SHA-256: `3182ffaa24b0382c39614c460e15f90ff730d7da4f60378123d9b3df09c01d04`.
- Verified recipe, patch, upstream license and provenance are retained under
  `packaging/hypridle/`; the binary and complete logs remain private/internal.
- Original candidate2 and diagnostic QEMU guests are stopped. Diagnostic
  offline check returned0; disk/overlay/firmware and earlier evidence remain
  preserved. Scheduler and automatic worker remain paused.

## Incomplete — not a runtime acceptance claim

- The copied/adapted portable regression entry point has NOT been run. It is
  explicitly marked WIP. Earlier extracted-loop RED/GREEN/UBSan logs remain
  historical evidence, not a pass for this adapted copy.
- New package has not passed a real compositor/session-teardown regression.
  Issue #31 remains open. No package deployment or ISO integration occurred.
- Current ISO remains `2026.10.26-stabilize2`, image source
  `e2561399e5ac5add3711549f9c48e1bcab1486d1`; its SHA-256 is
  `6c909c5f9e78c0326e999fc3977f66164157df19d320a86c6f136ae3f72aeebd`.
  It lacks the newer migration/rendering/package fixes and is not final
  acceptance for physical installation.

## Exact later resumption

Read the newest private close-out checkpoint and acquire the existing lock.
Only if explicitly resumed: finish the remaining focused harness and one
real teardown check using the already-built package; do not repeat the full
build without changed inputs. Decide #31 acceptance before ISO integration.
Do not start that work as part of this close-out. No merge/public release,
physical disk/USB or Proxmox changes; subscription-only Codex, no paid fallback.
