"""Execute the same model used by the DMS modal (no UI reimplementation)."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'config/dms/plugins/wilsofCommandCenter/Model.js'


def evaluate(expression):
    script = "const fs=require('fs'),vm=require('vm'); const m={}; vm.createContext(m); vm.runInContext(fs.readFileSync(process.argv[1],'utf8').replace('.pragma library',''),m); console.log(JSON.stringify(" + expression + "));"
    result = subprocess.run(['node', '-e', script, str(MODEL)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_default_view_has_three_shortcuts_then_seven_shallow_categories():
    assert MODEL.exists(), 'Command Center model is not implemented'
    rows = evaluate('m.defaults()')
    assert [r['name'] for r in rows[:3]] == ['Browser', 'Terminal', 'Files']
    assert [r['name'] for r in rows[3:]] == ['Applications', 'Files & Folders', 'Settings', 'Appearance', 'Help & Shortcuts', 'About Wilsof OS', 'Power']
    assert len({r['id'] for r in rows}) == len(rows)


def test_selection_survives_async_results_and_cannot_activate_another_row():
    assert evaluate('m.selection([{id:"a"},{id:"b"}], "b")') == 1
    assert evaluate('m.selection([{id:"c"}], "b")') == 0
    assert evaluate('m.selection([], "b")') == -1
    assert evaluate('m.move(0,-1,3)') == 2
    assert evaluate('m.move(2,1,3)') == 0
    assert evaluate('m.move(-1,1,0)') == -1


def test_plain_queries_find_shortcuts_settings_and_lock_without_prefixes():
    assert evaluate('m.commands("terminal").map(r=>r.id)') == ['terminal']
    assert evaluate('m.commands("display").map(r=>r.id)') == ['settings']
    assert evaluate('m.commands("lock").map(r=>r.id)') == ['power', 'lock']
    assert evaluate('m.commands("nonsense-427").length') == 0


def test_native_dms_modal_distribution_and_safe_launcher_fallback():
    plugin = MODEL.parent
    assert (plugin / 'CommandCenter.qml').exists(), 'native DMS modal missing'
    metadata = json.loads((plugin / 'plugin.json').read_text())
    assert metadata['components']['daemon'] == 'CommandCenter.qml'
    qml = (plugin / 'CommandCenter.qml').read_text()
    for contract in ['DModal {', 'AppSearchService.searchApplications', 'AppSearchService.getBuiltInLauncherItems', 'SessionService.launchDesktopEntry', 'SessionService.launchDesktopAction', 'PopoutService.openPowerMenu', 'Model.selection', 'Model.move', 'onStreamFinished', 'wilsof-file-search', 'pendingQuery === root.query', 'function status()', 'Theme.surface', 'forceActiveFocus']:
        assert contract in qml, contract
    manifest = (ROOT / 'runtime/image-files.txt').read_text().splitlines()
    for name in ['plugin.json', 'CommandCenter.qml', 'Model.js']:
        assert 'config/dms/plugins/wilsofCommandCenter/' + name in manifest
    runtime = (ROOT / 'runtime/desktop.py').read_text()
    assert 'wilsofCommandCenter' in runtime
    assert 'wilsof-file-search' in runtime
    assert 'commandCenter toggle' in (ROOT / 'bin/wilsof-search').read_text()


def test_shortcuts_and_lock_escape_the_shell_service_lifetime():
    qml = (MODEL.parent / 'CommandCenter.qml').read_text()
    assert 'DesktopEntries.heuristicLookup' in qml, 'Shortcuts must use DMS desktop-entry launch policy'
    assert 'Quickshell.execDetached([row.data])' not in qml
    assert '["systemd-run", "--user", "--collect", "--quiet", "--", root.bin + "wilsof-lock"]' in qml
    assert '["systemd-run", "--user", "--collect", "--quiet", "--", "xdg-open"' in qml
