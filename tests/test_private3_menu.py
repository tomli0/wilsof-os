"""Private3 contracts execute the JavaScript shared with the resident menu."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'config/dms/plugins/wilsofCommandCenter/Model.js'


def evaluate(code):
    script = "const fs=require('fs'),vm=require('vm');const m={};vm.createContext(m);vm.runInContext(fs.readFileSync(process.argv[1],'utf8').replace('.pragma library',''),m);console.log(JSON.stringify(" + code + "));"
    result = subprocess.run(['node', '-e', script, str(MODEL)], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_root_has_exactly_eight_categories_and_apps_has_direct_launches():
    assert evaluate('m.defaults().map(r=>r.name)') == ['Apps', 'Learn', 'Tools', 'Appearance', 'Configure', 'Software', 'About', 'Power']
    assert evaluate('m.page("apps").map(r=>r.id)') == ['applications', 'browser', 'files', 'terminal']
    assert evaluate('m.page("learn").map(r=>r.id)') == ['shortcuts', 'guide', 'hyprland-docs', 'dux-docs', 'arch-wiki']
    assert evaluate('m.page("power").map(r=>r.id)') == ['lock', 'logout', 'restart', 'shutdown']


def test_nested_navigation_restores_each_selection_query_and_scroll():
    result = evaluate('''(()=>{
        const root={category:"",query:"",selectedId:"configure",scrollY:86,stack:[]};
        const first=m.enter(root,"configure");
        first.selectedId="network";first.scrollY=42;
        const second=m.enter(first,"network");second.selectedId="bluetooth";
        return {first:m.back(second),root:m.back(m.back(second)),empty:m.back(root)};
    })()''')
    assert result['first']['category'] == 'configure'
    assert result['first']['selectedId'] == 'network'
    assert result['first']['scrollY'] == 42
    assert result['root'] == {'category':'', 'query':'', 'selectedId':'configure', 'scrollY':86, 'stack':[]}
    assert result['empty'] is None


def test_editing_keys_do_not_trigger_back_or_forward_navigation():
    assert evaluate('m.keyAction("Left",true,false)') == 'edit'
    assert evaluate('m.keyAction("Right",true,false)') == 'edit'
    assert evaluate('m.keyAction("Backspace",true,false)') == 'edit'
    assert evaluate('m.keyAction("Left",false,false)') == 'back'
    assert evaluate('m.keyAction("Right",false,false)') == 'forward'
    assert evaluate('m.keyAction("Backspace",false,false)') == 'back'
    assert evaluate('m.keyAction("Escape",true,false)') == 'escape'
    assert evaluate('m.keyAction("Down",true,false)') == 'next'
    assert evaluate('m.keyAction("Up",true,false)') == 'previous'
    assert evaluate('m.keyAction("Return",true,false)') == 'activate'
    assert evaluate('m.keyAction("Left",false,true)') == 'edit'


def test_ranked_case_insensitive_search_hides_unavailable_actions():
    for query, first in [('FIREFOX','browser'), ('wifi','wifi'), ('screenshot','screenshot'), ('shortcuts','shortcuts'), ('terminal','terminal'), ('update','update')]:
        assert evaluate(f'm.search({json.dumps(query)},[],null)[0].id') == first
    assert evaluate('m.search("screenshot",[],{screenshot:false}).length') == 0
    assert evaluate('m.search("not-an-action-427",[],null).length') == 0
    assert evaluate('m.search("firefox",[m.row("app:firefox","Firefox","Web browser","apps","app",{id:"firefox"})],null).map(r=>r.id)') == ['browser']


def test_native_menu_is_one_resident_component_with_focus_and_navigation_wiring():
    plugin = MODEL.parent
    qml = (plugin / 'CommandCenter.qml').read_text()
    for contract in ['Model.enter(', 'Model.back(', 'Model.keyAction(', 'Model.search(', 'function returnFromDialog()', 'closeOnEscapeKey: false', 'search.forceActiveFocus()', 'root.goRoot()', 'root.goBack()', 'onClicked: root.activate(index)', 'modalWidth: Math.min(460', 'animationDuration: 0']:
        assert contract in qml, contract
    search = (ROOT / 'bin/wilsof-search').read_text()
    assert 'spotlight' not in search
    assert 'commandCenter toggle' in search
    assert 'commandCenter configure' in search
    metadata = json.loads((plugin / 'plugin.json').read_text())
    assert metadata['components']['widget'] == 'Bar.qml'
    bar = (plugin / 'Bar.qml').read_text()
    assert 'wilsof-search' in bar and 'toggle' in bar
    assert 'ws-monogram.png' in bar
    assert 'implicitWidth: 38' in bar, 'Image source width must not collapse the bar into its overflow control'


def test_dialog_roundtrip_restores_the_same_menu_frame():
    qml = (MODEL.parent/'CommandCenter.qml').read_text()
    assert 'dialogSnapshot = snapshot()' in qml
    assert 'apply(dialogSnapshot)' in qml
