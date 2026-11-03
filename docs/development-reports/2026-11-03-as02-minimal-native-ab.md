# AS-02 minimal native A/B acceptance — 2026-11-03

## 1. Result and exact scope
**PASS — requested minimal native A/B comparison.** Fresh original Hyprland 0.57.0-1 reproduced keyboard leakage to an ordinary client during native session lock. The preserved private patched package prevented that delivery and passed the required password/unlock/recovery/relock checks. **Production/Integration3 integration remains NO-GO pending independent security review and separately scoped integration acceptance.** No package rebuild, ISO build, merge or release.

## 2. Harness and readiness
Read the current checkpoint/reports, verified package/patch hashes, absence of conflicting protected processes and existing lock availability, then acquired the established project lock. Exact greetd properties, foreground native console prompt text/nonblack QMP frames, genuine synthetic-fixture PAM login and an active Wayland user session were required. Existing inactive/activating/failed/deactivating controls and bounded-timeout handling were checked. **DMS IPC was not a prerequisite.** User commands used the actual compositor instance/socket and user bus, with process-level timeouts. Same historical minimal client, same manual Hyprlock configuration and same input procedure were used in both guests.

## 3. Fresh original baseline
Original package `hyprland 0.57.0-1`; native ELF SHA256 `1004b8b34c79a473c781b440c4befccc4f427a9b1c833bbd19063156f2644f90`. Ordinary input while unlocked passed. Hyprlock logged its secured event and independent native second-lock requests were denied before/after the input test. Inactive ordinary-client state stayed unchanged. After ordinary-client focus-grab activation, native trace recorded **1 keyboard.enter and 16 key events** during the owned lock; the client counter increased and its query changed. **Original isolation FAIL, as expected; baseline reproduction PASS.** No password was entered after the vulnerable baseline locked.

## 4. Preserved candidate and provenance
Reused `hyprland-as02-private 0.57.0-1.1`, 53701518 bytes, package SHA256 `b81531b9cf70b9f372238539cd64ae7d2ad66b41f1fc429dec6e998c41873a1f`. Source `0aa6745f705f2c4b0a5004eb019ef76e5bbdb426`; unchanged private patch SHA256 `f75de0300bebde61151f83171e7ca1ed2a32b1f1296b1273536f8e41a68dfadf`. Candidate guest package ownership, transferred-package checksum and running compositor identity were checked; packaged ELF SHA256 `8a4a88e1cfebe165f37b50a9a83cacb2632adce6a3bd66fef44b2365b0c0e096`, Build ID `3e028756ffffaae966ced21992c5bdf2e995d4d5`. Matching dependency ABI/version output was retained. Existing package-signature configuration was hash-verified unchanged. This is an explicitly private unsigned local candidate, not an official upstream package. Prior native build/inspection provenance is preserved; no build was repeated.

## 5. Candidate native evidence
Hyprlock acquired the native session lock. The ordinary client's text and key counter remained unchanged after its native grab request and harmless sentinel input. Both the initial lock and immediate-relock intervals contained a new native grab commit but **0 ordinary keyboard.enter and 0 key events**. This is owning-state/protocol evidence, not a conclusion from a visible lock screen alone. Native second-lock denial corroborated ownership, including after the rejected password and relock.

| Minimal case | Original baseline | Private candidate |
| --- | --- | --- |
| Ordinary input while unlocked | PASS | PASS |
| Native Hyprlock session-lock acquisition | PASS | PASS |
| Inactive ordinary client gets no new input | PASS | PASS |
| Active ordinary focus-grab isolation | **FAIL — leak reproduced** | **PASS** |
| Legitimate lock-surface input | NOT RUN as auth control | PASS — PAM handled typed test password |
| Wrong password rejected, lock retained | NOT RUN after leak | PASS |
| Correct password authenticates and unlocks | NOT RUN after leak | PASS |
| Ordinary input returns after unlock | NOT RUN after leak | PASS |
| Immediate relock isolates a new grab request | NOT RUN after leak | PASS |

## 6. Authentication and lab controls
Only a private synthetic QA fixture was used, never a real password. Candidate authentication was attempted only after input isolation was demonstrated. Journal evidence contains a wrong-password PAM failure followed later by exact `auth: authenticated for hyprlock`, normal unlock/locker exit, ordinary input recovery and a genuine new lock lifecycle. No forceunlock, locker-kill unlock, PAM change or authentication bypass. DMS and automatic Hypridle services were temporarily stopped as common disposable lab controls in both guests; this is not a product change or acceptance of automatic-idle policy. Hyprland native lock and Hyprlock configuration were unchanged apart from diagnostic logging.

## 7. Evidence-oracle correction and limitations
The original baseline script's exact sentinel-suffix assertion failed because TCG generated repeated characters. Its original result/assertion/log are preserved. New native keyboard delivery, retained lock ownership and owning client counter/query changes independently proved the leak; the baseline was not rerun merely to obtain exact spelling. The candidate-only continuation used the same procedure with a delivery-based positive-input control. Its strict **zero locked input** criterion was not relaxed. Correct/wrong authentication and relock were verified on the candidate's real compositor, not a model or stub. Slow software-rendered lock frames were observed; no performance or physical-input acceptance is inferred.

## 8. Optional integration and review
DMS Command Center IPC integration: **NOT RUN, optional**; no DMS probe could invalidate the completed native test. Independent review: **PENDING**. Bounded self-review matched exact built source hashes, centralized keyboard-focus/grab admission, keyboard enter/key/modifier endpoints/rebinding and lock transition/lifetime checks against fresh evidence. It is not independent review or certification of alternative IME/capture protocols, pointer/touch, hotplug, suspend/resume, locker crash or all ordinary applications. Patch, package, raw logs and detailed reproduction remain private; upstream draft updated but NOT sent.

## 9. Shutdown and artifact integrity
Exactly one fresh baseline and one separate candidate guest were used sequentially. Both received normal QGA shutdown; exact process identities exited. Both disposable overlays passed non-repairing offline qcow2 checks with exit **0**. Protected original ISO/backing disk/overlay/firmware SHA256 values were verified unchanged before/after. Preserved ISO: `wilsof-internal-2026.11.01-integration2-x86_64.iso`, 2,549,536,768 bytes, SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`. No original QA disk modification or historical artifact overwrite. No physical client/GPU/keyboard or installation test.

## 10. Git, report and process controls
Only this sanitized report is added on isolated branch `fix/as02-native-20261103`; earlier reports/evidence and other PR branches are preserved. Exact remote report blob/head and the permanent #16 status comment are read back. No main merge, force-push, package publication or integration into Integration3. The owned project lock is released through its legitimate holder only after protected processes exit and publication is verified; final availability is independently probed in the private checkpoint. Worker remains paused; Wilsof scheduler remains disabled/paused. CI is checked separately; no CI-green claim.

## 11. Durable checkpoint, resources and cost
Private checkpoint: owner state `wilsof-qa/as02-native-20261103/checkpoint.json`; this run's evidence: `minimal4/native-comparison.json`, `native-evidence-verification.json`, per-guest journals/state, source-oracle correction and preservation/exit checks. Free bytes at 2026-11-03T10:33:28.171238+00:00: 45637349376 (42.503 GiB). One main agent on supplied gpt-6.1-sol/openai-codex route; no new paid agents, independent reviewer dispatch or worker/scheduler activation. Actual billing remains unavailable, not asserted to be zero.

## 12. Decision and next bounded gate
**Minimal native acceptance PASS. Independent review PENDING; production integration NO-GO.** Preserve and reuse this exact package without rebuilding. The next safe gate is independent security review and, if separately requested, the optional Command Center/DMS integration test. No next VM, task, build, merge or disclosure is started automatically.
