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


def test_cached_wifi_summary_is_read_only_and_never_exposes_network_identity():
    m=load()
    assert m['wifi_scan_summary']('42:WPA2\n80:WPA2 WPA3\n') == {'cache_only':True,'network_count':2,'strongest_signal_percent':80}
    assert m['wifi_scan_summary']('') == {'cache_only':True,'network_count':0,'strongest_signal_percent':None}
    source=SCRIPT.read_text()
    assert "'--rescan', 'no'" in source
    assert "'SSID'" not in source and "'BSSID'" not in source


def test_numeric_pci_identity_includes_unknown_wireless_and_graphics_without_guessing(tmp_path):
    m=load()
    for name,cls,vendor,device in [('0000:01:00.0','0x028000','0x14e4','0x4331'),('0000:02:00.0','0x030000','0x8086','0x1234')]:
        p=tmp_path/'bus/pci/devices'/name;p.mkdir(parents=True)
        for f,value in [('class',cls),('vendor',vendor),('device',device)]: (p/f).write_text(value)
    ids=m['hardware_ids'](tmp_path)
    assert len(ids['pci'])==2
    assert ids['pci'][0]['vendor']=='0x14e4' and ids['pci'][0]['driver'] is None
    assert ids['pci'][1]['class']=='0x030000'
    assert not any('wl'==row['driver'] for row in ids['pci'])


def test_session_display_summary_drops_monitor_and_owner_identity():
    m = load()
    raw = [{'name':'private-output', 'serial':'SECRET', 'description':'Alice display',
            'width':2560, 'height':1600, 'scale':2.0, 'refreshRate':60.0,
            'focused':True, 'disabled':False}]
    assert m['display_summary'](raw) == [
        {'width':2560, 'height':1600, 'scale':2.0, 'refresh_hz':60.0, 'disabled':False}]
    assert m['display_summary']([{'width':-1, 'height':1600, 'scale':'broken'}]) == []


def test_wireless_modules_and_power_are_read_from_sysfs_without_addresses(tmp_path):
    m = load()
    interface = tmp_path / 'class/net/wlp2s0'
    (interface / 'wireless').mkdir(parents=True)
    (interface / 'operstate').write_text('down\n')
    (interface / 'address').write_text('aa:bb:cc:dd:ee:ff\n')
    module = tmp_path / 'module/testwifi'; module.mkdir(parents=True)
    (interface / 'device/driver').mkdir(parents=True)
    (interface / 'device/driver/module').symlink_to(module)
    (tmp_path / 'power').mkdir()
    (tmp_path / 'power/state').write_text('freeze mem disk\n')
    (tmp_path / 'power/mem_sleep').write_text('[s2idle] deep\n')
    battery = tmp_path / 'class/power_supply/BAT0'; battery.mkdir(parents=True)
    (battery / 'type').write_text('Battery\n')
    (battery / 'capacity').write_text('63\n')
    (battery / 'status').write_text('Discharging\n')
    (battery / 'serial_number').write_text('PRIVATE-SERIAL\n')
    report = m['device_state'](tmp_path)
    assert report['wireless'] == [{'interface':'wlp2s0', 'state':'down', 'module':'testwifi', 'module_loaded':True}]
    assert report['sleep_states'] == ['freeze', 'mem', 'disk']
    assert report['mem_sleep'] == {'available':['s2idle','deep'], 'selected':'s2idle'}
    assert report['power_supplies'] == [{'type':'Battery', 'status':'Discharging', 'capacity_percent':63}]
    assert 'aa:bb' not in json.dumps(report) and 'PRIVATE-SERIAL' not in json.dumps(report)


def test_missing_rfkill_state_is_unknown_not_unblocked(tmp_path):
    m = load()
    radio = tmp_path / 'class/rfkill/rfkill0'; radio.mkdir(parents=True)
    (radio / 'type').write_text('wlan\n')
    assert m['hardware_ids'](tmp_path)['rfkill'] == [{'type':'wlan', 'soft':None, 'hard':None}]


def test_declared_firmware_checks_compressed_files_without_treating_all_as_required(tmp_path):
    m = load()
    (tmp_path / 'vendor').mkdir()
    (tmp_path / 'vendor/example.bin.zst').write_bytes(b'fixture')
    report = m['firmware_summary']('vendor/example.bin\nvendor/absent.bin\n../private\n/secret\n', tmp_path)
    assert report == {'declared_candidates_not_all_required':True, 'files':[
        {'pattern':'vendor/example.bin', 'present':True},
        {'pattern':'vendor/absent.bin', 'present':False}], 'truncated':False}
