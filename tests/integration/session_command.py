"""QGA shell payload for an ordinary user's real systemd session environment.

This is QA infrastructure, not a desktop shortcut implementation. The caller
owns guest identity/lifetime and the QGA transport; this helper never starts a VM.
"""
import shlex


def user_command(command, *, username, uid):
    """Return one shell payload; preserve the inner command as a single argument."""
    return shlex.join([
        'runuser', '-u', username, '--', 'env',
        f'XDG_RUNTIME_DIR=/run/user/{uid}',
        f'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus',
        # The command is Bash syntax, not a systemd environment expression.
        # With expansion enabled a whole $HOME-prefixed argument can disappear
        # before Bash receives it, even though the outer shell quoted it.
        'systemd-run', '--user', '--quiet', '--collect', '--wait', '--pipe',
        '--expand-environment=no',
        '--', '/bin/bash', '-lc', command,
    ])
