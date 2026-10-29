# Milestone A — Hypridle regression, 2026-10-28

Authorized continuation of #31; no package rebuild. Source baseline 2015a534383a3a7272a72eb1299fd9aecf82216a.

## Verified

- Recovered newest private checkpoint, live processes, worktrees, worker lock and GitHub #16/#27/#30/#31/#32/#33. No pre-existing guest/build. Scheduler disabled/paused; automatic worker paused throughout.
- Current parent billing: openai-codex / subscription_included, gpt-6.1-sol, ChatGPT auth. Auxiliary routes pinned to Codex with empty fallback chains. No configuration changed or paid model contacted; OpenRouter financial controls not verified, hence no paid fallback permitted.
- Exact already-built hypridle 0.1.8-2.1 package SHA256 `3182ffaa24b0382c39614c460e15f90ff730d7da4f60378123d9b3df09c01d04` reverified. Executable SHA256 `3b5b36e21cb88e2939ed42f5d1a87c8b05f3c95876703545dd74dd280ee7fdd9` matches the running guest process.
- The actual portable entry point `packaging/hypridle/verification/run-regression.py` ran against the preserved patched source: 14/14 normal, 14/14 UBSan. Compile and runner exit0; every injected disconnect/error exits1 with worker joined before main-thread cleanup. EINTR, both DBus descriptors, Wayland dispatch, exception unwinding, conditions/retries and POLLERR/POLLNVAL checked. Earlier TSAN mapping failures remain NOT PASSED; TSAN not repeated.
- One new disposable overlay above the preserved diagnostic image. No original disk modified. Native package installed by pacman, no rebuild. Ordinary greeter password login starts Hyprland and the exact packaged Hypridle, active with zero restarts.
- Real compositor exit via `hyprctl eval 'hl.dispatch(hl.dsp.exit())'`: PID852 logs Wayland pollfd1 disconnect at 08:53:38.925 UTC, catches the error, exits code1 (not SIGABRT), no Hypridle core. Compositor and original idle process disappear; greeter returns. The IPC client timed out during cold TCG processing; later journal/process/greeter evidence, not its return code, establishes teardown. An earlier invalid dispatcher-call probe made no state change and is not counted as a pass.
- Second ordinary password login starts fresh Hyprland PID1735 and Hypridle PID1797, active/running, zero restarts. Guest powerdown through QGA completed; exact QEMU67997 exited, supervisor released lock. Offline overlay check exit0.

## Explicit limitations / severity decision

The packaged service retains upstream Restart=on-failure. After compositor disconnect it made six failed connection attempts before the old user manager exited. Dux likewise restarted against the gone Wayland socket; its restarted Quickshell PID1345 aborted in Qt platform initialization. This is preserved teardown-only evidence, not a Hypridle core or a crash of the new authenticated session. Fresh login recovered both services normally. These bounded teardown diagnostics do not block an internal test candidate, but #31 remains OPEN for cold TCG lock latency/upstream lifecycle follow-up and final-ISO locking tests. No physical-hardware acceptance or blanket crash-free claim.

## Durable evidence

Private directory `/home/tommy_ai/.local/state/wilsof-qa/session-20261028/`:

- `regression/patched-normal.log`, `regression/patched-ubsan.log` and exact generated C++;
- `milestone-a-vm/02-install-existing-package.json`, `06-idle-readiness.json`, `08-pre-teardown.json`, `14-final-teardown-journal.json`, `15-unit-and-crash-context.json`, `16-second-login-idle-health.json`, `18-offline-after-shutdown.json`;
- screenshots, VM argv/PIDs, lock ownership, firmware and new overlay preserved privately. No passwords, disks or raw cores in Git.

Next authorized milestone: one versioned internal ISO including #30 and this exact native package, with installer safety checks and actual-artifact acceptance. No merge, release, physical disk/USB or Proxmox changes.
