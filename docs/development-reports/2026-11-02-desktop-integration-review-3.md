# Independent Review 3/5 — Desktop Integration, Hyprland, DMS and Startup

Date: 2026-11-02. Verdict: **NEEDS REMEDIATION**.

## 1. Scope and source identity

Read-only implementation review; the only committed addition is this report. Reviewed GitHub PR bodies/comments/reviews, changed-file lists, actual source, and prior reports. At retrieval all three PRs were OPEN, unmerged:

| PR | Head branch | Exact reviewed head |
| --- | --- | --- |
| #47 | `feat/integration-20261101` | `0abf4a51af2338f14c691c2d325d6abfa2c8a410` |
| #48 | `fix/installer-safety-20261101` | `26cf38457efb170d587bd6e1f0b6f353c92fab5c` |
| #49 | `fix/auth-session-security-20261102` | `a28d4678bbbaa091337fdab2b331a1b9e56b7e4d` |

Report branch: `review/desktop-integration-20261102`, based on #49, which descends from #48 and Integration2. #47 remains stacked on `feat/accept-completion-20261031` (`2122cd012a5edba30b0025cd68e2731b1d9e9a67`). Also inspected the Command Center development-to-acceptance change inventory and #47 integration diffs. This is focused inspection of relevant desktop code, not exhaustive review of every historical branch. References below use #49 line numbers. The implicated appearance/shortcut/systemd/plugin files are byte-unchanged from #47; `runtime/desktop.py` differs only by the previously reviewed AS-01 executable-list additions at line 60. Findings therefore apply to Integration2 as well as this remediation stack.

## 2. Findings by severity

Critical: none demonstrated. High: none demonstrated. Three Medium findings and one conditional Low finding follow. No graphical or production-service behavior was reproduced.

### DI-01 — Medium: upgrading an existing plugin configuration omits Command Center activation

Source: `runtime/desktop.py:88–104`, especially `100–104`; consumer entrypoint/fallback: `bin/wilsof-search:15–22`; plugin descriptor: `config/dms/plugins/wilsofCommandCenter/plugin.json:7–10`.

The plugin files are deployed, but `wilsofCommandCenter.enabled=true` is only inserted when the entire plugin settings file is new. An existing file containing `wilsofProfiles` is never updated; an existing file containing only an unrelated plugin gets Profiles but not Command Center. This is a missing upgrade initialization, not an allegation that an explicitly disabled plugin should be forcibly enabled.

Verified with the real `install_user()` against three disposable homes with a fixture-generated Hyprland base: existing Profiles -> no Command Center entry; unrelated personal plugin -> personal entry preserved, Profiles added, Command Center absent; missing settings file -> both Wilsof plugins enabled. The fallback can conceal the omitted feature by opening upstream Spotlight. Actual plugin-load/UI behavior remains untested.

Required correction: migrate missing Wilsof plugin entries independently, preserving explicit disabled states and unrelated plugin data. Add upgrade fixtures, not just fresh-home assertions.

### DI-02 — Medium: single-action shortcut reset bypasses conflict checking

Source: `bin/wilsof-shortcuts:172–190,195–206`; Lua generation `130–149`; defaults `config/wilsof-keybinds.json:4–14`; load order `config/hypr/wilsof.lua:86–92`.

`set` checks conflicts, but `reset ACTION` does not check whether another action now owns that action's default. Reproduction, with isolated HOME/state and the real CLI:

    wilsof-shortcuts set command-center ALT+F12
    wilsof-shortcuts set lock SUPER+space
    wilsof-shortcuts reset command-center
    wilsof-shortcuts list --json

All mutations return 0. The resulting map reports BOTH `command-center` and `lock` on `SUPER + space`. Generated Lua unbinds `SUPER + L` and binds `SUPER + space` to `wilsof-lock`, while the base already binds that key to search. This proves conflicting configuration generation; it does not prove which action a running compositor dispatches. No real lock was requested.

Required correction: validate the complete post-reset effective map before writing either file; refuse the collision or use an explicit, documented coordinated reset. Add this sequence and binding-map consistency regressions. Do not change AS-02 authentication synchronization as part of this finding.

### DI-03 — Medium: appearance-only reset replaces unrelated DMS settings

Source: `bin/wilsof-appearance:2–6,21–22,79–95`.

Despite claiming that nothing outside appearance defaults is touched, reset validates the existing JSON and then replaces the entire document with `dict(defaults)`. It does not merge only appearance-owned fields. Unrelated DMS preferences disappear or revert to template values.

Verified directly with `command_reset()` using a disposable settings file containing `personalSentinel="KEEP"` and `loginctlLockIntegration=false`: return 0, sentinel removed, lock-integration key absent from the replacement, one recoverable settings backup produced. Absence is NOT proof of the effective upstream lock default; no authentication behavior is claimed. The explicit reset and backup limit impact, but do not make this an appearance-scoped operation.

Required correction: merge only explicitly defined appearance fields into current settings, retaining unrelated/authentication preferences. If a full settings factory-reset is desired, expose it separately with accurate warning/confirmation. Add nonappearance-preservation tests.

### DI-04 — Low, conditional: reapplying configuration does not repair executable modes

Source: `runtime/desktop.py:34–50,60–61`.

`write()` returns on equal bytes before checking the requested mode. If an installed helper has intact contents but lost its executable bit, configuration reapplication reports success yet leaves the command unexecutable.

Verified: provision a fixture home, chmod its installed `wilsof-search` to 0644, reapply `install_user()`; final mode remains 0644. No actual desktop launch was attempted. The failure requires prior permission damage; fresh-file installation sets 0755 correctly.

Required correction: validate/repair mode for owned managed regular files even when contents match, without broad chmod of personal paths. Add a mode-only drift regression.

## 3. Existing safeguards

- `bin/wilsof-session:4–17` validates arguments, uses exec, and delegates to packaged `start-hyprland`; ordinary output is journal-routed while diagnostic mode preserves direct output. It does not invent a replacement PAM/session supervisor.
- Installed greetd explicitly uses `tuigreet --time --cmd /usr/local/bin/wilsof-session` as `greeter` (`runtime/provision-target:79–89`). Session-start/materialization fixtures passed. ReGreet remains an opt-in candidate, not the accepted default or a newly certified installed payload.
- `runtime/desktop.py:134–143` generates DMS's Hyprland base only when absent and appends the Wilsof require once; it rejects a nonregular/symlink entry. An existing base is preserved, not silently regenerated.
- User-unit enablement is offline (`runtime/desktop.py:145–163`), avoiding another user's bus. DMS/idle are linked to graphical-session; wallpaper to the Wilsof target. `config/systemd/wilsof-session.target:3–5` orders DMS and requires graphical-session. Absence of `PartOf=` alone is not a demonstrated logout bug: Requires already propagates explicit dependency stop, while actual compositor teardown remains a dynamic gate.
- `config/systemd/dms-wilsof.conf:3–9` allows 300-second cold startup and queues wallpaper nonblocking after successful DMS activation. The ignored hook failure avoids making cosmetic failure fatal. `wilsof-wallpaper.service:3–11` supplies dependency/order, a binary condition, and bounded oneshot execution. `bin/wilsof-apply-wallpaper:9–26` retries IPC within a bounded window and checks both set acknowledgement and get path. This avoids incorrectly reporting the old wallpaper dependency-recovery omission as still wholly unfixed.
- Canonical provisioning confines managed paths, refuses unexpected symlinks, atomically replaces changed files, and saves per-file backups (`runtime/desktop.py:21–53`). Existing personal DMS settings, Dux's specific legacy-to-`dms` migration link, Ghostty and app shortcuts are preserved (`78–86,106–122`); user shortcut override files are not seeded over. Backups are not a transactional rollback.
- Search requires the Command Center IPC marker and falls back to Spotlight; a known locked marker does not trigger fallback (`bin/wilsof-search:15–22`). Plugin file-search failures remain isolated to search results (`CommandCenter.qml:168–200`), with generation-based stale-result rejection and modal closure on session-lock notification (`68–85,204–235`). These source safeguards do not certify real keyboard grabs or AS-02.

## 4. Startup/lifecycle risks requiring dynamic testing

These are unproven failure paths, not additional confirmed defects:

1. The Dux v2.0.0 generated base submits environment import and `hyprland-session.target` startup separately; Wilsof submits its own target on `hyprland.start` (`config/hypr/wilsof.lua:33–36`). Source order alone does not establish completed environment import before service activation. Check cold/re-login environment, actual start-hyprland/watchdog implementation, user-manager DISPLAY/WAYLAND_DISPLAY and target readiness; inject slow import only in an authorized disposable environment.
2. Repeated DMS crashes, clean unexpected termination, restart limits, failed IPC/asset, timeout, and logout during pending wallpaper activation: inspect exact packaged unit, actual journal/InvocationID/NRestarts, child/cgroup teardown and rendered recovery. The upstream v2.0.0 unit has notify readiness, `Restart=on-failure`, and graphical-session coupling; this is contextual source, not proof of the installed package's effective unit/drop-ins. Do not assume every termination restarts it.
3. After DMS recovery, prove exactly one shell/plugin instance, restored Command Center/Shortcuts IPC, correct wallpaper, no stale modal/grab, and no surviving file-search child. Read back effective user units and process ownership through logout/watchdog crash/re-login, including a persistent user manager and two same-user graphical sessions. Multiple requests for the same systemd unit are not themselves evidence of duplicate processes.
4. Missing/wrong-version `start-hyprland`, DMS/Dux, generated Lua API and external user units are dependency/version gates: the repository delegates to package content and existing generated config. Verify the exact installed package set, executable availability and generated config compatibility; do not infer a missing package just because its implementation is not vendored.
5. Wallpaper hook intentionally reapplies the approved asset at each successful DMS start (`bin/wilsof-apply-wallpaper:29–31`). Clarify whether personal wallpaper selection should survive crash/re-login; current source implements forced-approved-wallpaper policy, not a proved violation of an agreed preservation policy.
6. Actual shortcut reload/dispatch and reset behavior, appearance updates while DMS owns the settings file, ReGreet candidate completeness/rendering/PAM, physical Super/F1 routing, GPU, multi-monitor/hotplug and suspend/resume remain untested. No workaround should bypass the AS-02 lock-state blocker.

Primary contextual references retrieved 2026-11-02: Dux [v2.0.0 service](https://github.com/duxlabs-dev/dux-shell/blob/v2.0.0/assets/systemd/dms.service), [generated Hyprland base](https://github.com/duxlabs-dev/dux-shell/blob/v2.0.0/core/internal/config/embedded/hyprland.lua), and [systemd dependency contract](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html). Moving documentation is not immutable installed-image provenance.

## 5. Previously documented defects

- R1 remains open: historical DMS UI SIGKILL/status 137 and automatic restart, killer/root cause unknown. R2 remains open: historical `hyprland-dialog`/libhyprtoolkit CWaylandBuffer crash while presenting an unresponsive-app dialog. R2 is not a Hyprlock crash. Evidence read: `docs/qa/2026-10-28-internal2-acceptance.json:159–165`, `docs/qa/2026-10-29-wallpaper-follow-up.md:7–17`, and `docs/qa/2026-10-30-internal3-e2-recovery.json:66–69`. These are historical reports, not newly inspected guest journals/coredumps or new reproductions.
- Integration2 closeout explicitly retains R1/R2 and physical gates (`2026-11-01-integration2-final-closeout.md:75–83`). The wallpaper post-hook is not a root-cause fix for either crash.
- #48's IS-01/IS-02 corrections are retained; installer safety is not reopened by this review. #49 reports AS-01 fixed in payload fixtures and AS-03 guarded with native lifetime/session assumptions still unverified. **AS-02 remains BLOCKED**, including normal unlock/shell-state resynchronization (`2026-11-02-auth-session-remediation-2.md:8–12,61–67`). No AS-02 implementation or remediation was attempted.

## 6. Executed tests and evidence

At exact #49 head, no new dependencies:

    PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider --basetemp=FRESH_SCRATCH       tests/test_desktop_runtime.py tests/test_session_start.py tests/test_hypr_config.py       tests/test_command_center.py tests/test_wallpaper_recovery.py tests/test_wallpaper_runtime.py       tests/test_lifecycle_fixture.py tests/test_profile_wallpaper_integration.py       tests/test_profile_deployment.py tests/test_appearance.py tests/test_user_shortcuts.py       tests/test_image_payload_contract.py tests/test_live_environment.py tests/test_live_recovery.py

Result: **74 passed, 1 skipped in 2.47s**, exit 0. The native wallpaper runtime gate was not authorized/enabled. Source/fixture passes are not native systemd, DMS, PAM, startup or rendered-UI acceptance.

Additional real-code scratch probes asserted all four findings; their six fixture scenarios and JSON results are retained privately in `wilsof-review3-20261102-probes.py` and `wilsof-review3-20261102-fixtures/results.json`. No probe is committed as implementation/test code. No dms/loginctl/hyprctl/systemctl service action was executed by these probes; generated-base fixture files avoid DMS setup. The lifecycle-fixture tests substitute their service/notify runner rather than activate real user units.

Focused ShellCheck of session/search/config-update/ReGreet wrappers and `git diff --check`: exit 0. One orchestration cell initially failed before any tool action because its kernel variable was absent; it was rerun with an explicit root. This was not a source/test failure. No full-suite or GitHub-CI-success claim is made.

## 7. Required corrections and verdict

Correct DI-01–03 and add upgrade/reset regressions; repair DI-04's conditional mode drift. Separately complete already authorized security work only under its own scope, and require authorized dynamic evidence for the lifecycle gates above. **NEEDS REMEDIATION**, not runtime acceptance, deployment permission, merge or release approval.

## 8. Publication and preservation

Only this report is staged/committed/pushed to the new review branch; no source branch is rewritten, merged or deleted. Exact remote branch and report bytes must be read back after push, with all pre-existing remote heads compared against the captured snapshot. The publication SHA/read-back receipt is kept outside this commit to avoid a self-reference loop. No PR, worker, scheduler or next review is started by this report.

Existing worktrees, ISOs and QA disks were not modified or used as fixtures. No new image-content hash audit is claimed. Only isolated scratch clone/probe/test/report files were written. Automation controls were not altered or re-certified.

## 9. Build, installation and hardware results

Not run: ISO build, QEMU, storage operations, installation, real login/lock/unlock, real service restart, firmware or physical-client tests. Historical Integration2 success is not transferred to the #48/#49 candidates or this review.

## 10. Agent/model budget

One review agent, no delegated agent or auxiliary coding CLI. Twelve bounded tool rounds including publication/read-back; no background worker or scheduler activation. Session model/provider: gpt-6.1-sol/openai-codex. Actual billing/token cost unavailable.

## 11. Process, storage and checkpoint

All review/test commands are synchronous, with scratch-scoped fixture execution. No VM/builder/service lifecycle was started and no project execution lock was acquired or released. Available scratch-filesystem space at 2026-11-02T09:51:56.225318+00:00: **64120709120 bytes**. Local scratch evidence is retained; it is not a durable substitute for the committed report.

## 12. Stop condition

Review 3/5 only. Stop after report publication and exact read-back. Do not begin remediation, deployment, merge/release or Review 4 automatically. Next safe action is owner prioritization of these findings and separate authorization of corrective work/dynamic tests.
