# Integration2 — Independent Review 2/5: Authentication and Session Security

Verdict: **NEEDS REMEDIATION**. Date: 2026-11-02 UTC. Independent, report-only review; no remediation performed.

## 1. Baseline, scope and lifecycle

Reviewed source: draft PR #48, `fix/installer-safety-20261101` at `26cf38457efb170d587bd6e1f0b6f353c92fab5c`. Its ancestry includes Integration2 branch `feat/integration-20261101` at `0abf4a51af2338f14c691c2d325d6abfa2c8a410` and stacked #41–47. All those heads were inspected through Git history/PR metadata; source inspection concentrated on the cumulative tree. Integration2 ISO's historical source is `b755bfabf82ece67eea3d666ea94330ff95f738e`, not #48. Parallel branches #38–40 were not silently substituted for this tree.

Traced: live preparation → temporary recovery account → greetd initial live session; installed account/password creation → root-owned greetd configuration → tuigreet/PAM → `wilsof-session` → packaged `start-hyprland` → user DMS/Hypridle units → manual/idle/suspend lock → Command Center focus protection → locker exit and logout/recovery. Read relevant prior acceptance, security, installer review and remediation reports; historical GUI observations are not new verification.

No source modifications, ISO build, QEMU, physical storage operations, authentication changes, dependency installation, scheduler/worker activation, merge or release. Only this report is committed on a new review branch. Harmless fixtures and retrieved upstream text remain outside the repository.

## 2. Findings and exact corrections

**Critical: none demonstrated. High: none demonstrated.** This is bounded evidence, not certification that upstream authentication or session isolation is secure.

### AS-01 — Medium: fresh installed systems omit the three-minute lock executable

Locations: `config/hypr/hypridle.conf:12–17`; `runtime/desktop.py:60–63`; `runtime/image-files.txt` (explicit payload list omits `bin/wilsof-idle`); `runtime/provision-target:94–98`. The separate developer installer does copy it (`scripts/install-user-config.sh:56–58`), concealing the difference between developer deployment and fresh installation.

Verified reproduction: call the real `install_user(source, fresh_home)` with only a fixture generated `hyprland.lua` present. Result: installed idle config references `wilsof-idle`, but `fresh_home/.local/bin/wilsof-idle` does not exist, and the image manifest also excludes it. This directly establishes the missing installed command, not a timed compositor test. The unattended desktop therefore lacks the configured 180-second lock path; the independent 300-second `wilsof-lock` remains configured. No claim that all idle locking is disabled.

Correction: include `bin/wilsof-idle` in `runtime/image-files.txt` AND the executable deployment list in `runtime/desktop.py`. Add a fresh payload/provisioning regression asserting every Wilsof executable referenced by the deployed Hypridle configuration exists and is executable. Test the fresh installed path, not only the developer script or source strings.

### AS-02 — Medium: locker failure still emits an unlock request; lock requests are misdescribed as confirmed state

Locations: `bin/wilsof-lock:20–31`; `bin/wilsof-idle:29–39`; consumer `config/dms/plugins/wilsofCommandCenter/CommandCenter.qml:68–85,204–235`.

Verified with fake `hyprlock`, `loginctl`, `pgrep`, and `id` in an isolated PATH: for BOTH wrappers a locker exiting 23 produces `lock-session fixture-42 → hyprlock failed → unlock-session fixture-42`, and the wrapper returns 23. Returning failure is good, but sending unlock after failure is not evidence of authenticated unlock. Systemd's D-Bus contract distinguishes Lock/Unlock requests from the session's `SetLockedHint` state; the wrapper comments and prior report overstate what `loginctl lock-session` establishes. Hypridle's own Lock handler may launch `lock_cmd` again, so notification requests also feed back into the start path.

Impact: failed startup is not a successful lock. A failed competing locker must not request unlocking another lock or relax the F1 modal guard. No real compositor unlock, password disclosure, or PAM bypass was reproduced; Hyprland may retain a secure abandoned lock. Severity reflects the verified unsafe lifecycle transition, with graphical consequences still pending.

Correction: separate lock requests, pending/secured state, and authenticated completion. Use compositor lock confirmation and the appropriate logind state API for state reporting, with explicit failure handling. Do not issue `UnlockSession` unconditionally on nonzero exit, and do not assume exit 0 alone proves PAM success or lock acquisition. Keep keyboard-grabbing shell surfaces closed while lock status is uncertain. Add nonzero-exit, signal, concurrent-start and D-Bus-failure regressions; retain the real locker return code and show an actionable lock failure. Do not replace this with a blanket forced desktop unlock.

### AS-03 — Medium, conditional: deduplication is neither atomic nor scoped to the desktop session

Locations: `bin/wilsof-lock:15–17`; `bin/wilsof-idle:17–19`; simultaneous entrypoints in `config/hypr/hypridle.conf:8–9,16,24` and `config/hypr/wilsof.lua:55`.

Verified concurrency fixture: two wrapper processes pass a barrier-controlled fake `pgrep` before either launches the fake locker; both launch `hyprlock`, both return 0, and both send unlock requests. This proves the wrapper does not serialize starts, not that two real lockers can acquire the compositor lock. Separately, a mocked successful same-UID process match makes the wrapper return 0 without launching or confirming any lock. The real query selects UID/name only, not Wayland display or logind session: a locker on another simultaneous session can suppress locking this desktop. A same-user compromised process is already inside the desktop trust boundary; this is not cross-user privilege escalation.

Correction: share an atomic, per-session/per-display start guard across BOTH wrappers (private runtime directory; no predictable public temporary files). Confirm that the existing locker owns this compositor's secure lock before reporting success. Cover two same-UID graphical sessions and simultaneous manual/idle/suspend requests, including one rejected or crashed locker; ensure the losing request cannot emit an unlock for the winning one.

**Low:** no separate security defect demonstrated. Incomplete ReGreet provisioning and remaining hardening/validation gaps are recorded below rather than inflated into authentication-bypass findings.

## 3. Verified existing safeguards

- Installed provisioning writes only `[default_session]`, uses service identity `greeter`, and selects `tuigreet --time --cmd /usr/local/bin/wilsof-session`; it does NOT copy live `[initial_session]` autologin or live sudo policy (`runtime/provision-target:84–98`). `wilsof-session:2–17` uses exec and preserves greetd session ownership rather than invoking root/runuser as a login shortcut.
- Installer passwords use hidden double entry; empty/NUL/LF/mismatch are rejected; `GetPassWarning` becomes an error, preventing an echoing fallback. Passwords are absent from the canonical plan, and backend password-setting failure is checked (`installer/wilsof_installer.py:231–235,253–292,314–334`). Arbitrary backend exception text is not printed. Python-memory zeroization is explicitly not guaranteed; no end-to-end backend log secrecy is claimed.
- #48 rejects reserved service identities through a shared policy before confirmation, and target provisioning requires a non-root UID >=1000 with the expected dedicated home (`installer/accounts.py`; `runtime/provision-target:18–43`). Desktop provisioning runs as that user, not root (`:94–98`; `runtime/desktop.py:175–177`).
- F1 guard exists: close Command Center and the already-loaded shortcut editor on session-lock notification; refuse ordinary open/toggle/search while `SessionService.locked`; treat the locked IPC marker as handled without Spotlight fallback (`CommandCenter.qml:68–85,204–235`; `bin/wilsof-search:15–22`). This verifies implementation, not every focus/order/crash interleaving. Existing regression checks mostly inspect strings, not Qt/Wayland ownership.
- Hypridle explicitly sets `inhibit_sleep = 3`; normal and idle lock presentations use Hyprlock rather than a fake unlocked screensaver, with immediate rendering and no desktop-capture fades (`config/hypr/hypridle.conf:2–10`; `hyprlock.conf:4–17`; `hyprlock-idle.conf:6–20`). Upstream source actually listens for compositor lock confirmation; configuration alone cannot guarantee suspend ordering.
- Live is explicitly public/unlocked: root password locked in generated shadow, live-only autologin and constrained named sudo commands, runtime-generated recovery password passed to `chpasswd` on stdin. The password is deliberately public in mode-0644 `/etc/issue`; this is NOT secret protection and must never be reused on installed systems (`scripts/prepare-iso.py:87–101,119`; `runtime/live-console-setup:14–27`; `runtime/desktop.py:119–121,148–166`).
- Managed desktop writes use exclusive temporary creation, replace, symlink refusal and per-file backups; no password is written by that path (`runtime/desktop.py:21–53`). No repository-owned PAM stack or custom polkit authorization rule was found. Absence of a custom rule is not proof that effective package policy is safe.

## 4. Dynamic tests and upstream/package boundaries still required

1. **F1/password routing:** test opening/closing Command Center and lazily loaded Shortcuts/About while locking; DMS restart during an already-secured lock; absent/stale `XDG_SESSION_ID`; missing/disabled logind integration; failed DMS IPC/Spotlight fallback. Loader `onLoaded: item.open()` is unguarded and `activate()` lacks its own lock check (`CommandCenter.qml:94–155,240–251`). These are race candidates, NOT a newly demonstrated password leak. Require zero synthetic secret characters in query/status/search-process argv, shell logs and underlying apps.
2. **Locker and suspend faults:** real startup failure, SIGTERM/SIGKILL, wrong password, PAM unavailable/locked account, repeat requests, inhibitors, actual 180/300/600-second timing, session lock notifier missing, suspend/resume, hotplug and multiple outputs/seats. Delay inhibitors are not an unlimited guarantee. Historical TCG suspend hung; no physical acceptance is inherited from that report (`2026-10-31-accept-completion-session.md:44–50`).
3. **Effective PAM:** read and verify the exact built/installed `/etc/pam.d/{greetd,hyprlock,login,system-local-login,system-login,system-auth}`, their includes, account/session restrictions, null-password policy, faillock/rate limits, and actual package versions/checksums. Upstream Hyprlock's supplied file contains `auth include login`; this does NOT independently establish the effective Arch stack or full account policy. Current primary source was read, not assumed trustworthy; no installed PAM files were mounted/read here.
4. **Privileges/polkit:** verify actual archinstall 4.5 `User(..., True)` administrator/wheel policy, generated sudoers syntax/argument matching, root account state, effective package polkit rules and agent startup, behavior while locked/inactive, and cached authorization. Do not certify these from mocks or `polkit-gnome` merely being in the package manifest. Exact backend source retrieval was unavailable at the attempted upstream tag paths; its password/logging behavior remains unverified here.
5. **ReGreet:** the wrapper runs cage as the greeter and adds no authentication. However the fresh ISO/installed package manifest lists tuigreet, not `greetd-regreet`/`cage`, and canonical provisioning does not install its wrapper/config/assets (`runtime/desktop-packages.txt:1–7`; `runtime/provision-target:79–98`; compare legacy `scripts/install-arch-test-vm.sh:60–77`). The historical one-line opt-in claim does not hold for the canonical fresh path. Before advertising/enabling it, distribute all candidate files/packages together, keep `user = "greeter"`, and test failed/successful PAM submissions, crash/recovery, VT switching and logout. Do not flip the verified tuigreet default during this review.
6. **Logout/recovery/secrets:** test a real logout returns to authenticated greetd with user targets/processes stopped, no old desktop/VT accessible, and clean re-login after compositor/watchdog crashes. Audit exact backend logs/tempfiles, coredumps, sudo I/O recording and external QA transcripts with synthetic secrets and restricted permissions; no known password was sought or published. Closeout's prior transcript cleanup is historical, not forensic erasure or proof of future non-exposure (`2026-11-01-integration2-final-closeout.md:33`).

Corrections above are recommendations only. No live PAM/sudo/polkit/greeter/locker configuration was changed.

## 5. Executed evidence and limitations

At source `26cf38457efb170d587bd6e1f0b6f353c92fab5c`:

    PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider       tests/test_scripts.py tests/test_command_center.py tests/test_desktop_runtime.py       tests/test_session_start.py tests/test_hypr_config.py tests/test_live_recovery.py       tests/test_installer_runtime.py tests/test_installer_safety.py       tests/test_image_payload_contract.py

Result: **180 passed in 1.56s**, exit 0. Focused ShellCheck for `bin/wilsof-{lock,idle,session,search}` and `config/greetd/wilsof-regreet`: exit 0. `git diff --check`: exit 0. Additional fixture reproductions: AS-01 missing deployment; both AS-02 nonzero locker exits; AS-03 same-UID match and synchronized double start. All session/system commands in those reproductions were substitutes; no real lock, authentication, system service or storage operation ran. No new source/test file is committed. A passing suite does not negate these untested deployment/failure cases.

Primary references retrieved 2026-11-02: [systemd logind D-Bus contract](https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html), [Hypridle v0.1.8 implementation](https://github.com/hyprwm/hypridle/blob/v0.1.8/src/core/Hypridle.cpp), [Dux v2.0.0 SessionService](https://github.com/duxlabs-dev/dux-shell/blob/v2.0.0/quickshell/Services/SessionService.qml), [Hyprlock supplied PAM file](https://github.com/hyprwm/hyprlock/blob/main/pam/hyprlock). Dux source consumes asynchronously reported `state.locked`; no synchronous modal-closure handshake is present in the Wilsof wrappers. The moving upstream PAM reference is contextual, not immutable image provenance or a security attestation.

## 6. Publication, preservation and remaining gates

Report-only branch: `review/auth-session-security-20261102`, based on #48; no PR, merge, release, automatic issue closure, worker or Review 3 is requested. Before push, verify the only new commit path is this report and all source blobs remain identical to the reviewed SHA. After push, read back the exact remote branch and report blob, and compare all pre-existing remote branch heads with the captured starting snapshot. Publication commit/read-back receipt belongs in the terminal result to avoid a self-referential commit loop. No GitHub CI-success claim is made.

ISO/build/installation/boot/password-login results for THIS review: **not performed**. Existing ISO files and QA disks were neither opened as fixtures nor modified; no fresh artifact hash audit or runtime acceptance is claimed. Only an isolated scratch clone and report branch were written; existing worktrees/branches remain untouched by our commands. Automation controls were not altered or re-certified. No project execution lock was required for this report-only isolated review.

One review agent, no delegated/paid auxiliary agent; maximum twelve review tool rounds including publication. Session model/provider: gpt-6.1-sol/openai-codex. Actual billed cost unavailable.

**NEEDS REMEDIATION:** fix AS-01–03 and add failure/deployment regressions before treating this review as passed; separately authorize runtime/physical checks. Physical keyboard routing, genuine password unlock, suspend/resume, multi-monitor and recovery remain pending. Stop after publishing Review 2/5; do not begin remediation or Review 3.
