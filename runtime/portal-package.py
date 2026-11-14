"""Independent fixed portal backport input; signature policy is never weakened.

A detached signature is mandatory. Pacman's existing TrustedOnly policy must
accept it at installation; a hash or signature-file presence is not trust proof.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import stat
import subprocess
import tempfile

NAME='xdg-desktop-portal-hyprland-1.4.1-2.1-x86_64.pkg.tar.zst'
SHA256='d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0'
BINARY_SHA256='03ee10c6df912184461f5c516bd54a5b81e111804b9c41aaaf25387c40d3393f'
MARKER='portal-backport.required'
TEST_MARKER='portal-test-only.json'
TEST_LABEL='WILSOF TEST ONLY — production signing trust pending. Do not use for production.'


def test_manifest(path,build_version):
    """A separate nonproduction assertion, never an owner approval."""
    try:
        path=regular(path)
        if path.stat().st_size>4096:raise ValueError('Oversized test manifest')
        def unique(pairs):
            result={}
            for key,value in pairs:
                if key in result:raise ValueError('Duplicate test manifest field')
                result[key]=value
            return result
        record=json.loads(path.read_text(),object_pairs_hook=unique)
        if (not isinstance(record,dict) or set(record)!={'schema','mode','production_trust','build_version',
                'package_sha256','primary_fingerprint','certificate_sha256'} or
                type(record['schema']) is not int or record['schema']!=1 or record['mode']!='test-only' or
                record['production_trust']!='pending' or record['package_sha256']!=SHA256 or
                not isinstance(build_version,str) or
                not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,53}-test-only',build_version) or
                record['build_version']!=build_version or
                not isinstance(record['primary_fingerprint'],str) or
                not re.fullmatch(r'[0-9A-F]{40}',record['primary_fingerprint']) or
                not isinstance(record['certificate_sha256'],str) or
                not re.fullmatch(r'[0-9a-f]{64}',record['certificate_sha256'])):
            raise ValueError('Invalid test-only identity/version')
    except (OSError,ValueError,TypeError) as error:
        raise ValueError('Missing or invalid TEST ONLY manifest/version') from error
    return record


def test_certificate(package,record):
    certificate=regular(str(package)+'.test-only.asc')
    if not 0<certificate.stat().st_size<=131072:
        raise ValueError('Bounded TEST ONLY public certificate required')
    data=certificate.read_bytes()
    if (hashlib.sha256(data).hexdigest()!=record['certificate_sha256'] or
            not data.startswith(b'-----BEGIN PGP PUBLIC KEY BLOCK-----\n') or
            not data.rstrip().endswith(b'-----END PGP PUBLIC KEY BLOCK-----') or b'PRIVATE KEY' in data):
        raise ValueError('TEST ONLY public certificate checksum/format mismatch')
    # Show-only cannot import/enroll anything. Never open the host GPG home.
    with tempfile.TemporaryDirectory(prefix='wilsof-public-',dir=os.environ.get('TMPDIR')) as home:
        proof=subprocess.run(['gpg','--no-options','--batch','--no-autostart','--homedir',home,
            '--no-auto-key-retrieve','--no-auto-key-import','--with-colons',
            '--import-options','show-only','--import',str(certificate)],
            check=True,capture_output=True,text=True,timeout=60)
    rows=[line.split(':') for line in proof.stdout.splitlines()]
    keys=[row for row in rows if row[0] in {'pub','sec','ssb'}]
    fingerprints=[row[9] for row in rows if row[0]=='fpr' and len(row)>9]
    if len(keys)!=1 or keys[0][0]!='pub' or not fingerprints or fingerprints[0]!=record['primary_fingerprint']:
        raise ValueError('TEST ONLY public certificate primary fingerprint mismatch')
    return certificate


def regular(path):
    path=Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file():
        raise ValueError('Portal package/signature must be a canonical regular file')
    return path


def member(package,name):
    return subprocess.run(['bsdtar','-xOf',str(package),name],check=True,capture_output=True,timeout=60).stdout


def approval(package):
    """Read an owner-supplied pin, never create approval or enroll a public key.

    The authenticated build handoff must freeze this external input after owner
    review. Its self-description alone is not evidence of identity approval.
    """
    try:
        path=regular(str(package)+'.approval.json')
        if path.stat().st_size>4096:raise ValueError('Oversized approval')
        def unique(pairs):
            result={}
            for key,value in pairs:
                if key in result:raise ValueError('Duplicate approval field')
                result[key]=value
            return result
        record=json.loads(path.read_text(),object_pairs_hook=unique)
        if (not isinstance(record,dict) or set(record)!={'schema','approval','package_sha256','primary_fingerprint'} or
                type(record['schema']) is not int or record['schema']!=1 or record['approval']!='owner-approved' or
                record['package_sha256']!=SHA256 or
                not isinstance(record['primary_fingerprint'],str) or
                not re.fullmatch(r'[0-9A-F]{40}',record['primary_fingerprint'])):
            raise ValueError('Invalid approval')
    except (OSError,ValueError,TypeError) as error:
        raise ValueError('Missing or invalid owner signer approval') from error
    return record


def artifact(package,*,test_only=False,build_version=None):
    package=regular(package)
    if not test_only and isinstance(build_version,str) and build_version.endswith('-test-only'):
        raise ValueError('TEST ONLY build version requires explicit test identity/mode')
    if test_only:
        signer=test_manifest(str(package)+'.test-only.json',build_version)
        test_certificate(package,signer)
        if Path(str(package)+'.approval.json').exists() or Path(str(package)+'.approval.json').is_symlink():
            raise ValueError('TEST ONLY input must not claim production approval')
    else:
        if any(Path(str(package)+suffix).exists() or Path(str(package)+suffix).is_symlink()
               for suffix in ('.test-only.json','.test-only.asc')):
            raise ValueError('TEST ONLY input requires explicit nonproduction opt-in')
        signer=approval(package)
    signature=regular(str(package)+'.sig')
    if package.name!=NAME or not 0 < signature.stat().st_size <= 65536:
        raise ValueError('Exact portal archive and bounded detached signature required')
    with package.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=SHA256:
            raise ValueError('Portal package checksum mismatch')
    info=member(package,'.PKGINFO').decode('utf-8')
    for key,value in [('pkgname','xdg-desktop-portal-hyprland'),('pkgver','1.4.1-2.1'),('arch','x86_64')]:
        if re.findall(r'^'+key+r' = (.+)$',info,re.M)!=[value]:
            raise ValueError('Portal package metadata mismatch')
    if hashlib.sha256(member(package,'usr/lib/xdg-desktop-portal-hyprland')).hexdigest()!=BINARY_SHA256:
        raise ValueError('Portal packaged executable checksum mismatch')
    dependencies=re.findall(r'^depend = (.+)$',info,re.M)
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9@._+:-]*(?:[<>=]+[A-Za-z0-9._+:-]+)?',p) for p in dependencies):
        raise ValueError('Invalid portal dependency constraint')
    return {'package':str(package),'signature_sha256':hashlib.sha256(signature.read_bytes()).hexdigest(),
            'version':'1.4.1-2.1','dependencies':dependencies,'test_only' if test_only else 'approval':signer}


def stage(record,base):
    mode={} if 'test_only' not in record else {'test_only':True,'build_version':record['test_only']['build_version']}
    if artifact(record['package'],**mode)!=record:
        raise ValueError('Portal input changed before staging')
    base=Path(base);folder=base/'packages'
    paths=[folder/NAME,folder/(NAME+'.sig'),base/MARKER,folder/(NAME+'.approval.json')]
    test_paths=[base/TEST_MARKER,folder/(NAME+'.test-only.json'),folder/(NAME+'.test-only.asc')]
    if not base.is_absolute() or any(p.exists() or p.is_symlink() or any(a.is_symlink() for a in p.parents) for p in paths+test_paths):
        raise ValueError('Refusing inherited portal staging paths')
    folder.mkdir(parents=True,exist_ok=True)
    for src,dst in [(Path(record['package']),paths[0]),(Path(record['package']+'.sig'),paths[1])]:
        with regular(src).open('rb') as incoming,dst.open('xb') as output:shutil.copyfileobj(incoming,output)
        dst.chmod(0o644)
    if mode:
        for path in test_paths[:2]:
            with path.open('x') as output:output.write(json.dumps(record['test_only'],sort_keys=True)+'\n')
            path.chmod(0o644)
        with regular(record['package']+'.test-only.asc').open('rb') as incoming,test_paths[2].open('xb') as output:
            shutil.copyfileobj(incoming,output)
        test_paths[2].chmod(0o644)
    else:
        with paths[3].open('x') as output:output.write(json.dumps(record['approval'],sort_keys=True)+'\n')
        paths[3].chmod(0o644)
    with paths[2].open('x') as output:output.write(SHA256+'\n')
    paths[2].chmod(0o644)
    return embedded(base,**mode)


def embedded(base,*,test_only=False,build_version=None):
    base=Path(base);paths=[base/'packages'/NAME,base/'packages'/(NAME+'.sig'),base/MARKER,base/'packages'/(NAME+'.approval.json'),
                          base/TEST_MARKER,base/'packages'/(NAME+'.test-only.json'),base/'packages'/(NAME+'.test-only.asc')]
    if not any(p.exists() or p.is_symlink() for p in paths):
        if test_only:raise ValueError('Missing persistent TEST ONLY marker/package')
        return None
    if regular(paths[2]).read_text().strip()!=SHA256:
        raise ValueError('Portal policy marker mismatch; no repository fallback')
    if test_only:
        marker=test_manifest(base/TEST_MARKER,build_version)
        record=artifact(paths[0],test_only=True,build_version=build_version)
        if marker!=record['test_only']:raise ValueError('TEST ONLY persistent marker mismatch')
        return record
    if paths[4].exists() or paths[4].is_symlink():
        raise ValueError('TEST ONLY marker requires explicit nonproduction opt-in')
    return artifact(paths[0])


def test_context(base):
    """Propagate only a persistent image opt-in, never an environment override."""
    base=Path(base);marker=base/TEST_MARKER
    if not marker.exists() and not marker.is_symlink():
        if any((base/'packages'/(NAME+suffix)).exists() or (base/'packages'/(NAME+suffix)).is_symlink()
               for suffix in ('.test-only.json','.test-only.asc')):
            raise ValueError('Missing persistent TEST ONLY marker; no production fallback')
        return {}
    try:
        data=json.loads(regular(marker).read_text())
        version=data['build_version']
    except (OSError,ValueError,TypeError,KeyError) as error:
        raise ValueError('Invalid persistent TEST ONLY marker') from error
    test_manifest(marker,version)
    return {'test_only':True,'build_version':version}


def signature_status(output,expected):
    """Require one valid binary signature, the pinned primary, and full validity."""
    rows=[line[len('[GNUPG:] '):].split() for line in output.splitlines() if line.startswith('[GNUPG:] ')]
    rows=[row for row in rows if row]
    invalid={'BADSIG','ERRSIG','EXPSIG','EXPKEYSIG','REVKEYSIG','KEYREVOKED',
             'NO_PUBKEY','NODATA','BADARMOR','FAILURE','ERROR','UNEXPECTED',
             'TRUST_UNDEFINED','TRUST_NEVER','TRUST_MARGINAL'}
    signatures=[row for row in rows if row[0]=='VALIDSIG']
    trusted=[row for row in rows if row[0] in {'TRUST_FULLY','TRUST_ULTIMATE'}]
    if (sum(row[0]=='NEWSIG' for row in rows)!=1 or
            sum(row[0]=='GOODSIG' for row in rows)!=1 or len(signatures)!=1 or len(trusted)!=1 or
            any(row[0] in invalid for row in rows) or trusted[0][1:]!=['0','pgp']):
        raise ValueError('Portal signature is not valid and fully trusted')
    row=signatures[0]
    if (len(row)!=11 or not re.fullmatch(r'[0-9A-F]{40}',row[1]) or row[10]!=expected or
            row[8] not in {'8','9','10','11'} or row[9]!='00'):
        raise ValueError('Portal signature signer or algorithm mismatch')
    return {'primary_fingerprint':row[10],'signing_fingerprint':row[1],'hash_algorithm':row[8]}


def label_test_root(target):
    """Visible persistent warning; preserve any existing console notices."""
    paths=[Path(target)/relative for relative in ('etc/issue','etc/motd')]
    for path in paths:
        if (not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents)) or
                (path.exists() and not path.is_file())):
            raise ValueError('Unsafe TEST ONLY notice path')
    for path in paths:
        existing=path.read_text() if path.exists() else ''
        if not existing.startswith(TEST_LABEL+'\n'):
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(TEST_LABEL+'\n'+existing)
            path.chmod(0o644)


def installation_inputs(target,base,*,test_only=False,build_version=None):
    record=embedded(base,test_only=test_only,build_version=build_version)
    if record is None:return Path(target),None,None
    if os.geteuid()!=0:raise PermissionError('Portal installation requires root in the isolated target environment')
    target=Path(target)
    if test_only:
        if not target.is_absolute() or any(p.is_symlink() for p in (target,*target.parents)):
            raise ValueError('Canonical isolated TEST ONLY target required')
        destination=target/'usr/share/wilsof'
        if target==Path('/'):
            # Only a pre-materialized, explicitly marked build/live root may use
            # native commands. A caller cannot turn the host into a test target
            # by pointing at an external staging folder.
            marker=regular(destination/TEST_MARKER)
            if (Path(base)!=destination or marker.stat().st_uid!=0 or marker.stat().st_mode&0o022 or
                    test_manifest(marker,build_version)!=record['test_only']):
                raise ValueError('Running root lacks its built TEST ONLY marker')
        elif not target.is_mount():
            raise ValueError('TEST ONLY installation requires a fresh mounted target')
        for relative in ('etc/pacman.d/gnupg','etc/issue','etc/motd','usr/share/wilsof'):
            path=target/relative
            if any(p.is_symlink() for p in (path,*path.parents)):
                raise ValueError('Refusing TEST ONLY target symlink')
    source=Path(__file__).resolve().parent
    pin=runpy.run_path(str(source/'pinned-package.py'))
    # This exact approved config retains PackageRequired/TrustedOnly and the
    # existing local-package policy. A present signature is checked by pacman.
    runpy.run_path(str(source/'repository-snapshot.py'))['read'](target)
    destination=target/'usr/share/wilsof'
    if Path(base).resolve()!=destination.resolve():
        if test_only and (destination/TEST_MARKER).exists():
            staged=embedded(destination,test_only=True,build_version=build_version)
            if staged is None or {k:v for k,v in staged.items() if k!='package'}!={k:v for k,v in record.items() if k!='package'}:
                raise ValueError('Inherited TEST ONLY target inputs differ')
            record=staged
        else:
            record=stage(record,destination)
    return target,record,pin


def prepare_test_trust(target,base,*,build_version):
    """Enroll before ANY signed private-package transaction, inside target only."""
    target,record,pin=installation_inputs(target,base,test_only=True,build_version=build_version)
    assert record is not None and pin is not None
    inside='/usr/share/wilsof/packages/'+NAME
    label_test_root(target)
    for args in (('--init',),('--populate','archlinux'),('--add',inside+'.test-only.asc'),
                 ('--lsign-key',record['test_only']['primary_fingerprint'])):
        subprocess.run(pin['target_command'](target,'pacman-key','--gpgdir','/etc/pacman.d/gnupg',*args),
            check=True,capture_output=True,text=True,timeout=180)
    return record


def seal_test_image(root=Path('/'),*,build_version):
    """Image-only sealing: retain public trust, never ship local master secrets.

    Fresh targets (and the ephemeral live overlay) initialize their OWN local
    pacman master. Never call this for an installed target or during updates.
    """
    root=Path(root)
    if not root.is_absolute() or root.resolve()!=root:
        raise ValueError('Canonical TEST ONLY image root required')
    base=root/'usr/share/wilsof'
    embedded(base,test_only=True,build_version=build_version)
    marker=regular(base/TEST_MARKER)
    if root==Path('/') and (marker.stat().st_uid!=0 or marker.stat().st_mode&0o022):
        raise ValueError('Built TEST ONLY image marker required')
    keyring=root/'etc/pacman.d/gnupg'
    folders=[keyring/'private-keys-v1.d',keyring/'openpgp-revocs.d']
    files=[keyring/'secring.gpg']
    for folder in folders:
        if any(p.is_symlink() for p in (folder,*folder.parents)):
            raise ValueError('Unsafe TEST ONLY image secret directory')
        if folder.exists():
            if not folder.is_dir():raise ValueError('Unsafe image secret directory type')
            files.extend(folder.iterdir())
    for path in files:
        if any(p.is_symlink() for p in (path,*path.parents)):
            raise ValueError('Unsafe TEST ONLY image secret path')
        if path.exists():
            info=path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_uid!=os.geteuid():
                raise ValueError('Unsafe TEST ONLY image secret ownership/type')
    pin=runpy.run_path(str(Path(__file__).with_name('pinned-package.py')))
    subprocess.run(pin['target_command'](root,'gpgconf','--homedir','/etc/pacman.d/gnupg','--kill','gpg-agent'),
                   check=True,capture_output=True,text=True,timeout=60)
    for path in files:path.unlink(missing_ok=True)
    for folder in folders:
        if folder.exists():folder.rmdir()


def install(target,base,*,test_only=False,build_version=None):
    if test_only:
        record=prepare_test_trust(target,base,build_version=build_version)
        target=Path(target)
        pin=runpy.run_path(str(Path(__file__).with_name('pinned-package.py')))
    else:
        target,record,pin=installation_inputs(target,base)
        if record is None:return
    assert record is not None and pin is not None
    inside='/usr/share/wilsof/packages/'+NAME
    # Use only the already enrolled target pacman keyring. This is an additional
    # signer/validity gate, never a replacement for libalpm's own verification.
    proof=subprocess.run(pin['target_command'](target,'gpg','--no-options','--batch',
        '--homedir','/etc/pacman.d/gnupg','--no-auto-key-retrieve','--no-auto-key-import',
        '--trust-model','pgp','--status-fd','1','--verify',inside+'.sig',inside),
        check=True,capture_output=True,text=True,timeout=60)
    signature_status(proof.stdout,record['test_only' if test_only else 'approval']['primary_fingerprint'])
    def run(*args):
        return subprocess.run(pin['target_command'](target,'pacman',*args),check=True,
                              capture_output=True,text=True,timeout=180)
    if record['dependencies']:
        result=run('-T','--',*record['dependencies'])
        if result.stdout.strip():raise ValueError('Portal dependency closure is incomplete')
    run('-U','--noconfirm','--needed','--','/usr/share/wilsof/packages/'+NAME)
    if (run('-Q','xdg-desktop-portal-hyprland').stdout.strip()!='xdg-desktop-portal-hyprland 1.4.1-2.1' or
            run('-Qoq','/usr/lib/xdg-desktop-portal-hyprland').stdout.strip()!='xdg-desktop-portal-hyprland' or
            hashlib.sha256(regular(target/'usr/lib/xdg-desktop-portal-hyprland').read_bytes()).hexdigest()!=BINARY_SHA256):
        raise ValueError('Installed portal identity does not match the reviewed backport')
