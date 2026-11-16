# Session-command QA boundary

`session_command.py` constructs the QGA shell payload for a known disposable
user/session. Its caller must verify the guest, user/UID and resource ownership.
It does not launch QEMU, authenticate a login or change any desktop shortcut.

The 2026-11-07 shortcut read-back failure was reproduced offline with real
systemd user services: a single Bash command argument beginning with `$HOME/`
was removed by systemd's default environment expansion. Bash then received
`-lc` without an operand and exited 2. Outer-shell quoting was intact.

Use `user_command(command, username=..., uid=...)` from this helper instead of
hand-building that chain. `--expand-environment=no` leaves expansion to the
inner Bash, using the session manager's environment. Do not replace `$HOME`
with a guessed physical user's path or modify production shortcuts to fix QA.

Run the deterministic argv/environment fixture:

    python3 -m pytest tests/test_session_command.py -q

Optional real, bounded user-manager boundary check (no VM, root or packages):

    WILSOF_NATIVE_SYSTEMD_ARGV=1 python3 -m pytest tests/test_session_command.py -q

The native check expects Bash to attempt an intentionally nonexistent executable
(exit 127). It must not fail with Bash's missing `-c` argument (exit 2).
This diagnoses the oracle; it does not accept keyboard capture, persisted
bindings or any other guest UI behavior. Those require a new owned guest test.

Upstream reference: systemd's `systemd-run(1)`, `--expand-environment=` option.
