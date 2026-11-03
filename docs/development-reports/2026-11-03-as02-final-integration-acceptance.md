# AS-02 final integration acceptance — 2026-11-03

Status: **PENDING — Integration3 NO-GO.** The successful minimal native A/B baseline is preserved, not repeated. This session did not complete final DMS/Command Center acceptance and is not an integration recommendation.

## 1. Milestones and scope

Reconciled the published [minimal native report](2026-11-03-as02-minimal-native-ab.md), private checkpoint, current branch heads, project pause controls, process state and protected hashes. Used one new disposable COW child of the previously tested candidate disk, with copied firmware. Fresh ordinary greetd PAM login, an active Wayland session and exact patched compositor startup **PASS**. No compositor rebuild, new ISO, physical installation, host modification, merge, release, force-push or scheduler/worker activation.

## 2. QA findings and blocker classification

The harness stopped at its 210-second overall bound while waiting for normal DMS readiness. The latest service observation was exactly `ActiveState=activating`, `SubState=start`, with a nonzero main PID. Private journal evidence nevertheless records QML configuration loaded, DMS API v38/CLI v2.0.0 connected and the `wilsofCommandCenter` daemon plugin loaded. These are partial startup evidence, not proof that its owning IPC or UI is ready. No Command Center status response was collected because the harness's active/running prerequisite never became true. The global bound included boot/login, so it did not provide a full separate DMS observation budget.

**This is an incomplete harness/readiness gate, not a demonstrated compositor security failure or proof that DMS is broken.** No code or security requirements were weakened, and no additional guest was started to chase a pass. No Claude or independent QA review was run.

## 3. Security and native focus evidence

Exact packaged-source hashes were rechecked against retained native build provenance. Bounded patch/source inspection was retained privately; it is **self-review only**, not a complete alternate-focus/lifecycle audit or independent approval. The patch and detailed vulnerability/reproduction evidence remain outside the public repository. The existing private upstream security draft was not submitted externally.

Historical minimal candidate evidence on this exact unchanged package remains **PASS**: both recorded lock intervals had **0 ordinary keyboard.enter and 0 ordinary key events** despite native grab requests and harmless test input. Historical legitimate lock input, wrong-password rejection, authenticated unlock, ordinary-input recovery and immediate-relock isolation passed. These counts are from `minimal4`, **not fresh DMS integration evidence**. This run reached no new secured-lock interval and supplies no new locked-input counters.

## 4. Git and CI

Report branch: `fix/as02-native-20261103`; starting head `4f219f7da09f8d5044d64fc9352c64de9bbd26dd`. Integration3 remains at the previously recorded `16ca0ec82c7552622cdf4ea74b402fafdf434868`, subject to final remote read-back. Only this sanitized documentation file is staged; other remote heads are compared with the session-start snapshot. Exact report blob/head and status issue comment are read back after publication. CI is queried at the final report commit separately; a missing check is not a green result. No main merge or deployment.

## 5. Exact package, source and preserved ISO

- Package: `hyprland-as02-private 0.57.0-1.1`; 53,701,518 bytes.
- Package SHA256: `b81531b9cf70b9f372238539cd64ae7d2ad66b41f1fc429dec6e998c41873a1f`.
- Upstream source revision: `0aa6745f705f2c4b0a5004eb019ef76e5bbdb426`.
- Source archive SHA256: `93b1fc24caca857e31d52717f4879c6f6132644d7b25365e947065dbe99ed125` (retained prior provenance; archive not freshly rehashed here).
- Unchanged private patch SHA256: `f75de0300bebde61151f83171e7ca1ed2a32b1f1296b1273536f8e41a68dfadf`.
- Guest-owned compositor ELF SHA256: `8a4a88e1cfebe165f37b50a9a83cacb2632adce6a3bd66fef44b2365b0c0e096`; retained Build ID `3e028756ffffaae966ced21992c5bdf2e995d4d5`.
- Local unsigned private candidate, not an official upstream release. Package ownership and native running-version output were collected anew; unchanged native source hashes checked anew. No package installation/rebuild was needed in the inherited candidate.
- Historical ISO, not attached or rebuilt: `wilsof-internal-2026.11.01-integration2-x86_64.iso`; 2,549,536,768 bytes; SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`, freshly verified unchanged.
- Package, disk, firmware and raw evidence remain in private owner QA storage; none is published with this report.

## 6. Installation and normal-desktop acceptance

| Gate | Result | Evidence / limitation |
| --- | --- | --- |
| New installation / ISO boot | NOT RUN | Explicitly out of scope |
| Installed disk-only cold boot | PASS | New COW child; no ISO |
| Ordinary PAM login | PASS | Genuine greeter password input and greetd PAM session plus active Wayland session |
| Hyprland startup | PASS | Exact private package ownership, ELF and compositor-instance version |
| DMS startup | PARTIAL / PENDING | Configuration/backend/plugin loaded; owning UI/IPC readiness unverified |
| Command Center opening | NOT RUN | Readiness prerequisite not met within bound |
| Keyboard navigation | NOT RUN | No owning Command Center observation |
| Normal application launch | NOT RUN | Test not reached |
| Lock with Command Center, IPC activation, sentinel, focus isolation | NOT RUN | No fresh DMS native-focus claim |
| Full DMS wrong/correct unlock and recovery | NOT RUN | Historical minimal authentication retained, not substituted |
| Immediate relock with DMS | NOT RUN | Historical minimal relock retained, not substituted |

No root/runuser administrative command is counted as ordinary password authentication. The private synthetic QA credential is not published.

## 7. Authenticated unlock and recovery

Historical exact-package minimal native acceptance passed wrong-password rejection, `auth: authenticated for hyprlock`, normal locker exit, ordinary-client input resumption and immediate relock. They were not rerun merely for presentation. Fresh full-DMS legitimate input, wrong-password rejection, normal authenticated unlock, DMS/Command Center recovery and immediate-relock acceptance remain **PENDING / NOT RUN**. No forced unlock or authentication bypass occurred.

## 8. Lifecycle and failure scenarios

| Required case | Fresh final-integration result |
| --- | --- |
| DMS restart while locked | NOT RUN |
| Command Center IPC disconnect | NOT RUN |
| Repeated lock cycles | NOT RUN |
| Direct external Hyprlock invocation with normal DMS | NOT RUN |
| Hypridle-triggered locking | NOT RUN |
| Session logout/login | NOT RUN (initial PAM login did pass) |
| Locker abnormal termination / fail-closed behavior | NOT RUN |

The harness contains later lifecycle steps, but unexecuted code is not acceptance evidence. Physical client keyboard forwarding, GPU/seat behavior and real hardware remain unverified. No new bypass was observed; absence of an executed security test is not a pass.

## 9. Independent review and engineering standards

**Independent security review: PENDING.** No genuinely separate reviewer verdict was obtained. The configured auxiliary review route and inherited fallback chain include paid OpenRouter routes; they were not invoked under the no-new-paid-agents constraint. This does not establish that every possible included reviewer is unavailable; it records that none was safely dispatched in this bounded session. Existing bounded self-review is not renamed independent.

A future independent review must inspect the exact affected source revision and unchanged patch: `setGrab()`, `refocusGrab()`, `setKeyboardFocus()`, `rawSurfaceFocus()`, related keyboard/pointer delivery and session-lock transitions, destroyed-client handling, legitimate locker input, immediate relock and regressions. Followed the repository's [reporting standard](../development-reporting.md); publication does not imply merge or security acceptance.

## 10. Model, iteration and cost boundary

One main agent, supplied `gpt-6.1-sol` / `openai-codex` session. Runtime metadata identifies subscription inclusion; actual billed cost is unavailable, not asserted to be zero. No new paid agents/services, provider budget probe or independent child dispatch. The task is closed within the requested twelve-agent-iteration ceiling; no subsequent acceptance run is scheduled automatically.

## 11. Shutdown, disk integrity, preservation and pause state

The established identity-checking shutdown helper was exercised and the owned guest exited. Its final receipt says `already-exited` because the outer cleanup called the idempotent helper a second time; the first method receipt was overwritten, so the final receipt alone is not proof of the first RPC's response. All QEMU and protected build processes were independently absent before the offline check. New disposable qcow2 check **exit 0**, no errors. **Eight** protected package/disk/firmware/ISO hashes match the before snapshot. Original installed disk, candidate backing disk, historical overlay, firmware and ISO were not modified.

The project lock was acquired by the test driver and released by that same legitimate owner after protected work exited; availability was independently probed. Publication uses the same exclusive lock without starting a worker. Final process/lock/pause checks are recorded after publication. Worker stays paused; Wilsof scheduler remains disabled/paused. Available storage at 2026-11-03T11:11:48.405500+00:00: **45592784896 bytes (42.462 GiB)**. No deletion or cleanup of historical artifacts.

Private durable checkpoint: logical `wilsof-qa/as02-native-20261103/checkpoint.json`; new evidence `final-integration/`, including exact identity, readiness excerpt, journal, result, offline check and before/after preservation manifests. The earlier minimal A/B checkpoint evidence remains intact.

## 12. AS-02 decision and exact Integration3 requirements

**AS-02: PENDING. Integration3: NO-GO.** The working minimal native baseline is preserved. No integration or deployment is recommended from these partial results.

Next bounded acceptance must reuse this exact package and a disposable COW, with a separate realistic cold-DMS observation budget. Reconcile DMS's notification/service state with real owning Command Center IPC readiness rather than classifying startup delay as a security failure. Then complete every normal-desktop, native locked IPC/input/focus, authenticated recovery, immediate-relock and lifecycle gate listed above, and obtain an independent cost-free security PASS against the exact source/patch. Preserve detailed evidence privately. Only all required gates passing permits recommendation for controlled Integration3 integration; physical checks remain separately disclosed. No rebuild, ISO, merge, release or external security submission is authorized by this report.
