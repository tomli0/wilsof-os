"""About data must report installed identity, never the development checkout HEAD."""
import importlib.machinery
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module():
    path = ROOT / 'bin/wilsof-about-info'
    assert path.exists(), 'About information helper is missing'
    loader = importlib.machinery.SourceFileLoader('wilsof_about', str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def test_about_reports_exact_installed_source_and_unknown_version_honestly(tmp_path):
    p = tmp_path / 'usr/share/wilsof/source/SOURCE_COMMIT'
    p.parent.mkdir(parents=True)
    p.write_text('a' * 40 + '\n')
    info = module().collect(tmp_path)
    assert info['sourceCommit'] == 'a' * 40
    assert info['version'] == 'Development snapshot'
    assert info['dedication'] == 'Dedicated to William and Sofie.'
    assert info['github'] == 'https://github.com/tomli0/wilsof-os'
    assert info['website'] == ''  # The repository does not declare an official website.
    assert 'No project-wide license' in info['license']
    p.write_text('not-a-commit\n')
    assert module().collect(tmp_path)['sourceCommit'] == 'Unavailable'


def test_about_is_a_real_native_modal_and_is_distributed():
    plugin = ROOT / 'config/dms/plugins/wilsofCommandCenter'
    assert (plugin / 'About.qml').exists(), 'About modal missing'
    text = (plugin / 'About.qml').read_text()
    for value in ['DModal {', 'wilsof-about-info', 'Dedicated to William and Sofie.', 'System', 'Upstream', 'License', 'GitHub']:
        assert value in text
    assert 'aboutLoader.item.open()' in (plugin / 'CommandCenter.qml').read_text()
    assert 'About.qml' in (ROOT / 'runtime/image-files.txt').read_text()
