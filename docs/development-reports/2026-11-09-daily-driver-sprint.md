# Wilsof OS — daily-driver sprint, 2026-11-09

Status: four source/QA milestones delivered; **Private3 NOT ACCEPTED**.
Development began 2026-11-09 13:57 UTC; controlled reporting began 14:42 UTC.
Branch: `integration/private3-20261107`.
Final tested implementation: `db4e45223c0c365b0e650b87add5af15624ae958`.
Tracking: [Private3 #60](https://github.com/tomli0/wilsof-os/issues/60) and
[dashboard #16](https://github.com/tomli0/wilsof-os/issues/16).

## Evidence scope

- Historical only: Private2's 18/18 QEMU acceptance and the previous Private3
  720-pass suite / 15-menu-pass overlay. These do not accept current image bytes.
- Newly executed: offline argv reproduction, focused RED/GREEN regressions,
  complete source suites, one new bounded COW source guest, read-only collector
  and CLI smoke, staged-source review and exact remote-content verification.
- Native source overlay maps to `488070e87e0a09d05579de84beab658eefa5ecc8`:
  62 retained payload inputs, two individually guest-hash-verified replacements.
  Later hardware-report/update/deployment changes were **not** in that guest.
- Private evidence root: `wilsof-daily-driver-20261109T1357Z`; logical files below
  are retained privately. No raw logs, credentials or infrastructure are published.

## 1. Completed milestones

1. Diagnosed the shortcut QA execution boundary; reusable tested session-command
   builder added, without changing production shortcuts for the oracle failure.
2. Fixed two independently reproduced desktop defects; actual shortcut capture,
   menu navigation, app/window/workspace interactions and one lock cycle tested.
3. Expanded read-only MacBook diagnostics and added a one-command physical runbook.
4. Added the minimal guarded update CLI and explicit config schema/provenance,
   source-tested and independently AI-reviewed. Native transaction acceptance
   remains pending; this is not delivery of the full daily-driver update goal.

All implementation milestones were committed/pushed separately and recorded on
#60 with exact comment read-back. No merge, release or additional PR was created.
Existing drafts and other worktrees were preserved.

## 2. Review findings and corrections

No new Claude or paid-provider review was commissioned. Two sequential bounded
AI source-review contexts used the inherited included route for the update layer.
These are source assessments, not independent human security certification.

| Finding | Evidence / correction | Result |
| --- | --- | --- |
| QA command dropped before Bash | Real user-manager reproduction of the exact missing `-c` operand; pass `--expand-environment=no` | Corrected and regression-tested |
| Shortcut writer command remained empty | Executed shipped QML function body: unqualified `arguments` modified JS function-local binding; use `editor.arguments` | RED/GREEN and real UI/backend PASS |
| `shutdown`/`logout` search excluded action IDs | Filtering omitted IDs even though ranking supported them; include stable IDs | RED/GREEN and real shutdown search PASS |
| Reviewer: Update entry hidden without local-bin PATH | Check the same absolute sibling launched by the action, including executability, rather than `which('wilsof')` | RED/GREEN; final re-review PASS |
| Missing rfkill state shown as unblocked | Unreadable values previously became false; now unknown/null | RED/GREEN PASS |

Final reviewed staged-patch SHA256:
`bf2801dc5fb5df90c5c6b1aaea770ea193a16c2e58cefd55735e7962a227ad12`.
It was rechecked unchanged immediately before the implementation commit.

## 3. Code quality, safety and tests

### Shortcut root cause

Outer Bash quoting preserves the nonempty intended command. With systemd
expansion enabled, a whole `$HOME/…`-prefixed argument can disappear before inner
`/bin/bash -lc`; Bash exits 2 with the exact original diagnostic. Disabling that
expansion leaves Bash responsible for its own syntax/environment. A literal and
absolute-command control succeed. The corrected native user-manager regression
reaches its intentionally missing executable (127), not a missing `-c` operand.
Local systemd 255 and actual guest systemd 262 were identified. Original private
helpers and failed evidence remain unchanged; a corrected copy was used only in
the new owned test lifetime. No production shortcut workaround was applied.

### Source evidence

| Command / scope | New result | Private evidence |
| --- | --- | --- |
| `WILSOF_NATIVE_SYSTEMD_ARGV=1 python3 -m pytest tests/test_session_command.py tests/test_private3_shortcuts.py -q` | 19 PASS, including real finite user service | `session-command-green.log` |
| QML writer and search regressions | Observed correct RED, then GREEN | `qml-writer-*`, `action-search-*` |
| Hardware/deployment focused selection | 24 PASS | `hardware-green.log` |
| Final update/runtime/actions selection | 34 PASS | `review-menu-route-green.log` |
| `python3 -m pytest -q`, final implementation bytes | **747 PASS / 3 SKIP**, 31.26 s | `source-final.log` |
| Correct-dialect ShellCheck, JSON, changed Python AST, diff whitespace | PASS | Source commands / private verification receipt |
| Actual hardware-report CLI on Ubuntu development host | JSON produced; unavailable components explicit | `ubuntu-diagnostic-smoke.json` |
| Actual `wilsof doctor` alias on that host | Exit 1 with missing-component warnings, not Wilsof acceptance | `wilsof-doctor-smoke.json` |
| Actual CLI help / unattended and non-Arch refusal | Executed; refusal retained | CLI and regression output |

Selections overlap; do not add their totals. Full-suite opt-in skips are native
arch-chroot, disposable wallpaper/systemd lifecycle and the new real-manager argv
case. The last case passed separately as shown; the other two were not rerun.
Qt JS tests strip only `.pragma library` for the JS engine. This is not blanket
QML type/import validation; the affected desktop QML also ran in the native guest.

The new update controller preserves exact repository/signature policy and native
Pacman review/authentication. No partial upgrade, automatic confirmation,
root-executed user source, lock deletion, security bypass or unattended update is
introduced. Package failures/cancellation preserve status and do not migrate
config or retry. Config schema validation precedes writes; version 1 is recorded
only after deployment succeeds. Existing personal settings, backups and tested
manual per-file recovery contracts remain. Backups are not atomic rollback.

## 4. Commits and CI

| Full commit | Milestone |
| --- | --- |
| `1fd186d7b9d5dff35c64e48e9618ab9735494ee3` | QA argv boundary |
| `488070e87e0a09d05579de84beab658eefa5ecc8` | Desktop writer/search fixes |
| `773581744930a348e509c9d7636fae486fa860a7` | Hardware diagnostics |
| `db4e45223c0c365b0e650b87add5af15624ae958` | Guarded update/config versioning |

Every milestone's exact remote head was read back. All **18 changed source/test/
document files** relative to the starting `6edc8fa1b0c84c5c6a7b74156f71e4a9585f8939`
were fetched from GitHub at the implementation SHA and byte-compared successfully.
The later reporting commit is separate and does not change the tested code.

At 14:39 UTC, exact implementation head has zero check runs and zero status
contexts; API `pending` with an empty contexts list means **CI MISSING / NOT
REPORTED**, not a running job or green CI. The workflow's push branch allowlist
does not include this development branch. No CI configuration was modified or
manual workflow dispatched. No Private3 PR was created; earlier drafts preserved.

## 5. ISO identity and readiness

**No Private3 ISO was built.** There is no new filename, size or SHA256 to report.
No previous ISO/backups/QA evidence were deleted, overwritten or rebuilt.
Private2's historical image/hash and 18/18 result remain historical only.

Readiness is **NO-GO for Private3 daily-driver/new-image acceptance**. A reviewed,
source-locked consolidated Private3 owner build command is still not prepared.
Prior builder-authentication limitations were not bypassed or re-tested; no
privileged build attempt was made. Native update/deployment acceptance is a
remaining technical prerequisite, not an excuse to transfer old ISO passes.

## 6. Installation and acceptance matrix

No installation or new-image test was run in this sprint. All 18 **new-ISO** gates
remain NOT RUN because the required new artifact does not exist:

| # | Exact-new-image gate | Result |
| --- | --- | --- |
| 01 | UEFI emulated-USB boot | NOT RUN |
| 02 | Live desktop | NOT RUN |
| 03 | Correct cowspace | NOT RUN |
| 04 | New blank-disk installation | NOT RUN |
| 05 | Installer exit 0 | NOT RUN |
| 06 | Installed disk-only boot | NOT RUN |
| 07 | Ordinary greetd/PAM login | NOT RUN |
| 08 | Installed branding | NOT RUN |
| 09 | Menu before locking | NOT RUN |
| 10 | Native Hyprlock | NOT RUN |
| 11 | Wrong password rejected | NOT RUN |
| 12 | Correct native unlock | NOT RUN |
| 13 | Menu after unlock | NOT RUN |
| 14 | Repeated lock/unlock | NOT RUN |
| 15 | Terminal, Firefox, Files | NOT RUN |
| 16 | Workspaces | NOT RUN |
| 17 | Normal reboot | NOT RUN |
| 18 | Clean shutdown | NOT RUN |

Separate source-overlay results: **6/6 shortcut**, **15/15 menu/navigation**,
**5/5 app/window/workspace** checks passed. The 15 menu cases were re-executed
against the final search change; the earlier run was retained separately. Initial
failed capture and shutdown-search observations were preserved, not relabeled.
Actual menu shutdown search/confirmation led to QEMU exit 0, and a subsequent
non-repairing qcow2 check reported zero errors. This does not fill any row above.

Storage observations: local available **20,254,511,104 bytes** at
2026-11-09T14:42:02Z; builder available **62,134,030,336 bytes** at 14:39:46Z.
No cleanup/allocation/resize was performed. These are observations, not a future
build reservation; capacity must be rechecked before a uniquely identified build.

## 7. Boot, login, desktop and locking observations

One COW guest, one owned supervisor and exclusive QA lock, 2 vCPUs / 4 GiB RAM,
KVM/UEFI with separate firmware and unique paths. Lifetime:
2026-11-09T14:04:27Z–14:17:54Z, bounded to 1,200 seconds.
The stopped Private3 disk and firmware matched preserved hashes before boot and
again after shutdown; they were backing inputs only, not the writable target.

The greeter Username and then Password screens were visually checked before
private synthetic input; greetd PAM opened the ordinary user session. Read-only
QGA/runuser or service readiness was not substituted for password login.

Actual Ctrl+Alt+J capture changed the owning Hyprland binding; Escape cancelled
capture; individual reset restored Super+F1. The UI displayed its saved state.
Login/reboot persistence, full reset and broader native collision coverage were
not tested. A UI claim of persistence is not acceptance evidence for persistence.

Real WS/Super+Space routes, ranked search, text editing, nested selection/history,
About return, power cancellation and final shutdown were exercised. Super+Enter
launched Terminal; menu actions created Firefox and Files clients; forward/reverse
window switching and Super+2/Super+1 preserved application PIDs. The retained
workspace frame visibly contains Terminal/Fastfetch, Files and Firefox. Firefox
renders an old-session restore warning; Internet browsing/session restoration is
not certified. WS bar/numbered workspaces and charcoal/ice-blue identity retained.

One real Super+L cycle: native state locked, normal branded lock surface, exact
locker PID's PAM wrong-password failure, same lock retained; correct credential
released native state, locker exited, and focused Firefox search worked again
in the same shell PID (automatic restarts 0 through that cycle). This is not
all-client input-isolation/security certification, repeated-cycle or suspend
acceptance. No temporary idle stop/inhibitor was introduced in this sprint;
Hypridle was active at the recorded checks. Idle timeout was not measured.

## 8. Remaining daily-driver blockers

- Physical MacBook chipset remains unknown. Wi-Fi scans/connections, Bluetooth,
  sound/microphone, display scaling, suspend/resume and physical power are unverified.
- Current frozen snapshot maintenance does not provide future security/OS
  advancement. Reviewed snapshot progression and private dependency compatibility
  remain work; no rolling switch was implemented.
- Real changed-version/no-op/cancel/failure package transaction, data preservation,
  new authenticated session, boot and recovery acceptance remain pending.
- Config versioning/preservation passed fixtures, not fresh-image/native upgrade
  acceptance. Ext4 + ESP + systemd-boot has no implemented atomic rollback.
- Remaining desktop persistence/full-reset/conflict/idle/logout/reboot/tools and
  small/physical-display gates must be resolved before broad acceptance.
- No current-branch CI or independent human security verdict; no Private3 ISO or
  18-gate new-image result; no complete new build handoff.

Owner physical diagnostic, from the reviewed checkout in the MacBook's Wilsof
session: `python3 bin/wilsof-hardware-report > "$HOME/wilsof-hardware.json"`.
Return JSON privately. See [MacBook runbook](../macbook-diagnostics.md), including
why cached network counts are not active-scan evidence and older Private2 report
commands do not contain the added fields. Do not alter Omarchy or install a
chipset-specific driver without actual identity evidence.

## 9. Engineering standards and documentation

Existing authorized branch/worktree retained; no other worktree/WIP was changed.
Followed [engineering standards](../ENGINEERING_STANDARDS.md), this 12-part report
and [reporting procedure](../development-reporting.md). Updated checkpoint and
private handoff preserve historical evidence and exact source/native boundaries.
New public references are [update contract](../update-layer.md),
[physical diagnostics](../macbook-diagnostics.md), and
[QA boundary](../../tests/integration/SESSION_COMMAND.md).

No report-only branch, ready transition, merge, release, public artifact,
protection/Proxmox/physical-disk change or historical cleanup. Relative links,
sensitive-content scan and diff checks are required before report publication;
exact published report bytes and issue writes are read back afterward.

## 10. Model/API use

Primary route: GPT-6.1-sol / openai-codex, as provided by this session. Two bounded
sequential source-review contexts inherited that route; returned counters report
11 and 5 API calls. Read-only runtime session metadata independently confirmed
both children as GPT-6.1-sol / openai-codex / subscription_included, with completed
lifetimes and actual-cost fields unavailable. They did not start a paid alternate provider or uncontrolled
worker. No model/fallback/authentication/budget configuration was changed.
Actual aggregated billing, token accounting and monthly cost are unknown; no
zero-cost or invoice claim is made. Vision observations are tool evidence, not
independent security review. No provider-cost probe was made merely for reporting.

## 11. Processes, locks and preservation

The owned QEMU/supervisor exited 0; no QEMU remains on the builder. QA lock was
independently available after exit. Child disk/firmware offline checks/hashes
retained; historical backing hashes unchanged. All **45 transferred evidence
files** were independently SHA256-compared. Scoped synthetic-credential scans
(raw/hex/base64) found zero matches in that new evidence set; no forensic-erasure
or global secret-audit claim.

Project lock is held only through synchronous publication by the active parent;
release and independent availability probe are recorded in the final issue/private
receipt, not guessed while publication is live. Worker control was read back as
paused=true/stop_requested=false; existing queue job was listed enabled=false,
state=paused. No scheduler/worker/plugin/hook was created or activated. Existing
Hermes gateway is unrelated and is not stopped. Test/review processes are complete.

## 12. Next recommended sprint

Run one bounded disposable **native update/config lifecycle** cycle on exact
`db4e45223c0c365b0e650b87add5af15624ae958`, including real Pacman/authentication,
private-package preservation, failure/cancel, config backup/manual recovery and
fresh login/boot. Preserve current evidence and use a new COW lifetime/QA lock.

Then prepare one reviewed, hash-locked, capacity/resource-bounded owner-controlled
Private3 build command; build only after its prerequisites pass, using a unique
output, and run all 18 gates on that exact ISO. Physical diagnostic results are
an independent owner input and never replaced by QEMU. No next cycle starts as
part of this controlled close-out.

## Publication receipt

Exact reporting commit, immutable report URL and issue comment URLs are supplied
in the verified final #60/#16 updates and private handoff after push/read-back.
This avoids a self-referential commit loop. Implementation source and later
reporting commit must remain distinct.
