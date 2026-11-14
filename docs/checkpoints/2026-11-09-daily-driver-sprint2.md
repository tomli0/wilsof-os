# Daily-driver sprint 2 — native source-COW checkpoint, 9 November 2026

Status: **Private3 NOT ACCEPTED. No Private3 ISO has been built.**

## Exact source and evidence boundary

- Integration branch: `integration/private3-20261107`.
- Broadcom implementation: `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`.
- Final complete source suite on that implementation: **756 passed / 3 explicit
  opt-in skips**, 31.91 seconds. ShellCheck, changed-Python AST and diff checks pass.
- One independent read-only AI source review found no blockers in exact patch
  `e9d29e39ca231b7cd5d868fac102d04fb618c5c2b13e71229366c23db52c4925`.
  This is not independent human security or legal acceptance.
- New source-COW guest only; historical backing disks were never booted writable.
  The immutable installed image identity remains Private2 source `063b7f0`.
  The verified exported source and migrated user configuration identify `7c3771b`.
  This is **not** a newly built/installed Private3 image.
- Private evidence is retained under the sprint-2 evidence root. **56 transferred
  evidence files** were independently SHA256-compared. Scoped export scans found
  no raw/hex/base64 synthetic credential match; this is not forensic-erasure proof.

## A. Broadcom — implemented, source-tested, native package/load evidence

See [exact compatibility and license assessment](../broadcom-wl.md).

Frozen signed packages supply `linux` / `linux-headers` `7.2.11.arch1-1`, kernel
release `7.2.11-arch1-1`, `broadcom-wl-dkms 6.30.223.271-50`, `dkms 3.4.4-1`.
Native builds/installations succeeded twice. Actual module path, vermagic,
cfg80211 dependency, class-wide PCI alias, successful `modprobe wl` and residency
were checked. An unsupported-kernel/missing-header build refused with exit 21.

The generated policy was exercised with real mkinitcpio: wl, cfg80211 and the
same-basename modprobe override were present in initramfs. After normal reboot,
wl was resident without a manual load. Virtual Ethernet remained connected.
No Broadcom device was emulated: physical binding, scans, WPA and reconnect are
**PENDING**. Lockdown was none; signature enforcement was not enabled, and normal
out-of-tree/proprietary/untrusted-key taints were recorded, not suppressed.

Native standalone helper execution used prototype helper SHA256
`424511d8be84c41d12f6a046b66accf3e45b1e6b466de16c56e8efe890a03c7b`.
The final committed helper is
`9f1d4c4c520dd1f9c1c840bae86b4920213a2cb4ae18dea7f941749aa0d375f2`:
subsequent image-only key exclusion and representative modalias refinement have
source/fixture tests, **not final-helper/image runtime acceptance**. Do not erase
that distinction because the native module and generated policy checks passed.

## B. Update and configuration lifecycle — newly executed native evidence

The real deployed `bin/wilsof` bytes matched the exact `7c3771b` source bundle.

| Check | Actual result and limit |
| --- | --- |
| Version / offline preflight | PASS; immutable image SHA retained; reviewed snapshot remains 2026-11-01. |
| Ordinary-user interactive update | PASS; genuine sudo password/PAM, exact full `pacman -Syu`, exit 0; **no-op**, no versions changed. |
| Interrupted operation | PASS for Ctrl+C **at sudo prompt**, exit 130; package/config inventories unchanged. **Not** a mid-write interruption test. |
| Unknown package argument | Refused, exit 2; controller exposes no arbitrary package/source argument. |
| Altered repository source | Refused before transaction, exit 78; original policy restored byte-for-byte. |
| Existing Pacman lock | Refused, exit 78; exact test-owned lock inode preserved until explicit lab cleanup. |
| Permitted real package transaction | Normal Pacman trusted-signature reinstall of the exact already-installed official `patch` version succeeded. This is not a version upgrade. |
| Invalid signature | Same real package plus a damaged provided signature refused by Pacman, exit 1; installed package inventory unchanged, signature policy unmodified. |
| Legacy configuration migration | PASS; schema 1 / exact config-source SHA recorded after successful deployment. |
| Personal preferences | PASS; actual DMS preference bytes preserved. |
| Identical rerun | PASS; identical marker and no additional backup entries. |
| Manual per-file recovery | PASS; saved bytes restored and reviewed source explicitly reapplied. Not atomic rollback. |
| Future schema | Refused without overwriting the observed managed file. |
| Partial failed migration | Deliberately absent late source asset caused failure after earlier files changed; old version marker and personal settings retained. Explicit reviewed-source rerun repaired it. |
| Fresh authenticated login | PASS after update/configuration, using normal greetd username/password and exact PAM-session journal. |
| Normal reboot / new login | PASS; changed boot ID in same owned QEMU, same hashes for configuration preference/marker/CLI/module/initramfs, second normal password login. |

Seven configuration checks, six rejection/signature checks and two interactive
PTY cases are retained separately; no overlapping aggregate pass count is used.
The first rejection harness attempt stopped because Pacman returned a cache
`file://` URL. The corrected harness obtains repository/filename metadata and
uses the exact approved archived package URL; the original failure is preserved.

A no-op and identical-version reinstall do **not** establish changed-version OS
advancement. No rolling-mirror change, partial Arch upgrade, automatic config
migration after package update, atomic snapshot rollback or lock deletion was
introduced. Future snapshot/kernel progression, mid-transaction power-loss /
interruption recovery, config-migration concurrency and updated private-package
compatibility remain open daily-driver gates.

## C. Essential desktop lifecycle — new source-COW checks

- Active unchanged Hypridle policy acquired authoritative native lock after
  **181.445 seconds**, configured 180 seconds; no keyboard input during the
  measured interval, no idle stop or inhibitor. Rendered Terminal Idle surface
  and normal input field independently inspected; no emergency notice visible.
- Genuine password unlock restored the keyboard-invoked resident menu.
- Actual Super+L immediately acquired a second native lock. Its ordinary branded
  password surface was inspected before credential input.
- Wrong password produced the exact Hyprlock PID's PAM failure and retained the
  native lock; correct password released it.
- Actual Super+Space/query worked after both unlocks in the same shell PID with
  **NRestarts=0**. Super+Enter opened Terminal; workspace 2/1 preserved app PIDs.
- Normal user reboot returned to greeter, then new authenticated desktop/menu.
  The reboot RPC timed out during guest shutdown; changed boot ID and prior-boot
  shutdown journal independently reconciled success. No reboot retry was sent.
- Post-reboot DMS NRestarts=0, Hypridle/PipeWire/WirePlumber active; system/user
  failed-unit lists and current-boot systemd-coredump journal empty at capture.
  NetworkManager and Bluetooth service enablement persisted; no virtual Bluetooth
  adapter/audio-output test is implied by service state.
- Normal user poweroff; supervisor exit **0**, no forced-stop marker; offline
  qcow2 check **0 errors**, QA lock independently available. Four historical
  backing/firmware identities were independently hash-matched unchanged.

No all-client keyboard-isolation certification, suspend/wake, physical scaling
2.0, Bluetooth pairing, speaker/microphone or MacBook battery/wireless claim.
Guest display was virtual 1280×800 at scale 1. Historical app/menu evidence is
retained separately, not relabelled as a new-image pass.

## D. Candidate preparation — not an ISO build

Prepared source archive SHA256:
`5e40387c8c3d7b750b418701adb5007bf61bbcb5ca00b357cae17d1dbac68e41`.
Source epoch: `1794237834`. Proposed unique output:
`wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso`.
**Actual ISO size and SHA256 do not exist yet.**

Native dependency-only resolution on a fresh local DB selected **814 official
packages** from the frozen snapshot, including private-package dependency
constraints without public compositor fallback. Every projected identity is
pinned for later comparison with the real signed freeze. This resolution is
metadata evidence, **not full-closure signature verification or installation**.

Metadata sums: **1,705,441,788 compressed package bytes** and
**5,200,437,061 installed package bytes**; not actual ISO size or peak build usage.
The separate owner build entry retains signed closure verification, historical
input/artifact preservation, isolated rootful smoke, device denial and bounded
resource supervision. Read-only native tool/private-input/generated-entry and
storage checks passed; **24 private orchestration/negative tests passed**.
They do not replace actual rootful execution, final SquashFS inclusion/key audit
or exact-image boot/install acceptance. A second independent read-only AI review
found no blockers in prepared helper SHA256
`b99f7241fa0b292565348958ff56e5f7a92ab27f2a209b85b95f30d3efe1611e`;
this approves the prepared handoff scope, not privileged execution or an image.

At 15:54:21 UTC the project lock holder had exited 0 and its lock was independently
available. QA lock was also available; no owned guest remains. Worker stays paused,
queue disabled. Final publication receipts are recorded in the full report's
status-issue comments and the private handoff.

Builder sudo requires owner authentication; no privileged build was attempted,
no sudo bypass or additional privileged probe was used. All 18 mandatory gates
on a new Private3 ISO, plus Broadcom image inclusion/update gates, are **NOT RUN**.
Public proprietary-driver redistribution remains **NOT CLEARED**.

## Next safe action

After review of the pinned single-attempt owner handoff, authorize its one
interactive sudo phase on the existing builder. It must recheck exact resources,
root-only inputs and actual inherited isolation before any build, stop on drift,
and preserve every old artifact. Then independently audit the produced exact
ISO and run all 18 new-image gates plus Broadcom/update gates. Physical MacBook
Wi-Fi, Secure Boot, suspend/wake and daily-driver acceptance remain separate.
