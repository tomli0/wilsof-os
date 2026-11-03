"""The physical-PC probe emits allowlisted state, never raw user/network logs."""
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'bin/wilsof-hardware-report'


def load():
    assert SCRIPT.is_file(), 'Missing read-only physical hardware diagnostic'
    return runpy.run_path(str(SCRIPT))


def test_kernel_summary_drops_private_messages_but_keeps_firmware_error():
    m = load()
    private = 'SSID=private-school PSK=secret 10.2.3.4 aa:bb:cc:dd:ee:ff /home/alice/private.txt'
    report = m['kernel_summary'](
        private + '\nDirect firmware load for intel/sof/test.ri failed with error -2\n'
        'snd_hda_intel: probe failed\nBluetooth: hci0: timeout\n')
    encoded = json.dumps(report)
    for value in ('private-school', 'secret', '10.2.3.4', 'aa:bb', 'alice'):
        assert value not in encoded
    assert report['missing_firmware'] == [{'file': 'intel/sof/test.ri', 'error': -2}]
    assert report['audio_error_lines'] == 1
    assert report['bluetooth_error_lines'] == 1


def test_audio_summary_never_exports_stream_or_device_names():
    m = load()
    devices = [{'index': 7, 'name': 'personal-speaker', 'description': 'Alice',
                'state': 'RUNNING', 'mute': False,
                'volume': {'front-left': {'value_percent': '42%'}},
                'monitor_source_name': 'private'}]
    assert m['audio_summary'](devices, 'personal-speaker') == [
        {'index': 7, 'default': True, 'state': 'RUNNING', 'mute': False, 'volume_percent': [42]}]


def test_probe_executes_only_bounded_read_only_argv_and_handles_missing_tools():
    m = load()
    calls = []
    def missing(argv, **kwargs):
        calls.append((argv, kwargs))
        raise FileNotFoundError
    assert m['probe'](['nmcli', '-t', '-f', 'TYPE,STATE', 'device', 'status'], run=missing)['status'] == 'unavailable'
    assert calls[0][1]['timeout'] == 8
    assert calls[0][1]['stdin'] == subprocess.DEVNULL
    assert 'shell' not in calls[0][1]


def test_invalid_arguments_do_not_run_collection():
    load()
    r = subprocess.run([sys.executable, str(SCRIPT), '--password'], capture_output=True, text=True)
    assert r.returncode == 2
    assert not r.stdout


def test_kernel_probe_does_not_misreport_denied_journal_as_clean():
    m = load()
    def denied(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, '-- No entries --\n',
            'Hint: You are currently not seeing messages from other users and the system.\n')
    assert m['probe'](['journalctl', '-k', '-b'], run=denied)['status'] == 'unavailable'


def test_installed_desktop_explicitly_carries_standard_sof_firmware():
    packages = (ROOT / 'runtime/desktop-packages.txt').read_text().splitlines()
    assert 'sof-firmware' in packages, 'Live ISO includes SOF, installed target must not silently omit it'
