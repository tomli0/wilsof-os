# AS-02 — native Hyprland focus-grab bypass isolated

2026-11-02 UTC. **Outcome: FAIL / BLOCKED. Root cause isolated; no product workaround.**

## 1. Milestones and exact baseline

Repository baseline is PR #50 at `16ca0ec82c7552622cdf4ea74b402fafdf434868`. This investigation is on separate documentation branch `docs/as02-root-cause-20261102`; it does not change that branch, Integration2, PR #49 or PR #51.

The single disposable guest reused the previous installed fixture through a new child COW image. Its existing runtime payload is the rejected experiment `6740e3bec97df5b1e9b7d818dae7705ab01b409a`, not the restored guarded #50 payload. The Command Center QML SHA256 was checked against that exact Git blob: `25f243218496ac43888c0bfcac8a0eabf00ab09f0208d332d1d3faa31e56133e`. This deliberately reproduces the failed Integration3 test; it is not a new deployment or acceptance claim for current guarded #50.

Native stack: Hyprland `0.57.0-1`, reported source commit `0aa6745f705f2c4b0a5004eb019ef76e5bbdb426`; Hyprlock `0.9.6-3`; Quickshell `0.3.2-1`; dux-shell/DMS `2.0.0-1`. No packages or ISO were rebuilt.

## 2. Bindings, IPC and focused reproduction

Actual `hyprctl -j binds`: **131 bindings, 12 locked bindings, zero duplicate chords**. The twelve locked bindings are audio/media/brightness controls. Neither Command Center, Spotlight, Spotlight-bar, settings, clipboard, notepad nor other interactive launcher actions has `locked=true`. Actual loaded Lua files, DMS defaults, user include and Wilsof overrides were read. The old `.conf` file is not the active configuration.

Super+Space resolves to `wilsof-search toggle`, which calls `dms ipc call commandCenter toggle`; Wilsof removes the generated Spotlight binding before registering its own. Alternative ordinary bindings include Alt+Space → Spotlight-bar, Super+comma → settings, Super+V → clipboard, and Super+Alt+L → DMS lock. These are not locked bindings. No binding correction is indicated.

The failed test's route is exactly:

    dms ipc call commandCenter close
    dms ipc call commandCenter search lockedactivation

This is a same-user shell IPC request, not a Hyprland shortcut dispatch. It therefore never passes through the compositor's locked-binding filter. The rejected payload intentionally no longer gates these calls on the asynchronous DMS Boolean. Its handler calls `root.open()` → `DModal.open()` → `DModalHost`, exposes a layer surface and requests a native Hyprland focus grab. The query's initial `lockedactivation` comes from IPC; the additional suffix below comes from newly generated keyboard events, not IPC.

## 3. Exact native input-routing defect

At the installed Hyprland source commit, the native route is:

    CFocusGrab::commit/start
      → CSeatManager::setGrab
      → CInputManager::isLocked()           [wrong kind of lock]
      → CSeatManager::refocusGrab
      → CSeatManager::setKeyboardFocus     [direct seat assignment]
      → CSeatManager::sendKeyboardKey

`setGrab()` comments that no surface should grab over a lockscreen, but its guard calls `g_pInputManager->isLocked()`. That function returns `m_pointerConstraints.locked()`: it tests a locked pointer, **not an ext-session-lock session**. Consequently a new ordinary grab is admitted during Hyprlock.

`refocusGrab()` then calls the low-level `setKeyboardFocus()` directly. Neither that assignment nor `sendKeyboardKey()` performs the session-lock check present in `CFocusState::rawSurfaceFocus()`. In `CFocusGrab::start()`, the grab is installed before the later `refocusKeyboard()` call; the latter can return because the ordinary surface is already focused. The normal surface-focus guard therefore does not repair the earlier seat-level focus assignment.

DMS is the triggering client, not a separate authentication authority: its shipped `KeyboardFocus.qml` selects OnDemand on Hyprland, `DModal` requests `DFocusGrab`, and `DFocusGrab` activates `HyprlandFocusGrab`. The independent minimal client below uses the same native grab without DMS, Wilsof or logind state and reproduces the leak.

Pinned primary source: [SeatManager.cpp](https://github.com/hyprwm/Hyprland/blob/0aa6745f705f2c4b0a5004eb019ef76e5bbdb426/src/managers/SeatManager.cpp), [InputManager.cpp](https://github.com/hyprwm/Hyprland/blob/0aa6745f705f2c4b0a5004eb019ef76e5bbdb426/src/managers/input/InputManager.cpp), [FocusGrab.cpp](https://github.com/hyprwm/Hyprland/blob/0aa6745f705f2c4b0a5004eb019ef76e5bbdb426/src/protocols/FocusGrab.cpp), [FocusState.cpp](https://github.com/hyprwm/Hyprland/blob/0aa6745f705f2c4b0a5004eb019ef76e5bbdb426/src/desktop/state/FocusState.cpp). Downloaded source hashes are preserved with the evidence. This is source-path analysis corroborated by actual protocol events, not an instrumented C++ backtrace or validation of a patched compositor.

## 4. Evidence, regressions and CI

One guest, one secured lock lifecycle, three harmless sentinel-input runs; chronological order **C, A, B**. No further keyboard input followed B.

| Case | Actual result |
| --- | --- |
| A — Hyprlock active, CC inactive, minimal hidden | `sentinela` did not change CC's empty query or the hidden client's `control`/7-key state. PASS within this scope; not proof for every ordinary application. |
| B — Hyprlock active, exact CC IPC activation | Query changed `lockedactivation` → `lockedactivationsentinelb`. **FAIL**. DMS received nine new presses and nine releases. |
| C — independent ordinary minimal client activated with native grab | Query became `control`; seven new presses and seven releases. **FAIL**, independent of DMS and Command Center. |

The idle locker acquired the session earlier than intended: Hypridle logged locked at **22:03:18**, and Hyprlock PID 1215 logged `onLockLocked` at **22:03:20**. The intended unlocked minimal-client control was therefore reclassified as case C, not falsely reported as an unlocked PASS. At **22:09:15**, its `hyprland_focus_grab_v1.add_surface/commit` was followed by `wl_keyboard.enter` for the same `wl_surface#46`; `control` arrived at **22:09:21–22**. A later attempt to start the direct wrapper returned busy/75 because the same locker already owned the guard; it did not create another lock lifecycle.

For B, **22:16:08**: DMS committed a grab for `wl_surface#65`; **22:16:09**: its `wl_keyboard.enter`; **22:16:13–15**: new key events. Before/after owning status confirms the appended suffix. PID 1215 remained alive and there was no authenticated unlock. Native second-lock requests were denied before and after A/B: `FINISHED_SECOND_LOCK_DENIED`, with `allow_session_lock_restore=false`. This directly checks compositor lock ownership, rather than trusting only a rendered locker or logind's hint. `session_lock_xray=false`; the screenshot still shows Hyprlock.

Relevant baseline source regressions: **73 passed in 5.37 s**:

    python -m pytest -q tests/test_auth_session.py tests/test_command_center.py tests/test_scripts.py

Evidence self-check asserted A/B/C owning state and the 14/18 actual minimal/DMS key events. Source tests are not a native security PASS. GitHub checks for the documentation head are checked separately at publication; no CI-green claim is inferred.

Evidence: [summary](../qa/as02-root-cause-20261102/summary.json), [actual Wayland event trace](../qa/as02-root-cause-20261102/wayland-events-recovered.json), [minimal client](../qa/as02-root-cause-20261102/minimal.qml), [locked leak frame](../qa/as02-root-cause-20261102/locked-leak.png), [source hashes](../qa/as02-root-cause-20261102/upstream-source-sha256.json).

## 5. ISO identity and preservation

**No ISO build or ISO modification.** Preserved Integration2 identity from the prior manifest: `wilsof-internal-2026.11.01-integration2-x86_64.iso`, 2,549,536,768 bytes, SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`, original source `b755bfabf82ece67eea3d666ea94330ff95f738e`, artifact root `internal-test-20261101-integration2/`. Its historical acceptance is not upgraded by this investigation.

The original guest COW, its backing disk and original firmware were hash-verified before/after use of the new child COW. Existing QA artifacts were not overwritten. This is a scoped preservation check, not a fresh full historical ISO inventory audit.

## 6. Installation and storage

No installation, package transaction, formatting, physical disk/USB write or infrastructure change. The only writable guest disk was the new disposable child image; firmware variables were copied. A separate sparse raw copy was subsequently used only for offline evidence extraction and mounted read-only with `noload`; the mount and owned read-only loop device were detached afterward.

## 7. Authentication and acceptance

| Acceptance criterion | This investigation |
| --- | --- |
| Lock → ordinary applications receive no new input | A's inactive clients unchanged; C demonstrates ordinary active-client isolation **FAIL**. |
| IPC activation during lock produces no leakage | **FAIL**, case B. |
| Incorrect password remains rejected | Not rerun after the native leak; historical Integration3 evidence is not transferred. |
| Correct password unlocks normally | Not rerun; no password was sent after this session locked. Ordinary greeter/PAM login before the test is not lock-unlock acceptance. |
| Command Center works after unlock | Not rerun; security stop. |
| Immediate relock remains isolated | Not rerun; security stop. |

No PAM/authentication change, administrative unlock, forceunlock, locker kill or Boolean unlock authorization was used. The sentinel typed in A was never submitted as a password. The guest was powered off while still locked.

## 8. Correction decision and limitations

**No product fix attempted, so no attempted fix requires reverting.** The failure is inside native Hyprland input isolation and reproduces without DMS. Per mission constraints, stop and preserve evidence instead of masking it by blocking Command Center, changing focus settings or introducing a new lock-state protocol/daemon/coordinator. The existing Integration3 revert and #49's restored gates remain untouched.

The initial journal filter failed because systemd JSON MESSAGE may be a byte array, not a string. The original journals were recovered from the stopped owned disk using the read-only mount, decoded correctly and filtered into the published trace. Raw journals remain private. A readiness loop also waited on the wrong direct-lock unit while the idle locker already held the lock; this is disclosed harness behavior, not another successful authentication or another deliberate input reproduction.

No new generic architecture review, package patch/build, fourth reproduction or hardware test. Physical keyboard/GPU/session timing and suspend/resume remain untested. Current guarded #50's complete native acceptance remains unverified; these results diagnose its rejected experiment and the installed compositor defect.

## 9. Documentation and branch scope

Only this report and sanitized QA evidence are added on the isolated branch. No main merge, public release, force-push, issue closure, branch deletion, scheduler activation or modification to PR #49/#50/#51. Publication is read back at the exact commit and summarized on permanent status issue #16. Raw journals, guest images and fixture secret are excluded from Git.

## 10. Model/API costs

One main agent, supplied route gpt-6.1-sol / openai-codex. No new agents or paid review services. Actual subscription billing is unavailable, not claimed to be zero. Local Python/QEMU and primary-source retrieval only; no provider budget contact or routing changes.

## 11. Shutdown, lock and checkpoint

QGA `guest-shutdown` requested normal powerdown. Its RPC timeout was reconciled against the exact owned QEMU PID/start identity: the guest exited; no second shutdown command was sent. Non-repairing offline child-qcow2 check returned **0**. No QEMU exit-status value is invented from process disappearance. The exclusive established project lock remains held only through publication/read-back, then is released with an identity-bound signal and an independent availability probe recorded in the private checkpoint. Worker remains `paused=true`; scheduler remains disabled/paused.

Durable private checkpoint: `.local/state/wilsof-qa/as02-root-cause-20261102/checkpoint.json` under the owner's home. Source snapshots, original/recovered evidence, guest disk and credential remain private there. Free space at **2026-11-02T22:20:41.887916Z**: **56,860,819,456 bytes / 52.9557647705 GiB**. No historical artifact cleanup.

## 12. Stop decision

**Root-cause isolation complete; security acceptance FAIL / BLOCKED. Stop after this task.** No application-side workaround or next milestone starts automatically. A native compositor correction and its separate authorized acceptance would be required before treating this route as secure; this investigation neither implements nor certifies one.
