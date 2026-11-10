"""Synthetic artifact/signature boundaries; not cryptographic trust acceptance."""
from pathlib import Path
import hashlib
import runpy
import subprocess

import pytest
ROOT=Path(__file__).resolve().parents[1]


def api():
    path=ROOT/'runtime/portal-package.py'
    assert path.is_file(), 'Missing independently pinned signed portal integration'
    return runpy.run_path(str(path))


def fixture(tmp_path,monkeypatch):
    module=api();package=tmp_path/module['NAME'];package.write_bytes(b'synthetic package')
    signature=Path(str(package)+'.sig');signature.write_bytes(b'synthetic detached signature')
    module['artifact'].__globals__['SHA256']=hashlib.sha256(package.read_bytes()).hexdigest()
    module['artifact'].__globals__['BINARY_SHA256']=hashlib.sha256(b'synthetic ELF').hexdigest()
    monkeypatch.setitem(module['artifact'].__globals__,'member',lambda p,n:b'pkgname = xdg-desktop-portal-hyprland\npkgver = 1.4.1-2.1\narch = x86_64\ndepend = wayland\n' if n=='.PKGINFO' else b'synthetic ELF')
    return module,package,signature


def test_signed_portal_input_requires_exact_archive_and_signature_before_staging(tmp_path,monkeypatch):
    module,package,signature=fixture(tmp_path,monkeypatch)
    record=module['artifact'](package)
    base=tmp_path/'profile/usr/share/wilsof'
    module['stage'](record,base)
    assert (base/'packages'/module['NAME']).read_bytes()==package.read_bytes()
    assert Path(str(base/'packages'/module['NAME'])+'.sig').read_bytes()==signature.read_bytes()
    assert module['embedded'](base)['version']=='1.4.1-2.1'
    signature.unlink()
    with pytest.raises(ValueError):module['artifact'](package)


@pytest.mark.parametrize('bad',['archive','signature-link','binary','missing-marker'])
def test_damaged_portal_input_never_falls_back(tmp_path,monkeypatch,bad):
    module,package,signature=fixture(tmp_path,monkeypatch)
    if bad=='archive':package.write_bytes(b'changed')
    elif bad=='signature-link':
        real=tmp_path/'signature';signature.rename(real);signature.symlink_to(real)
    elif bad=='binary':module['artifact'].__globals__['BINARY_SHA256']='0'*64
    if bad!='missing-marker':
        with pytest.raises(ValueError):module['artifact'](package)
    else:
        base=tmp_path/'base';module['stage'](module['artifact'](package),base)
        (base/module['MARKER']).unlink()
        with pytest.raises(ValueError):module['embedded'](base)


@pytest.mark.parametrize('case',['valid','signature-rejected','policy-drift'])
def test_portal_install_preserves_policy_and_propagates_signature_refusal(tmp_path,monkeypatch,case):
    module,package,signature=fixture(tmp_path,monkeypatch)
    live=tmp_path/'live';module['stage'](module['artifact'](package),live)
    target=tmp_path/'target';target.mkdir()
    snapshot=runpy.run_path(str(ROOT/'runtime/repository-snapshot.py'));snapshot['stage'](target)
    if case=='policy-drift':(target/'etc/pacman.conf').write_text('SigLevel = Never\n')
    calls=[]
    def run(argv,**kwargs):
        calls.append(argv)
        assert argv[:4]==['arch-chroot','-r',str(target),'pacman']
        assert '--config' not in argv and '--nodeps' not in argv
        out=''
        if '-U' in argv:
            assert Path(str(target/'usr/share/wilsof/packages'/module['NAME'])+'.sig').is_file()
            if case=='signature-rejected':raise subprocess.CalledProcessError(1,argv,stderr='signature rejected')
            binary=target/'usr/lib/xdg-desktop-portal-hyprland';binary.parent.mkdir(parents=True);binary.write_bytes(b'synthetic ELF')
        elif '-Q' in argv:out='xdg-desktop-portal-hyprland 1.4.1-2.1\n'
        elif '-Qoq' in argv:out='xdg-desktop-portal-hyprland\n'
        elif '-T' not in argv:pytest.fail('Unexpected package operation')
        return subprocess.CompletedProcess(argv,0,out,'')
    monkeypatch.setattr(subprocess,'run',run)
    if case=='valid':module['install'](target,live)
    else:
        with pytest.raises(ValueError if case=='policy-drift' else subprocess.CalledProcessError):module['install'](target,live)
        assert not (target/'usr/lib/xdg-desktop-portal-hyprland').exists()
        if case=='policy-drift':assert calls==[]


def test_live_profile_carries_portal_signature_and_runtime_install_consumer(tmp_path,monkeypatch):
    module,package,signature=fixture(tmp_path,monkeypatch)
    original=runpy.run_path
    monkeypatch.setattr(runpy,'run_path',lambda p,*a,**kw:module if str(p).endswith('portal-package.py') else original(p,*a,**kw))
    upstream=tmp_path/'releng';(upstream/'airootfs').mkdir(parents=True)
    (upstream/'packages.x86_64').write_text('base\n')
    output=tmp_path/'profile'
    original(str(ROOT/'scripts/prepare-iso.py'))['prepare'](upstream,output,ROOT,'a'*40,portal_package=package)
    base=output/'airootfs/usr/share/wilsof'
    assert (base/'packages'/module['NAME']).read_bytes()==package.read_bytes()
    assert Path(str(base/'packages'/module['NAME'])+'.sig').read_bytes()==signature.read_bytes()
    assert (base/module['MARKER']).is_file()
    assert "portal['install']" in (output/'airootfs/root/customize_airootfs.sh').read_text()
    assert "portal['install'](target" in (ROOT/'runtime/provision-target').read_text()


def test_build_wrapper_rejects_missing_portal_input_before_outputs(tmp_path):
    from build_fixture import layout
    source,_,_,env=layout(tmp_path)
    env.pop('WILSOF_PORTAL_PACKAGE',None)
    result=subprocess.run(['sh',str(source/'scripts/build-iso.sh'),'--build'],env=env,capture_output=True,text=True)
    assert result.returncode!=0
    assert not Path(env['WILSOF_ISO_OUTDIR']).exists()
    assert not Path(env['CAPTURE']).exists()


