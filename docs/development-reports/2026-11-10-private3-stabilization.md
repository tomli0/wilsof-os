# Wilsof OS — Private3 stabilization, 10 November 2026

Status: **CONTROLLED STOP — SOURCE STABILIZATION VERIFIED; FINAL VIRTUAL ACCEPTANCE BLOCKED.**
Development: 9 November 2026 22:32 UTC through 10 November 2026 close-out.
Implementation checkpoint: `91606297fc8a1a7a61c6271f734872bc47920271`, branch
`integration/private3-20261107`. Existing issues #16/#60 and draft PR #61 remain open.
This report is not a release, new ISO acceptance, physical acceptance or permission
for Omarchy replacement. Documentation delivery may have a later commit than the
frozen implementation/archive identified here.

## Evidence boundaries

- Original exact-image report: [9 November acceptance](2026-11-09-private3-exact-image-acceptance.md).
  Its 18 basic PASS results remain historical; the image still contains the crash.
- New native evidence: separate disposable/COW guests, disclosed source/service
  overlays, real package build, actual PTY installer and normal prompt/PAM login.
- New source evidence: complete local suite and exact implementation-head CI,
  scoped static validation and a separate bounded AI source assessment.
- Private group: `wilsof-stabilization-20261109T2232Z`. Raw cores, journals,
  credentials, VM disks and private infrastructure locators are not published.
- No owner files, physical disk, Omarchy, Proxmox configuration, main merge or
  public release was modified. No additional privileged ISO build was executed.

## 1. Completed milestones

**Portal:** original xdg-desktop-portal-hyprland 1.4.1-2 / Wayland 1.26.0-1
SIGSEGV reproduced at ordinary logout. Symbolized core identifies an output proxy
being destroyed after display disconnection in normal exit handlers. Narrow
upstream backport `0121b2e3f85c7ebf6280173f1054f7e5606262d1` applies to v1.4.1.
Five ordinary login/logout cycles pass with the development ELF and another five
with the packaged ELF, with real Screenshot backend work and no new portal core.
Native lock/authentication controls pass. See [portal evidence](../portal-teardown.md).
No success-exit override, disabled portal or coredump suppression was used.

**Installer:** explicit `--replace-existing`, exact target/plan-digest destructive
confirmation, full inventory review, live-media/active-device refusal, immediate
revalidation, real FD-bound libblkid erasure and explicit kernel partition reread.
Strict blank mode is retained. A real synthetic EFI/Btrfs replacement passes,
followed by disk-only boot and ordinary password login. Later backend operations
remain pathname-based; the whole install is not atomic or FD-confined.

**Recovery:** one controlled missing-EFI-loader fault in a NEW COW image, observed
firmware failure, live-media repair through installed bootctl, disk-only boot,
normal password login and unchanged data/settings all PASS. Original backing
image/firmware and read-only sentinels remain unchanged. See [recovery scope](../recovery.md).

**Candidate preparation:** trusted-signature-required portal input is wired into
both live and fresh-target consumers; supplemental Dux/shared-component notices
stage through both source paths. A clean exact-commit regular-file source archive
was created and verified. These are not native trust, image or legal clearance.

## 2. QA findings and independent-assessment boundary

No Claude or additional paid-model review was started. Two bounded separate AI
contexts used the inherited route before the overnight no-new-workers guard.
The first review correctly rejected three destructive-boundary defects:

| Finding | Confirmed correction/evidence |
| --- | --- |
| wipefs canonicalizes/reopens `/proc/self/fd/N` | Replace CLI boundary with real libblkid FD API; actual pathname-substitution fixture PASS |
| Backend metadata checked too late | Exact archinstall 4.5 distribution metadata checked without importing its global Btrfs machinery before erasure |
| Missing explicit partition reread | Bound-FD BLKRRPART after child handles close; topology validation and EBUSY-only bounded retry |

Final scoped AI verdict: PASS, security and logic blocker arrays empty, exact diff
SHA256 `6d63c52b36fd5d7296cd09acc663e9ff2fe23a03fe3373cdacf6219f22d1a821`,
23-file manifest unchanged before commit. This is not professional independent
security approval. Real trusted/untrusted package-signature consumer tests remain
pending; no new model worker was started after the guard.

## 3. Source quality and security

- Local complete suite: **835 PASS / 3 explicit native opt-in SKIP**, exit 0.
- Python AST: 110 files; JSON: 20 files; schema validation: 1 schema; 72 image
  payload entries validated. Selected shell scripts/PKGBUILD pass ShellCheck;
  PKGBUILD's makepkg-context exclusions are recorded in private command receipts.
- Whitespace and tracked modes checked. Candidate file group/world write bits
  removed without changing execute bits. Scoped credential-pattern scan has no
  matches; this is not a comprehensive secrets or security audit.
- Actual FD/path substitution uses formatted disposable ext4 regular-file images,
  not just mocked command arguments. Selection, confirmation, identity, mounted
  targets, media/copy-to-RAM, mapping and failure/interruption fixtures pass.
- Generated installer logs were privately checked for the synthetic secret and
  encoded forms; no matches in the scanned scope. No signature/mitigation bypass.
- Dux notices/provenance repair inclusion at source level. Complete transitive
  licensing and proprietary Broadcom redistribution clearance remain unresolved.

## 4. Commits and exact-head CI

| Commit | Role | Verified result |
| --- | --- | --- |
| `922446ab7ff5fe2e8c13fb3b0f01d66d6a653921` | Portal backport/provenance/native regression | Built and native-tested; pushed |
| `91606297fc8a1a7a61c6271f734872bc47920271` | Guarded replacement, portal consumers, notices and active-branch CI trigger | Local suite PASS; exact-head Actions run 42728421041 SUCCESS |

[Implementation CI](https://github.com/tomli0/wilsof-os/actions/runs/42728421041)
checks out the exact 9160629 full SHA and reports **831 PASS / 7 SKIP**.
Do not substitute the local 835/3 count for that CI result: the environments differ
and the CI summary does not print every skip reason. Skips are not passes.
The later report-only delivery head's state is read back separately at close-out;
no old run is claimed as its exact-head result. PR remains draft, not merged.

## 5. ISO identity and new candidate status

| Field | Actual status |
| --- | --- |
| Retained ISO | `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso` |
| Bytes | 2813849600 |
| SHA256 | `111c06b70cf6d909b3e815975f69bfa18f299af9dcfe9bbbfd5e197992c53a59` |
| Frozen image source | `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261` |
| Custody | Original/copies remain private and unchanged; recovery live launch independently rechecks its hash |
| New ISO | **NOT BUILT**, no new filename/path/hash or accepted image |
| Prepared source archive | Source 9160629, 341 regular source files, 14428160 bytes; not an ISO |
| Source archive SHA256 | `f92507f1607bd92a501d588b938cc8f75e7af7ffe2e2f0c70ef44f0077cd0dcf` |

The retained portal package is unsigned. Its archive/ELF identities are pinned;
actual real-input preflight refuses the missing `.sig`. No valid-signature native
install occurred. A build command that silently enrolls a new trust root or reuses
the consumed old-image helper would be unsafe. The source archive is ready for
custody, **not BUILD READY**: obtain an owner-approved signing/trust path, native
consumer proof, fresh authenticated root-boundary reconciliation and separate
single-build authorization before providing/running the new rootful command.

## 6. Installation and all 18 basic image gates

| Gate | Retained Private3 | New candidate ISO |
| --- | --- | --- |
| 01 UEFI boot from emulated USB | PASS (historical) | NOT RUN |
| 02 Live Hyprland/Dux desktop | PASS (historical) | NOT RUN |
| 03 Correct cowspace | PASS (historical) | NOT RUN |
| 04 Install on new blank QCOW2 | PASS (historical) | NOT RUN |
| 05 Installer success | PASS (historical) | NOT RUN |
| 06 Disk-only boot | PASS (historical) | NOT RUN |
| 07 Normal greetd/PAM login | PASS (historical) | NOT RUN |
| 08 Installed branding/desktop | PASS (historical) | NOT RUN |
| 09 Menu before lock | PASS (historical) | NOT RUN |
| 10 Native Hyprlock | PASS (historical) | NOT RUN |
| 11 Wrong password rejected | PASS (historical) | NOT RUN |
| 12 Correct password unlock | PASS (historical) | NOT RUN |
| 13 Menu after unlock | PASS (historical) | NOT RUN |
| 14 Repeated lock/unlock | PASS (historical) | NOT RUN |
| 15 Terminal, Firefox, Files | PASS (historical) | NOT RUN |
| 16 Workspaces | PASS (historical) | NOT RUN |
| 17 Normal reboot | PASS (historical) | NOT RUN |
| 18 Clean shutdown | PASS (historical) | NOT RUN |

These historical rows do not erase the retained image's portal FAIL. New overlay
results cannot fill the new-ISO column.

| Additional gate | Result and boundary |
| --- | --- |
| Original ordinary portal logout | FAIL reproduced and preserved |
| Corrected portal: five source + five packaged cycles | PASS native extracted ELF; NOT new ISO or trusted installation |
| Full Btrfs/EFI replacement attempt 1 | FAIL: partition reread EBUSY; preserved |
| Controlled raw-reader EBUSY reproduction/release | PASS; only idempotent reread retries |
| Full Btrfs/EFI replacement attempt 2 | PASS, installer exit 0, 418.1198 seconds, five answered prompts |
| New GPT/ESP/ext4 root, disk-only UEFI, real password login | PASS in labelled source-overlay installation |
| Unselected disk | PASS unchanged hash; intentionally read-only sentinel |
| Replacement blank-GPT/full ext4 installation matrix | NOT RUN as full native installations; ext4 FD-eraser seam is separately tested |
| Wrong selection/confirmation/changed identity/mount/media/path/layout/interruption | PASS applicable source regressions; not a complete native/new-ISO matrix |
| Frozen update prechecks | PASS; explicitly no refresh/transaction/write |
| Future 2026-11-08 full-transaction planning | FAIL dependency preparation, safely refused; no installed DB/policy change |
| Actual signed future version progression/reboot/apps/migration | BLOCKED; no future packages installed |
| Controlled EFI repair, disk-only password boot, data/settings persistence | PASS manual recovery COW gate |
| Local package database consistency after EFI recovery | PASS, pacman -Dk exit 0 |
| Actual mid-package-transaction interruption and retry | NOT RUN |
| Automatic system rollback | BLOCKED / not implemented, not promised |
| New-image notices/private-key/module audit | NOT RUN; source checks do not replace it |

Storage observed 2026-11-10T00:46:05Z: private builder 26998591488 available bytes
(25.14 GiB); control/evidence filesystem 13469282304 available bytes. Builder has
4 CPUs, MemAvailable 7288716 KiB; archiso 92-1 / arch-install-scripts 32-1 queried.
These are read-only observations, not approval of full-build resource/namespace
limits. The observed SSH cgroup is not a future rootful build scope.

## 7. Boot and authentication

Both the real replacement and repaired COW boot without attached installation
media, mount `/dev/vda2` as ext4 and pass actual greeter password/PAM login.
Administrative QGA/runuser access is not used as authentication evidence.
No physical MacBook boot or unlock acceptance is inferred.

## 8. Remaining defects and limitations

- Missing trusted portal signature and real live/fresh-target signature acceptance.
- Private compositor requires `libaquamarine.so=14-64` and
  `libhyprgraphics.so=4-64`; proposed aquamarine 0.16.0-1 / hyprgraphics 0.6.0-1
  from 2026-11-08 break them. No dependency override, SONAME link or partial upgrade.
- No actual forward version progression or mid-transaction recovery proof.
- Separate nonzero Dux/GTK portal/Hypridle teardown results remain disclosed;
  portal-specific correction is not a clean-all-services teardown claim.
- Remaining replacement matrix and every gate on the exact new image are pending.
- Required notice/legal/redistribution assessment and exact-image audit pending.
- Broadcom wl presence/kernel ABI/policy were established on the retained image;
  new image checks and physical 14e4:43a0 binding/scan/WPA/reconnect are NOT RUN.
- All display/input/audio/Bluetooth/power/suspend MacBook rows remain NOT RUN.
  Owner-controlled independent backups and restore verification are NOT RUN.

## 9. Standards, documentation and delivery

Existing authorized branch/draft PR only. No report-only branch, main merge,
release, worker activation, physical writes or historical artifact deletion.
Owner checklist now distinguishes source replacement support from frozen ISO
limitations; recovery documentation describes only the method actually exercised.
Final issue/PR comments link this report and exact delivery commit after read-back.

## 10. Model/quota observations

Parent route: GPT-6.1 / openai-codex. Two bounded AI assessments predate the
no-new-workers guard; none were spawned afterwards. No quota/capacity exhaustion
was observed; remaining quota and billed cost are unknown. No budget endpoint,
paid fallback or rate-limit circumvention was used to continue work.

## 11. Processes, locks and preservation

All owned portal/replacement/recovery QEMU lifetimes are stopped. Four recovery
lifetimes exit 0; the expected firmware-only failed-boot lifetime uses owned QMP
quit, not an OS-shutdown acceptance claim. Offline COW checks pass, original
backing/firmware hashes and both sentinels match, and QA lock is probed available.
Nineteen replacement and twenty-three recovery evidence files were copied and
matched against remote digests; earlier portal/core custody receipts are retained.
The project holder is retained only for final synchronous publication; actual
release is checked and recorded in the final status comment/private handoff.
Existing paused automation is not reactivated. No new VM/build/review is dispatched.

## 12. Next recommended action

Complete one bounded, owner-approved portal signing/trust gate using the retained
exact package, without rebuilding it or weakening package signature policy. Prove
both native consumers and rejection controls; then prepare one source-pinned,
hash-locked, separately approved ISO-build action. Do not run the old-image helper.
Future coherent update delivery needs a compatible verified private-compositor
closure/rebuild as a separate workstream. No Omarchy replacement is authorized.

## Publication receipt

This report intentionally cannot embed its own commit hash. The final issue/PR
comment and private handoff record its actual delivery SHA, exact-head check
status, read-back result and released-lock receipt. Implementation identities and
source/native/ISO boundaries above remain fixed; later documentation does not
retroactively modify the retained image.
