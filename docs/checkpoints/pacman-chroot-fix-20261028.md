# Target chroot / Pacman regression — 2026-10-28

Related bug: #34. Draft integration PR #27 remains unmerged. This is one bounded source correction and isolated regression check, not a new ISO/install milestone.

## Observed failure and root cause

The actual `2026.10.28-internal1` image, source `98bda89c453365b9fc51a0b40ad4174c40b4af8a`, failed installation with exit1 during pinned Hypridle provisioning. The parent PTY driver exited0 after reporting the installer's failure; its exit is not installation success. Five prompts were answered and the transcript reported no plaintext password. The source bundle/desktop provisioning had not completed. The target retained 17GiB free; this was not actual space exhaustion.

Arch's installed filesystem package `2025.10.12-1` supplies `/etc/mtab -> ../proc/self/mounts`. Inspected package metadata and a disposable clone confirm the link is intact. With no proc mount in the target it is dangling *inside that chroot*, so Pacman's filesystem accounting fails and emits both the missing-mtab error and a misleading free-space message.

The Wilsof adapter mounts the target root/ESP, calls Archinstall4.5 operations, then invokes `provision-target` as a separate live-environment process. Inspected Archinstall source uses `arch-chroot -S` with per-command `MountAPIVFS=yes`; this setup does not persist into the parent process or Wilsof's later bare `chroot TARGET pacman`. `chroot` changes the root directory, not mount setup. The same bare-chroot assumption also affected the subsequent unprivileged desktop-provisioning command. proc, sys, dev and run are prerequisites, not only the mtab filename.

This is a Wilsof implementation regression introduced with the internal package integration, not evidence of broken QEMU firmware or a missing filesystem-package symlink. The old command reproduces the exact failure outside QEMU with the root already a mountpoint. No preserved failed disk was opened or repaired for this task.

## Minimal correction

`runtime/pinned-package.py` now provides one `target_command` boundary:

- External target: `arch-chroot -r TARGET COMMAND ...`, using the already-present Arch install scripts' API setup and teardown.
- Target `/`: run directly inside the already prepared live/build environment; do not nest mounts over its root.

Both native-package installation and `provision-target`'s existing `runuser` command use this boundary. `-r` avoids overwriting/bind-mounting the target resolver after it has deliberately been configured. The upstream offline wrapper mounts proc/sys/dev/run/tmp and cleans its mounts on exit, including a partial setup error.

No manual mtab replacement, duplicated custom production mount manager, CheckSpace/signature bypass or fallback to a broken bare chroot. Package/binary hashes, failure propagation, target/symlink guards, user validation, password handling, disk review/blankness/reprobe and firmware limits are unchanged. Installer storage code is not modified.

## Evidence and results

Private durable evidence: `/home/tommy_ai/.local/state/wilsof-qa/pacman-chroot-fix-20261028/`.

| Gate | Actual outcome |
| --- | --- |
| Old native helper / exact symptom | RED: intact mtab link, root mounted, target proc absent; same mtab/mountpoint/CheckSpace failure; package remains0.1.8-2 |
| Unit regression before source correction | RED: expected API-prepared command boundary absent |
| Focused package + desktop runtime tests | 16 passed |
| Full repository suite | 175 passed |
| Static checks | Existing CONTRIBUTING ShellCheck commands, Python AST parsing of modified Python/entrypoint, JSON validation and `git diff --check` passed |
| Actual fixed native transaction | GREEN: real offline Pacman upgrade0.1.8-2 to0.1.8-2.1, exit0; not a synthetic package response |
| Executable identity | SHA256 `3b5b36e21cb88e2939ed42f5d1a87c8b05f3c95876703545dd74dd280ee7fdd9`, matching existing verified artifact |
| Partial chroot setup failure | Injected sysfs mount failure propagates nonzero; package unchanged; earlier proc mount removed; no fallback/retry |
| API prerequisites / cleanup | mtab resolves to proc; proc/sys/dev/run/tmp present during command, absent as target mounts after completion; `/dev/null` works |
| User-provisioning execution boundary | Real unprivileged `runuser` context can access required APIs; not evidence of password authentication or a full desktop install |
| Existing-root `/` branch | Actual pinned helper invocation inside prepared root passes (package already current, honest no-op) |
| Resolver | Target link/file state preserved across success and setup failure |
| Independent review | Pending; no subagent or separate model review used |
| New ISO / full installation / installed boot | NOT RUN, explicitly outside this task |

The exact fixed helper SHA256 exercised in the lab is `8ee91bb649c06c022cef82cd9bd210fc6169472071d583ec5498b0695b100708`. Private `red.log`, `unit-red.log`, `green.log`, `full-tests.log` and lab source record the sequence.

The lab cloned the previously built immutable Arch root, not the failed QA disk. It used private mount/PID/network namespaces and no network transaction. A lab-only mount shim substitutes a minimal device tmpfs for upstream global devtmpfs, preventing exposure of host physical block nodes; all other upstream chroot setup and the actual pinned helper/Pacman binary execute normally. That device isolation is a disclosed test-environment difference, not a production wrapper change. The stock version was restored only in this disposable clone to make the real upgrade exercise CheckSpace. No Hypridle build, VM startup, full reinstall or ISO build occurred. No retained image/source marker was changed.

## Preserved artifact and next gate — STOP after this task

Existing internal1 ISO remains 2545111040 bytes, SHA256 `ab78770ce5c4c5fe8b7b913263ade47e4f2d8830a4ffbb6a38c935c9e9a45e83`, at `/home/tommy_ai/wilsof-assets/internal-test-20261028-internal1/`. Its bytes still contain the old implementation and its installation acceptance is FAILED. Earlier live-boot/app results remain valid only for those original gates; they do not make installation pass. Original partial disk, firmware and logs remain preserved, with prior controlled shutdown/offline-check evidence.

Next concrete milestone, only under separate authorization: review #34/#27 correction, freeze a new source revision, build one newly versioned internal ISO and perform an actual guarded installation to a new dedicated virtual disk, then disk-only boot and normal authentication before claiming installation fixed in an ISO. Do not silently repair/reuse the preserved partial disk as a blank target. #30 updater/preservation and installed locking gates remain pending for that future artifact. No such work starts here.

Scheduler/automatic worker remain paused. Included Codex only; no paid API/fallback, model configuration change, parallel subagent, physical disk/USB or Proxmox action. No merge, release or issue closure. Engineering Standards files and their separate branch are not changed by this fix.
