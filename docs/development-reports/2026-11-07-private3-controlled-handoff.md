# Private3 — controlled implementation handoff, 7 November 2026

Status: CONTROLLED STOP / PARTIAL IMPLEMENTATION / NOT ACCEPTED.

Implementation started at approximately 19:41 UTC. Close-out checks began at 22:17 UTC. No new feature cycle, VM boot, ISO build or full regression run was started during close-out.

Branch: `integration/private3-20261107`.
Source checkpoint: `054e201aa83e2c6aec5de346871f4284d3475fad`.
Approved Private2 base: `063b7f034dce7387e88f649f2c67ba95f370fcdc`.
Status issue: #16. Private2 draft #59 is retained unchanged. No Private3 PR exists at this checkpoint.

## Evidence boundaries

The last complete source run and the two GUI deployments are different evidence scopes. None establishes acceptance of a fresh Private3 ISO.

- Baseline source suite: 682 passed, 2 native opt-in skips.
- Last retained complete source run: **720 passed, 2 skipped**, in 31.22 seconds. This corrects the earlier interim summary of 717; the later log was recovered during close-out. Later UI/theme/query changes were not followed by another complete run.
- Earlier focused checks: 40 passed; a subsequent shortcut/navigation selection had 30 passed. These overlap the full suite and are not additional unique totals.
- `dev3` source payload SHA256: `65093b7f77ba7ff72c195f8edab789308db591cad02cbe526eab177d0e36a278`. Its resident-menu navigation run recorded **15 PASS, 0 FAIL**.
- `dev4` payload SHA256: `4258a5d7cc513bdabf1e45817b1e21c52504c7abb23d08fa027805333cbe26ac`. All 62 payload files match the source checkpoint byte-for-byte. Its shortcut UI run recorded **1 PASS, 1 FAIL**, then stopped; remaining cases did not execute.
- The `dev3` payload differs from the checkpoint in four files: search-wrapper final whitespace, About QML, shortcut QML and keybinding labels. Do not label its complete GUI pass as a final-checkpoint pass.
- Private evidence, source patches, pre-staging files, GUI frames and remote receipts are retained outside Git. The local `PRIVATE3_HANDOFF.md` contains their exact locations and continuation instructions; it is deliberately not published.

## 1. Implemented source work

The coherent source checkpoint contains:

- One resident Wilsof Menu, addressed by WS click and Super+Space, with exactly eight categories, ranked search, nested forward/back navigation, saved selections/scroll positions, search focus, and dialog return state.
- An authentic-logo bar component, numbered workspace defaults, removal of profile UI from the new-image payload, and preservation/migration of existing user data.
- Required default bindings, native Hyprland window cycling, and removal of the generated alternative launcher binding.
- A shortcut backend with actual-binding queries, conflict refusal before writes, tagged ownership, reload/read-back checks, configuration rollback and persistent Lua overrides; a shared keyboard-capture UI remains runtime-unverified.
- The locked About wording, cropped original WS logo with provenance, installed credits/license access, Terminal naming, interactive-only Fastfetch integration and original ASCII artwork.
- Focused screenshot/recording/emoji/software actions, an expanded lightweight package closure, and privacy-restricted hardware diagnostics.

This is implemented source, not a declaration that every action works in the installed product.

## 2. QA findings and investigation

No new Claude assessment, paid fallback or independent security review was commissioned.

The source-overlay navigation evidence covers real WS clicking, Super+Space, keyboard focus, mouse entry, nested navigation/back selection, inner WS home, six requested search examples, text editing, Escape hierarchy, power-confirmation cancellation and About return state.

The shortcut script failed while reading its verification oracle:

    /bin/bash: -c: option requires an argument

The recorded command returned exit 2 with empty stdout. The intended call was `$HOME/.local/bin/wilsof-shortcuts list --json`, routed through QGA, `runuser`, `systemd-run --user` and a second `bash -lc`. Static reconstruction retains a nonempty command argument. Environment expansion/argument handling across that boundary is a hypothesis, **not a confirmed root cause**. This does not prove that GUI capture failed or succeeded; it may already have changed a binding before read-back failed.

Next investigation: use an argv-only substituted fixture to capture each boundary and compare literal/absolute and `$HOME` command forms. Check the actual guest manager's documented expansion behavior before proposing a helper fix. Do not change product shortcut logic on the present evidence alone.

## 3. Source quality and security status

Close-out only: Python AST parsing of 21 changed Python inputs, JSON parsing, JavaScript grammar checks of Model/Capture with only Qt's `.pragma library` stripped from parser input, and staged whitespace checks passed. These are not native QML type checks or a security certification.

A bounded added-line scan found no `shell=True` or simple hard-coded secret assignment. No independent review occurred. Private raw evidence was not published. One trailing blank line in a new test was removed solely to pass the staged whitespace gate; its original bytes remain in the preservation archive. No functional source change was made during wrap-up.

## 4. Git and CI

The 44-file implementation was committed as a cohesive **WIP** checkpoint rather than split into potentially unusable partial installations. Source: `054e201aa83e2c6aec5de346871f4284d3475fad`. This report is a following documentation commit on the same branch.

No merge, release, ready transition or new PR was performed. Remote CI is not claimed green. The current workflow push filters do not include the Private3 branch, and no manual workflow was dispatched.

## 5. ISO identity

No Private3 ISO was built. There is no Private3 size or SHA256 to report.

The retained accepted Private2 ISO has SHA256:

    9a6fd11488546193e6e85584a22ad33ff3fbb648857e3ba62383d5da7a64ae8e

Its local checksum was verified during implementation. Private2 base-disk and firmware hashes were independently matched again after the disposable COW guest exited. No historical artifacts were deleted or overwritten.

## 6. Required new-ISO acceptance matrix

All rows below are **NOT RUN / BLOCKED: no new Private3 ISO**. Historical Private2 acceptance and source-overlay results do not transfer.

| ID | Required new-image gate | Status |
| --- | --- | --- |
| 01 | UEFI boot from emulated USB | NOT RUN |
| 02 | Live Hyprland/Dux desktop | NOT RUN |
| 03 | Correct cowspace behavior | NOT RUN |
| 04 | Real installation onto a new blank QCOW2 | NOT RUN |
| 05 | Installer exit code 0 | NOT RUN |
| 06 | Disk-only boot without ISO | NOT RUN |
| 07 | greetd/PAM password login | NOT RUN |
| 08 | Installed desktop and branding | NOT RUN |
| 09 | Wilsof Menu before lock | NOT RUN |
| 10 | Native Hyprlock | NOT RUN |
| 11 | Incorrect password rejected | NOT RUN |
| 12 | Correct password unlock | NOT RUN |
| 13 | Wilsof Menu after unlock | NOT RUN |
| 14 | Repeated lock/unlock | NOT RUN |
| 15 | Terminal, Firefox and file manager | NOT RUN |
| 16 | Workspace switching | NOT RUN |
| 17 | Normal reboot | NOT RUN |
| 18 | Clean shutdown | NOT RUN |

## 7. Source-overlay session and authentication

A separate COW overlay over the retained Private2 installation was used, with a copied firmware file and a new guest lifetime. Normal greeter authentication and a native Hyprlock password unlock were observed there; the latter was followed by successful menu admission. These are explicitly **Private2-base/source-integration** observations, not fresh Private3 installation or complete security acceptance.

The owner reported QMP shutdown. The preserved supervisor exit receipt is 0; close-out independently found no QEMU/test process, a closed VNC listener and an available QA lock. An offline, non-repairing COW consistency check returned 0 with zero check errors. The disk and firmware were hashed and retained without another boot.

## 8. Unfinished and unverified work

- Final complete regression and final-source native GUI acceptance remain pending.
- Interactive capture, capture cancellation, individual/all reset, live conflicts and reboot persistence need conclusive native verification after the oracle failure is isolated. Backend fixture tests are narrower evidence.
- Actual launches, window cycling, workspace clicking/occupancy, capture output, recording stop/output, clipboard/emoji transfer, and normal-user software transactions need recorded functional acceptance.
- Final palette changes, scrollability/license access and small-screen behavior need final-source rendered/input checks.
- Window-visual preferences are intentionally capability-disabled; no unsupported control is advertised as working.
- Physical MacBook chipset, firmware/driver selection, scan failure, Bluetooth, audio, graphics/scaling and laptop power remain unverified. Cached scan diagnostics deliberately do not force a scan or expose SSIDs/BSSIDs.
- Builder sudo authentication is unavailable to the agent. A consolidated, reviewed owner build handoff has **not** been completed; no speculative owner command is supplied.
- No Private3 ISO, draft PR or independent security approval exists.

## 9. Reporting and preservation

The approved Private2 source, draft #59 and historical artifacts remain preserved. Pre-staging tracked diffs, all changed/untracked source, raw test logs, payload archives and GUI evidence were retained privately. Exact local/remote paths and hashes are in the local handoff, not this public report.

No report-only branch was created. No other worktree was reset, stashed, cleaned, merged or deleted.

## 10. Model/cost boundary

No child reviewer or paid fallback was started for close-out. The implementation session had reported the OpenAI Codex subscription route; no new provider-budget probe was made. Actual billed cost is not available and is not asserted to be zero.

## 11. Process, lock and temporary-service state

At 22:17 UTC, local test-process inspection found no matching orphan and the project lock was available. Builder inspection likewise found no QEMU/source-test orphan; the QA lock was available and VNC connection was refused. The Hermes main process/gateway is not treated as an orphan and was not killed.

The existing queue job and project worker remain paused. No scheduler or worker was restarted. Hypridle had been temporarily stopped and the DMS inhibitor enabled inside the disposable source guest; restoration was not verified before its shutdown. That retained overlay is not evidence of normal idle-policy acceptance.

## 12. Next bounded action

Read the local `PRIVATE3_HANDOFF.md`, verify exact branch/head and preservation receipts, then isolate the shortcut oracle's argv/environment boundary **without QEMU or product edits first**. Only after a controlled reproduction should a later authorized implementation cycle repair/retest the relevant path, complete the owner build handoff and eventually build/retest a unique image. Physical hardware remains a separate gate.

Private3 must remain marked **NOT ACCEPTED**.
