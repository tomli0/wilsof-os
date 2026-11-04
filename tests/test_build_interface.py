"""Invoke real wrapper/docs in a sanitized environment, never real build tools."""
import json
from pathlib import Path
import re
import subprocess

import pytest
from build_fixture import ROOT, layout


@pytest.mark.parametrize('bad', ['missing-upstream', 'missing-package', 'file-output', 'dangling-output', 'input-output-nesting', 'canonical-root', 'bad-epoch', 'bad-version', 'file-parent', 'symlink-releng-file', 'reserved-provenance'])
def test_invalid_inputs_fail_before_any_build_output_is_created(tmp_path, bad):
    source, upstream, package, env = layout(tmp_path)
    out = Path(env['WILSOF_ISO_OUTDIR'])
    if bad == 'missing-upstream':
        (upstream / 'packages.x86_64').unlink()
    elif bad == 'missing-package':
        package.unlink()
    elif bad == 'file-output':
        out.write_text('historical sentinel')
    elif bad == 'dangling-output':
        out.symlink_to(tmp_path / 'absent')
    elif bad == 'input-output-nesting':
        out = source / 'new-output'
        env['WILSOF_ISO_OUTDIR'] = str(out)
    elif bad == 'canonical-root':
        env['WILSOF_ISO_WORKDIR'] = '/unused/..'
    elif bad == 'file-parent':
        parent = tmp_path / 'regular-file'; parent.write_text('sentinel')
        env['WILSOF_ISO_WORKDIR'] = str(parent / 'work')
    elif bad == 'symlink-releng-file':
        config = upstream / 'pacman.conf'; config.unlink(); config.symlink_to(package)
    elif bad == 'reserved-provenance':
        (upstream / 'BUILD-SOURCE.json').symlink_to(package)
    elif bad == 'bad-epoch':
        env['SOURCE_DATE_EPOCH'] = 'tomorrow'
    elif bad == 'bad-version':
        env['WILSOF_ISO_VERSION'] = '../unsafe'
    result = subprocess.run(['sh', str(source / 'scripts/build-iso.sh'), '--build'], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert not Path(env['CAPTURE']).exists()
    assert not Path(str(env['WILSOF_ISO_WORKDIR']) + '-profile').exists()
    if bad not in ('file-output', 'dangling-output'):
        assert not out.exists(), result.stderr
    if bad == 'file-output':
        assert out.read_text() == 'historical sentinel'
    if bad == 'dangling-output':
        assert out.is_symlink() and not out.resolve().exists()


def test_isolated_valid_layout_reaches_only_substituted_builder(tmp_path):
    source, _, _, env = layout(tmp_path)
    result = subprocess.run(['sh', str(source / 'scripts/build-iso.sh'), '--build'], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(Path(env['CAPTURE']).read_text()) == ['-v', '-w', env['WILSOF_ISO_WORKDIR'], '-o', env['WILSOF_ISO_OUTDIR'], env['WILSOF_ISO_WORKDIR'] + '-profile']


def test_documented_archive_and_sudo_command_supplies_all_required_inputs(tmp_path):
    source, _, package, env = layout(tmp_path)
    (source / 'SOURCE_COMMIT').unlink()
    for args in (['init', '-q'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture']):
        subprocess.run(['git', *args], cwd=source, check=True, capture_output=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    env.pop('WILSOF_SOURCE_COMMIT')
    env.update(WILSOF_APPROVED_COMMIT=commit, WILSOF_EXPORT_ROOT=str(tmp_path / 'export'), WILSOF_HYPRIDLE_PACKAGE=str(package))
    doc = (ROOT / 'docs/iso.md').read_text()
    match = re.search(r'<!-- build-command:start -->\n(.*?)<!-- build-command:end -->', doc, re.S)
    # Execute the original displayed invocation for genuine RED evidence.
    command = match[1] if match else next(line.strip() for line in doc.splitlines() if line.strip().startswith('sudo WILSOF_ISO_WORKDIR='))
    result = subprocess.run(['sh', '-eu', '-c', command], cwd=source, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert Path(env['CAPTURE']).exists(), 'Documented command must reach substituted mkarchiso'
    assert (Path(env['WILSOF_EXPORT_ROOT']) / 'SOURCE_COMMIT').read_text().strip() == commit
