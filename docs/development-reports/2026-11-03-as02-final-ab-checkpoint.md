# AS-02 final native A/B checkpoint — 2026-11-03

## 1. Exact harness correction
Service readiness now requires exact `ActiveState=active`, `SubState=running`, `Result=success`, and a nonzero MainPID. Eight focused controls passed, explicitly rejecting inactive, activating, failed and deactivating, plus bad substate/result/PID. Foreground tty1 console text and a nonblack QMP framebuffer were required for actual Username/Password prompts; the password frame was also visually inspected. An initially black frame was correctly rejected without input. No credentials were sent solely because a process existed.

## 2. Fresh baseline result
Exactly **one** new disposable baseline guest booted. Installed stack was read back: Hyprland 0.57.0-1, Hyprlock 0.9.6-3, Hypridle 0.1.8-2.1, Quickshell 0.3.2-1, dux-shell 2.0.0-1. Baseline Hyprland ELF SHA256 `1004b8b34c79a473c781b440c4befccc4f427a9b1c833bbd19063156f2644f90`.

The real greeter displayed Username: wilsqa and an empty Password prompt. Synthetic-fixture PAM login succeeded: fresh greetd PAM session-open evidence and an active UID-1000 Wayland user session were recorded. However, DMS owning-state/Command Center IPC readiness was **not established**. One probe returned activating/start and no Quickshell instance; a later probe exceeded 30 seconds. The timeout escaped the overall polling loop and the driver shut down the guest prematurely. Recovered journals show DMS backend/UI startup activity, but backend-ready logs are not accepted as Command Center readiness. This is a **harness orchestration failure**, not proof that DMS is defective or that compositor isolation failed. No second baseline was started.

## 3. Patched candidate result
**NOT STARTED.** The candidate supervisor refused to proceed because the fresh baseline gate had not passed. The existing package remained private and unchanged; no package or ISO rebuild occurred. Historical AS-02 leakage is not substituted for this attempt's missing native baseline reproduction.

## 4. Native security acceptance
**PENDING / BLOCKED; NO-GO for integration.** A/B/C isolation scenarios did not execute in either guest. Hyprlock acquisition, ordinary-client isolation, IPC-triggered Command Center, independent focus-grab client, wrong/correct lock password, post-unlock routing, immediate relock, DMS restart/IPC disconnect and repeated lock cycles remain NOT RUN. No compositor fix or production security acceptance is claimed. The only password entry was the synthetic fixture at the verified unlocked greeter.

## 5. Package and source provenance
Reused `hyprland-as02-private 0.57.0-1.1`, 53701518 bytes. Package SHA256 `b81531b9cf70b9f372238539cd64ae7d2ad66b41f1fc429dec6e998c41873a1f`; ELF SHA256 `8a4a88e1cfebe165f37b50a9a83cacb2632adce6a3bd66fef44b2365b0c0e096`; Build ID `3e028756ffffaae966ced21992c5bdf2e995d4d5`. Source `0aa6745f705f2c4b0a5004eb019ef76e5bbdb426`; unchanged private AS-02 patch SHA256 `f75de0300bebde61151f83171e7ca1ed2a32b1f1296b1273536f8e41a68dfadf`. Prior full native build and packaged-binary inspection passed; neither was repeated. No host package replacement or weakening of authentication/package-signature policy. This is a private unsigned local candidate, not an official upstream package.

## 6. Review status
**Independent review PENDING.** A bounded self-review checked the exact native source hashes, central focus/grab admission, keyboard enter/key/modifier endpoint guards, rebinding and lock lifecycle changes, and alternate routing context. Source seam controls are not native acceptance. Alternative protocol, pointer/touch and lifecycle-race coverage is not certified. No new paid reviewer/agent was engaged. The private upstream draft was updated but NOT submitted.

## 7. Remaining blocker and focused correction
The DMS IPC probe itself lacked a subprocess bound, and its per-probe exception aborted readiness before the total deadline. The harness now bounds the IPC command and retries per-probe timeouts within the monotonic overall deadline. Three focused tests on the actual extracted polling block passed: timeout-then-ready recovery, persistent-timeout refusal, and rejection of a missing IPC target. These use synthetic collaborators and are **not QEMU tests**. Native retest of that correction is NOT RUN. Reuse the existing package in any separately authorized continuation; do not rebuild it or restart architecture analysis.

## 8. Artifact and physical scope
No ISO build, physical installation, Proxmox change, main merge, public release or modification of original QA disks. Preserved Integration2 ISO `wilsof-internal-2026.11.01-integration2-x86_64.iso`, 2,549,536,768 bytes, SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`. ISO, original backing disk/overlay and firmware were hash-verified unchanged before/after. Physical keyboard/GPU/client tests remain unperformed.

## 9. Shutdown, evidence and resources
Normal QGA guest-shutdown completed; exact QEMU identity and session-owned driver/supervisor exits were verified. Disposable overlay non-repairing offline qcow2 check returned **0**. Journals were recovered from a separate sparse raw copy through an owned read-only loop and ro,noload,nosuid,nodev,noexec mount; mount and loop were detached. No additional guest boot occurred for recovery. Original artifacts and the existing candidate package remained unchanged. Free bytes at 2026-11-03T10:09:08.721153+00:00: 45896441856 (42.744 GiB). Project lock release is verified in the private checkpoint after publication. Worker remains paused; Wilsof scheduler remains disabled/paused.

## 10. Git and reporting
Only this sanitized report is added on `fix/as02-native-20261103`; earlier reports are preserved. Exact remote head/report blob and the #16 status comment are read back. Other remote heads and existing PR branches remain unchanged; no integration into Integration3. Sensitive patch/package, console/raw journal evidence and synthetic fixture remain private. CI is queried separately; no green-CI claim.

## 11. Checkpoint and cost
Durable private checkpoint: owner state `wilsof-qa/as02-native-20261103/checkpoint.json`; current evidence directory `ab3/`. It contains exact-state controls, prompt proofs, PAM/session evidence, original failure, recovered journals, bounded self-review, process/lock identities and preservation hashes. One main agent on the supplied gpt-6.1-sol/openai-codex route; no additional paid agents or scheduler activation. Actual billing is unavailable, not asserted to be zero.

## 12. Stop decision
**Stop: baseline could not be established reliably through DMS readiness, as required by the one-baseline-guest constraint. Native security acceptance PENDING; integration NO-GO.** No second baseline, patched guest, package rebuild or next task starts automatically. The remaining gate is a separately authorized native validation of corrected per-probe DMS readiness, then a fresh baseline and the existing candidate's A/B/C and lifecycle acceptance, followed by independent review.
