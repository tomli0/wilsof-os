"""Exercise the actual launcher model in JS, not a duplicate Python model."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'config/dms/plugins/wilsofProfiles'


def test_launcher_model_filters_four_profiles_and_never_marks_saved_only_active():
    model = PLUGIN / 'Profiles.js'
    assert model.is_file(), 'DMS profile model missing'
    node = shutil.which('node')
    if not node:
        pytest.skip('Node required for the real launcher JS model')
    script = r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const c = {}; vm.createContext(c);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8').replace(/^\.pragma library\s*/, ''), c);
const confirmed = {saved:'study',applied:'study',error:null};
const pending = {saved:'study',applied:null,error:'IPC unavailable'};
let items = c.items('', confirmed);
assert.deepStrictEqual(Array.from(items, x=>x.action), ['clean','study','development','everyday']);
assert.equal(items.filter(x=>x.comment.includes('Aktiv')).length, 1);
assert.equal(c.items('profil',confirmed).length,4);
assert.equal(c.items('dev',confirmed)[0].action,'development');
assert.equal(c.items('nonsense',confirmed).length,0);
assert.equal(c.items('',pending).filter(x=>x.comment.includes('Aktiv')).length,0);
assert(c.items('',pending).every(x=>x.comment.includes('IPC unavailable')));
assert(c.label(pending).includes('?'));
assert.equal(c.label(confirmed),'STUDY');
assert(!c.valid('study;touch nope')); assert(c.valid('clean'));
console.log('launcher model assertions passed');
'''
    result = subprocess.run([node, '-e', script, str(model)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_composite_manifest_has_both_real_surfaces_and_no_daemon():
    path = PLUGIN / 'plugin.json'
    assert path.is_file(), 'DMS plugin manifest missing'
    manifest = json.loads(path.read_text())
    assert manifest['id'] == 'wilsofProfiles'
    assert set(manifest['components']) == {'launcher', 'widget'}
    assert manifest['trigger'] == ''
    for name in manifest['components'].values():
        assert (PLUGIN / name).is_file()
