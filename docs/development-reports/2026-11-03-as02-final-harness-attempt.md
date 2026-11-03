# AS-02 final automated harness attempt — 2026-11-03

**Functional DMS readiness PASS. Locked Command Center isolation NOT RUN. Unlock/relock NOT RUN. Native AS-02 integration PENDING / Integration3 NO-GO.** Exactly one guest boot; no harness rewrite/retry after failure.

## 1. Scope and completed gates

Read the [previous report](2026-11-03-as02-dms-readiness-unblock.md) and private checkpoint. One fresh disposable COW boot reached the real greeter, completed ordinary password/PAM login and started the exact privately patched Hyprland. Fresh identity and active Wayland-session evidence are retained. The corrected private harness ran byte-for-byte unchanged.

## 2. Pre-flight and offline controls

PASS: package and protected artifact hashes, absent conflicting QEMU/build processes, available resources and existing exclusive project lock. Re-ran eight functional-readiness controls, compiled four embedded Python payloads, shell-parsed fourteen literal commands, exercised the actual readiness function with `activating/start`, and checked native-event regex positive controls. The launcher used explicit supported background execution with completion notification, not a short foreground timeout. Cold-start and security phase budgets remain separate. Offline controls are not substituted for native tests.

## 3. Functional readiness result

**PASS:** after 103.385 seconds in the cold-DMS observation phase, attempt 7 returned valid owning Command Center JSON while DMS remained exactly **activating/start**. A live DMS process and plugin-loaded evidence were also present. This directly confirms the previous active/running-only admission was too restrictive. The unit is `Type=notify`, `NotifyAccess=main`; functional IPC and systemd notification completion are different observations. No renderer/notification root cause beyond that evidence is asserted.

## 4. Exact point of failure

The next native command was `dms ipc call commandCenter search control`: exit **0**, response **'search requested'**, stderr **''**. The immediately following `dms ipc call commandCenter status` returned exit **0**, stderr **''**, with owning `visible=false`, query `control`, count `0` and selected `-1`.

The harness then raised **AssertionError at run.py:174**, `assert a and a['visible']`. It did not perform a bounded observation of the later modal transition. The caught exception had an empty message and the driver exited 0; the private failure receipt therefore preserves the actual traceback, source point and command responses instead of mislabeling exit 0 as acceptance. This single immediate observation does not distinguish delayed mapping from a genuine modal-opening defect. No speculative fix or further automated boot followed, per the requested failure policy.

## 5. Unchanged package, source and historical ISO

`hyprland-as02-private 0.57.0-1.1`; package SHA256 `b81531b9cf70b9f372238539cd64ae7d2ad66b41f1fc429dec6e998c41873a1f`; source `0aa6745f705f2c4b0a5004eb019ef76e5bbdb426`; guest ELF SHA256 `8a4a88e1cfebe165f37b50a9a83cacb2632adce6a3bd66fef44b2365b0c0e096`. No compositor modification/install/rebuild. Historical ISO `wilsof-internal-2026.11.01-integration2-x86_64.iso`, 2,549,536,768 bytes, SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`, freshly verified unchanged. No new ISO or installation.

## 6. Native acceptance matrix

| Gate | This attempt |
| --- | --- |
| Real greeter and ordinary PAM login | PASS |
| Patched Hyprland startup/identity | PASS |
| DMS/plugin and functional Command Center IPC | PASS while activating/start |
| Normal Command Center opening/keyboard operation | NOT VERIFIED; immediate visibility assertion failed |
| Native Hyprlock acquisition | NOT RUN |
| Locked Command Center IPC/sentinel isolation | NOT RUN |
| Legitimate lock input and authenticated unlock | NOT RUN |
| Post-unlock Command Center recovery | NOT RUN |
| Immediate-relock isolation | NOT RUN |

## 7. Native focus and authentication evidence boundary

DMS-only Wayland tracing, compositor diagnostics and actual client state were retained privately. No native secured-lock interval occurred, so no fresh zero-event isolation claim is made. The only password input was the private synthetic greeter/PAM credential. No lock password, forced unlock or authentication bypass. Historical exact-package minimal A/B/input/authentication/relock PASS is preserved, not repeated or substituted for DMS acceptance.

## 8. Security classification and remaining gates

This is an **inconclusive harness/application-transition blocker**, not a demonstrated compositor security failure. Native AS-02 integration remains **PENDING**. Broader lifecycle cases, independent security review and physical-client tests remain incomplete. No deployment or controlled Integration3 recommendation is justified yet.

## 9. Git, publication and privacy

Only this sanitized report is added on new branch `docs/as02-final-harness-attempt-20261103`, based on `9e22a612aa56a262270f68e4abd7c1d278417858`. Existing PR branches are not changed. Remote heads/report blob and #16 comment are read back; exact-head CI is queried without a green claim. No merge, release or security disclosure. Private patch, raw keyboard/protocol logs, credentials and detailed reproduction stay private.

## 10. Iteration and cost limits

One main agent on supplied `gpt-6.1-sol`/`openai-codex`; maximum six agent iterations, one QEMU boot and no additional agents/reviewers or paid-service calls. No worker/scheduler activation. Actual billing is unavailable, not claimed to be zero.

## 11. Safe shutdown and preservation

Established identity-checked QGA shutdown **PASS**; receipt says `guest-shutdown`, exited=true. All QEMU/build processes independently absent. New disposable qcow2 offline check **exit 0**, no errors. **14 protected artifact hashes unchanged**. The legitimate driver released the existing project lock after guest exit; availability independently probed. Worker remains paused and scheduler disabled/paused. Private guest disk/firmware and diagnostics are preserved, not deleted. Available storage at 2026-11-03T11:37:41.993575+00:00: **45508009984 bytes (42.383 GiB)**.

Private checkpoint: logical `wilsof-qa/as02-native-20261103/checkpoint.json`; evidence: `final-harness-attempt/` including exact harness/pre-flight, readiness response, failure receipt, journal, process ownership, shutdown, disk check and before/after hashes.

## 12. Exact next method

Stop automated harness attempts. Recommend a simpler **direct-console** acceptance on an owner-authorized disposable guest: observe actual Command Center opening/owning state before advancing, then perform critical native lock/IPC/sentinel, authenticated recovery and immediate-relock checks with private protocol evidence. An owner-only procedure is saved privately and **NOT EXECUTED**. Do not infer readiness from systemd status, modal mapping from an IPC acknowledgement, or security acceptance from a visible lock screen. No next guest or automation is started.
