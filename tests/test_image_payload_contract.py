"""The live ISO payload must contain every source file desktop.py consumes."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = (ROOT / 'runtime' / 'desktop.py').read_text(encoding='utf-8')
MANIFEST = (ROOT / 'runtime' / 'image-files.txt').read_text(encoding='utf-8').splitlines()


def test_every_deployed_binary_is_in_the_iso_payload():
    listing = re.search(r"for name in \(([^)]*wilsof-search[^)]*)\):", DESKTOP).group(1)
    for name in re.findall(r"'([^']+)'", listing):
        assert f'bin/{name}' in MANIFEST, f'bin/{name} deployed by desktop.py but missing from image-files.txt'


def test_every_share_origin_is_in_the_iso_payload():
    block = DESKTOP[DESKTOP.find('for name, origin in'):]
    block = block[:block.find('):')]
    for origin in re.findall(r"'(config/[^']+)'", block):
        assert origin in MANIFEST, f'{origin} deployed by desktop.py but missing from image-files.txt'


def test_every_deployed_hypr_config_is_in_the_iso_payload():
    line = [l for l in DESKTOP.splitlines() if l.strip().startswith('for name in') and 'wilsof.lua' in l][0]
    for name in re.findall(r"'([^']+)'", line):
        assert f'config/hypr/{name}' in MANIFEST, f'config/hypr/{name} missing from image-files.txt'
