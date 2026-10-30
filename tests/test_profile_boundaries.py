"""Boundary and deployment-independence checks; no compositor is required."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import pytest
from test_profile import CLI, invoke, seed, state_file


def test_runtime_has_no_network_process_or_desktop_dependency():
    tree = ast.parse(CLI.read_text())
    imports = {node.names[0].name.split('.')[0] for node in ast.walk(tree)
               if isinstance(node, ast.Import)}
    imports |= {node.module.split('.')[0] for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module}
    assert imports <= {'argparse', 'contextlib', 'fcntl', 'json', 'os', 'pathlib',
                       'secrets', 'stat', 'sys', 'time'}
    calls = {node.func.attr for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert not calls & {'system', 'popen', 'fork', 'execv', 'execve', 'spawnv'}


def test_copied_executable_works_without_repository_or_graphics(tmp_path):
    home = tmp_path / 'home'
    home.mkdir()
    executable = tmp_path / 'wilsof-profile'
    shutil.copyfile(CLI, executable)
    executable.chmod(0o755)
    env = {'HOME': str(home), 'PATH': os.path.dirname(sys.executable) + ':/usr/bin:/bin'}
    for args, expected in [(('set', 'development'), 'development\n'),
                           (('get',), 'development\n')]:
        result = subprocess.run([str(executable), *args], env=env, cwd=tmp_path,
                                capture_output=True, text=True, timeout=5)
        assert (result.returncode, result.stdout, result.stderr) == (0, expected, '')


def test_private_modes_with_permissive_umask(tmp_path):
    result = subprocess.run([sys.executable, str(CLI), 'set', 'study'],
                            env=os.environ | {'HOME': str(tmp_path)}, umask=0,
                            capture_output=True, text=True, timeout=5)
    assert result.returncode == 0
    path = state_file(tmp_path)
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700
    assert (path.parent / '.profile.lock').stat().st_mode & 0o777 == 0o600


def test_existing_legacy_state_directory_is_tightened_only_on_set(tmp_path):
    path = seed(tmp_path, b'{"schema_version":1,"profile":"study"}')
    path.parent.chmod(0o755)
    assert invoke(tmp_path, 'get').returncode == 0
    assert path.parent.stat().st_mode & 0o777 == 0o755
    assert invoke(tmp_path, 'set', 'everyday').returncode == 0
    assert path.parent.stat().st_mode & 0o777 == 0o700


@pytest.mark.parametrize('relative', ['.local', '.local/state', '.local/state/wilsof-os'])
def test_group_writable_directory_is_refused_not_silently_chmodded(tmp_path, relative):
    path = seed(tmp_path, b'{"schema_version":1,"profile":"study"}')
    unsafe = tmp_path / relative
    unsafe.chmod(0o775)
    raw = path.read_bytes()
    assert invoke(tmp_path, 'get').returncode == 1
    assert invoke(tmp_path, 'set', 'clean').returncode == 1
    assert unsafe.stat().st_mode & 0o777 == 0o775
    assert path.read_bytes() == raw


@pytest.mark.parametrize('home', ['relative', '/bad/../home'])
def test_invalid_home_is_reported_without_writes(home):
    result = invoke(Path(home), 'get')
    assert result.returncode == 1
    assert result.stdout == 'clean\n'
    assert 'HOME must be' in result.stderr


def test_deeply_nested_json_is_bounded_and_preserved(tmp_path):
    raw = b'[' * 1500 + b']' * 1500
    path = seed(tmp_path, raw)
    assert invoke(tmp_path, 'get').returncode == 1
    assert invoke(tmp_path, 'set', 'clean').returncode == 1
    assert path.read_bytes() == raw


def test_unknown_future_schema_is_never_downgraded(tmp_path):
    raw = b'{"schema_version":99,"profile":"study"}'
    path = seed(tmp_path, raw)
    assert invoke(tmp_path, 'get').stdout == 'clean\n'
    assert invoke(tmp_path, 'set', 'clean').returncode == 1
    assert path.read_bytes() == raw


def test_live_reader_observes_only_complete_json_during_competing_writes(tmp_path):
    assert invoke(tmp_path, 'set', 'clean').returncode == 0
    writers = [subprocess.Popen([sys.executable, '-B', str(CLI), 'set', profile],
                                env=os.environ | {'HOME': str(tmp_path)},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
               for profile in ('study', 'development', 'everyday') * 4]
    observed = 0
    deadline = time.monotonic() + 10
    try:
        while any(p.poll() is None for p in writers):
            assert time.monotonic() < deadline, 'competing writers did not finish'
            data = json.loads(state_file(tmp_path).read_bytes())
            assert set(data) == {'schema_version', 'profile'}
            assert data['profile'] in ('clean', 'study', 'development', 'everyday')
            observed += 1
        for process in writers:
            out, err = process.communicate(timeout=5)
            assert process.returncode == 0, (out, err)
        assert observed > 0
        # Unordered launches have no profile priority. This final serialized
        # commit provides a deterministic result after all contenders complete.
        assert invoke(tmp_path, 'set', 'clean').returncode == 0
        assert invoke(tmp_path, 'get').stdout == 'clean\n'
    finally:
        for process in writers:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)
