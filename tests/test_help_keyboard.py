"""The compositor can give keybinding children a TTY on stdin."""
import os
from pathlib import Path
import pty
import signal
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_help_keybinding_renders_without_reading_inherited_terminal(tmp_path):
    commands = tmp_path / 'bin'
    commands.mkdir()
    dms = commands / 'dms'
    dms.write_text('#!/bin/sh\nprintf "%s\\n" NOTEPAD_OPEN_FILE_SUCCESS\n')
    dms.chmod(0o755)
    document = tmp_path / 'shortcut-help.txt'
    env = os.environ | {
        'HOME': str(tmp_path), 'PATH': str(commands) + ':' + os.environ['PATH'],
        'WILSOF_SHORTCUTS_FILE': str(ROOT / 'config/wilsof-shortcuts.json'),
        'WILSOF_HELP_VIEWER': str(ROOT / 'bin/wilsof-help-view'),
        'WILSOF_HELP_DOCUMENT': str(document),
    }
    master, slave = pty.openpty()
    child = subprocess.Popen([str(ROOT / 'bin/wilsof-help')], stdin=slave,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, start_new_session=True)
    os.close(slave)
    try:
        try:
            out, err = child.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            raise AssertionError('Help keybinding blocked on inherited TTY before opening Notepad')
        assert child.returncode == 0, err.decode()
        assert b'NOTEPAD_OPEN_FILE_SUCCESS' in out
        assert 'Super+F1' in document.read_text()
        assert 'Trykk Enter' not in document.read_text()
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            child.communicate(timeout=3)
        os.close(master)
