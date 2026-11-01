# Integration2 — Independent Review 1/5: Installer Safety

Verdict: **NEEDS REMEDIATION**. Read-only source review; no installer fixes applied.
Reviewed branch: `feat/integration-20261101` at `0abf4a51af2338f14c691c2d325d6abfa2c8a410`.
The Integration2 ISO's recorded source is `b755bfabf82ece67eea3d666ea94330ff95f738e`; this review targets current source, not a fresh ISO audit.
Review date: 2026-11-01 UTC. Evidence window: 23:46–23:48 UTC, with later report publication.

## 1. Completed scope

Inspected `bin/wilsof-install`, `installer/wilsof_installer.py`, `runtime/provision-target`, `runtime/pinned-package.py`, `runtime/desktop.py`, plan validation, and installer/provisioning tests. The old `scripts/install-arch-test-vm.sh` was read for context; it is a separate VM-specific prototype, not the current ISO entrypoint (`docs/installer-runtime.md`, Parent-owned ISO handoff).

No code changes, dependencies, ISO builds, QEMU, real disk probes/writes, chroots, mounts, Proxmox operations, scheduler activation, merges or releases. Only this new report is delivered on an isolated review branch. Existing artifacts were not used as mutable fixtures. Test files and harmless reproduction fixtures were created only in fresh scratch directories.

## 2. Verified findings

No Critical or High defect was demonstrated within this bounded review.

### IS-01 — Medium: system-account names pass preflight, but cannot satisfy target provisioning

Locations at the reviewed commit:
- `installer/wilsof_installer.py:90–92`: only `root`, `greetd`, and `nobody` are reserved; names such as `greeter` and `daemon` pass.
- `installer/wilsof_installer.py:246–259`: that validation is the account preflight before confirmation.
- `installer/wilsof_installer.py:209–224,230–231`: formatting and base/package installation precede account creation and provisioning.
- `runtime/provision-target:35–38`: the selected account must have UID >=1000 and home `/home/USERNAME`.
- `runtime/provision-target:82`: `greeter` is also the target greeter service identity, not a dedicated desktop administrator name.

Reproduction executed using the real validators and a harmless temporary Arch-like target: change `signed_plan()` from `tests/test_installer_runtime.py:18–34` to username `greeter`, recompute `review_digest`, and call `validate_plan`. Result: **ACCEPTED**. Create target `usr/lib/os-release` containing `ID=arch`, and `etc/passwd` containing the synthetic service-account row `greeter:x:969:969:Greeter:/var/lib/greetd:/usr/bin/nologin`. Calling real `validate_target(target, 'greeter', False)` returns **ValueError: Expected a non-root target account with a dedicated home**.

This verifies inconsistent acceptance across the two boundaries, not a real package installation. On an initialized target with that service identity, preserving/reusing the account fails the downstream requirement; rejecting the duplicate during account creation also happens after formatting. No successful login, backend account mutation, or actual data loss is claimed. The installer deliberately only accepts entirely blank disks, so the demonstrated consequence is avoidable failed/partial installation, not overwriting existing nonblank user disks.

Recommended fix: reject names reserved by the effective base/desktop package set before confirmation/formatting (including `greeter` and base system accounts). Add an explicit backend account-existence/UID/home check before setting a password or granting administrator membership, plus regression tests for reserved-name selection and existing service users. Do not silently repurpose a service account.

### IS-02 — Low, conditional: mount guard compares lexical aliases instead of canonical targets

Location: `installer/wilsof_installer.py:149–156`; the caller retains the supplied path at `:174` and rechecks it at `:185,208`.

Reproduction executed: create an empty real directory `REAL/target` and ancestor symlink `ALIAS -> REAL`; supply `ALIAS/target` to `check_target_mount`. Mock only `read_json` to return the real-shaped findmnt result `{'filesystems': [{'target': 'REAL/target'}]}`. Result: **ACCEPTED**, even though the canonical target is listed as mounted. `path.is_symlink()` checks only the leaf; lexical `Path` equality misses the ancestor alias.

This is a verified guard bypass under a fixture mount table, not an actual mount or host write. The shipped CLI fixes the destination to `/mnt/wilsof` and exposes no target option. Exploitation therefore requires a changed/aliased ancestor or another caller, not ordinary target-disk input; this is not rated High. A nonempty destination is still rejected.

Recommended fix: reject symlinks in all target ancestors or require an absolute canonical path and compare canonical mount targets. Keep the final pre-format recheck. Add a test for an empty mounted destination reached through an ancestor symlink; existing leaf-symlink tests do not cover it.

## 3. Existing safeguards and test evidence

- Disk selection has no default, requires a unique explicit canonical whole-disk path, writable disk >=16 GiB, stable serial/WWN, no child devices, partition table, filesystem, mount aliases or holders (`installer/wilsof_installer.py:332–362,51–62`).
- Both probes require no wipefs signatures and a full zero-byte scan with `O_RDONLY|O_NOFOLLOW`, block-device verification, short-read rejection and before/after inventory checks (`:28–62`). This intentionally refuses merely repartitioned/nonblank disks.
- Packages and nonsecret plan are shown before exact `ERASE /dev/NAME` confirmation; hidden matching passwords and a fresh final target probe precede formatting (`:242–278`). `--validate` does not execute a saved plan (`:294–312`).
- Root/TTY, live Archiso, x86-64/64-bit UEFI and known-enabled Secure Boot gates; exact archinstall 4.5 pin, visible Btrfs and third-party plugin rejection (`:107–146,285–312`).
- The backend must identify the reviewed empty disk/size and propose exactly FAT32 `/boot` plus ext4 `/` before filesystem operations (`:188–209`).
- Locale, password setter, initramfs, provisioning exit, post-install flags and fallback EFI file are checked (`:216–239`). Exceptions return failure without automatic retry/reboot (`:314–324`). Mounts are intentionally left for inspection; this is documented, not an invented rollback guarantee.
- Provisioning refuses `/` outside live mode, checks Arch/account identity and symlink write paths, requires a mounted installed root, runs desktop setup as the target user, and validates resolver postconditions (`runtime/provision-target:12–38,49–103`). Pinned-package checksums and destination symlink guards add protection (`runtime/pinned-package.py:36–59`). Desktop managed-file writes preserve personal settings and create backups (`runtime/desktop.py`, `install_user`).

Executed in the isolated review worktree, with `PYTHONDONTWRITEBYTECODE=1`:

    python3 -m pytest -q -p no:cacheprovider \
      --basetemp=FRESH_SCRATCH_DIRECTORY \
      tests/test_installer_runtime.py tests/test_installation_plan_validation.py \
      tests/test_installer_architecture.py tests/test_desktop_runtime.py \
      tests/test_chroot_contract.py tests/test_arch_installer.py

Actual result: **120 passed in 0.92s**, exit 0. These tests use fixtures/mocks for privileged operations; this is not partitioner or hardware certification. Existing guard-order, stale-inventory, leaf-symlink, firmware, password/initramfs/provisioning/postcheck failure tests passed. No new regression tests were committed because this is a report-only review.

## 4. Commits and CI

Source HEAD and remote Integration2 branch agreed at review start. Exact source-head GitHub check-runs query returned `total_count: 0`; **no reported CI checks**, not CI success. Only the report is to be committed/pushed; Integration2 must stay at its original SHA. Final publication identity/read-back is recorded in the terminal receipt rather than a self-referential report commit.

## 5. ISO/artifacts

No ISO built, mounted, modified, or newly certified. Historical Integration2 artifact metadata is in `../checkpoints/integration2-final-closeout-20261101.md`; no historical hash-preservation check was rerun or inherited as current review evidence.

## 6. Installation results and potential risks requiring further testing

- **Concurrent storage changes:** the full scan closes its read descriptor before the backend writes (`installer/wilsof_installer.py:39–62,206–209`). No exclusive device reservation is demonstrated. Hotplug/concurrent writes are already explicitly excluded by `docs/installer-runtime.md`, Safety boundary. Test in a separately authorized disposable environment; no race-caused data loss was reproduced here.
- **Real backend cleanup/faults:** mock tests verify propagation/order, not archinstall's real partially completed formatting/mounting, package/network failure, bootloader failure or signal teardown. Native chroot tests are opt-in (`tests/test_arch_chroot_integration.py:1,34–55`) and were not run. Verify retained mount ownership and actionable recovery before retry; do not add blind recursive unmounting or cleanup.
- **Partition/boot side effects:** a real layout/partition geometry, bootloader firmware-variable behavior, disk-only boot and unrelated-disk preservation were not exercised. The adapter delegates these operations; a successful mock is insufficient evidence of target-only runtime effects.
- **Account backend behavior:** IS-01 establishes the validator mismatch; actual archinstall duplicate-user/password/group handling and package account allocation still require a disposable integration test. No service-account privilege escalation is claimed.
- **Password carriage returns:** a separate mock reproduction showed `abc\rdef` reaches the backend, although the prompt says single-line and rejects LF/NUL (`installer/wilsof_installer.py:260–263`). No hashing/authentication failure was demonstrated, so this is not counted as a defect; test supported input semantics before changing policy.

No physical client/USB/GPU/storage/firmware acceptance is asserted. Those tests need separate authorization. Existing virtual acceptance in the closeout report is historical evidence, not rerun by this review.

## 7. Boot and password login

Not performed. Real password handling, normal greeter authentication and persistence are not certified by validator or mocked executor tests.

## 8. Remaining limitations and verdict

**NEEDS REMEDIATION:** resolve IS-01 before considering installer review passed; harden/test IS-02 as a bounded guard defect. Neither finding proves current default-path loss of existing disk data. Real cleanup/firmware/concurrency boundaries remain explicitly unverified. No fixes or issue closures accompany this report.

## 9. Workflow and reporting compliance

Followed `CONTRIBUTING.md` isolated-worktree/read-only review boundaries and `docs/development-reporting.md` report-only branch publication. This report retains all twelve reporting categories while putting the requested findings, risks, safeguards, recommendations and verdict first. No PR creation, merge, source-branch change or automation activation is needed for delivery.

## 10. Model/API cost

One active review agent; no delegated reviewer or paid auxiliary review requested. Session model: gpt-6.1-sol/openai-codex. Actual billed cost/token totals unavailable; no zero-cost claim. Review uses no more than twelve agent tool rounds, including report publication/verification.

## 11. Processes, locks and storage

Only synchronous read-only inspection, fixture tests/reproductions and report publication were started. No worker, scheduler, VM, builder, mount process or privileged installer was started. Existing automation controls were not changed; historical paused state was not independently re-certified. No project lock was acquired or released for destructive work because none was performed. Available scratch-filesystem storage at **2026-11-01T23:48:30Z: 65,171,869,696 bytes** (`df -B1 --output=avail`). No artifacts deleted.

## 12. Next recommended action

Separately authorize a focused IS-01 account-preflight fix and regression test; keep the review result open until corrected and verified. This is a recommendation, not execution approval. **Stop after Review 1; do not start Review 2.**
