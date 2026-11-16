"""Execute the shipped QML save function's JavaScript, not a duplicate model."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_capture_save_sets_process_command_not_javascript_arguments():
    qml = (ROOT / 'config/dms/plugins/wilsofCommandCenter/Shortcuts.qml').read_text()
    start = qml.index('function save(args) {')
    end = qml.index('\n    Process {', start)
    function = qml[start:end].strip()
    script = '''const vm = require('vm');
const source = process.argv[1];
const state = {writer:{running:false}, editor:{arguments:[]}, helper:'/fixture/wilsof-shortcuts',
               capturing:true,captureAction:'help',confirmReset:false,errors:'',message:''};
vm.createContext(state);
vm.runInContext(source + '; save(["set","help","CTRL + ALT + J"]);', state);
console.log(JSON.stringify(state));'''
    r = subprocess.run(['node', '-e', script, function], capture_output=True, text=True, check=True)
    state = json.loads(r.stdout)
    assert state['writer']['running'] is True
    assert state['editor']['arguments'] == ['/fixture/wilsof-shortcuts', 'set', 'help', 'CTRL + ALT + J', '--apply']
