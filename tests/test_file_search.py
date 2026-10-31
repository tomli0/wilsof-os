import importlib.machinery
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def helper():
    path = ROOT / 'bin/wilsof-file-search'
    assert path.exists(), 'bounded home-name search is not implemented'
    loader = importlib.machinery.SourceFileLoader('file_search', str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_home_names_search_excludes_generated_trees_and_symlink_escape(tmp_path):
    home = tmp_path / 'home'
    home.mkdir()
    for folder in ['Downloads', 'Documents', '.cache', '.local/share/Trash', '.git', 'node_modules', 'build', '.config']:
        p = home / folder
        p.mkdir(parents=True, exist_ok=True)
        (p / 'needle.txt').touch()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'needle-secret').touch()
    (home / 'escape').symlink_to(outside, target_is_directory=True)
    result = helper().search(home, 'needle', budget_ms=1000)
    assert {r['path'] for r in result['items']} == {str(home / 'Downloads/needle.txt'), str(home / 'Documents/needle.txt')}
    assert helper().search(home, 'downloads')['items'][0]['path'] == str(home / 'Downloads')
    assert result['truncated'] is False


def test_bounded_search_and_literal_names(tmp_path):
    (tmp_path / '$(touch pwned); note.txt').touch()
    m = helper()
    assert m.search(tmp_path, '$(touch')['items'][0]['path'].endswith('$(touch pwned); note.txt')
    assert m.search(tmp_path, '', max_entries=0)['truncated'] is True
    assert m.search(tmp_path, 'x', budget_ms=0)['truncated'] is True
    assert not (tmp_path / 'pwned').exists()
