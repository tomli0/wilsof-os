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
import subprocess

NAME='xdg-desktop-portal-hyprland-1.4.1-2.1-x86_64.pkg.tar.zst'
SHA256='d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0'
BINARY_SHA256='03ee10c6df912184461f5c516bd54a5b81e111804b9c41aaaf25387c40d3393f'
MARKER='portal-backport.required'


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


def artifact(package):
    package=regular(package)
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
            'version':'1.4.1-2.1','dependencies':dependencies,'approval':signer}


def stage(record,base):
    if artifact(record['package'])!=record:
        raise ValueError('Portal input changed before staging')
    base=Path(base);folder=base/'packages'
    paths=[folder/NAME,folder/(NAME+'.sig'),base/MARKER,folder/(NAME+'.approval.json')]
    if not base.is_absolute() or any(p.exists() or p.is_symlink() or any(a.is_symlink() for a in p.parents) for p in paths):
        raise ValueError('Refusing inherited portal staging paths')
    folder.mkdir(parents=True,exist_ok=True)
    for src,dst in [(Path(record['package']),paths[0]),(Path(record['package']+'.sig'),paths[1])]:
        with regular(src).open('rb') as incoming,dst.open('xb') as output:shutil.copyfileobj(incoming,output)
        dst.chmod(0o644)
    with paths[3].open('x') as output:output.write(json.dumps(record['approval'],sort_keys=True)+'\n')
    paths[3].chmod(0o644)
    with paths[2].open('x') as output:output.write(SHA256+'\n')
    paths[2].chmod(0o644)
    return embedded(base)


def embedded(base):
    base=Path(base);paths=[base/'packages'/NAME,base/'packages'/(NAME+'.sig'),base/MARKER,base/'packages'/(NAME+'.approval.json')]
    if not any(p.exists() or p.is_symlink() for p in paths):return None
    if regular(paths[2]).read_text().strip()!=SHA256:
        raise ValueError('Portal policy marker mismatch; no repository fallback')
    return artifact(paths[0])


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


def install(target,base):
    record=embedded(base)
    if record is None:return
    if os.geteuid()!=0:raise PermissionError('Portal installation requires root in the isolated target environment')
    target=Path(target)
    source=Path(__file__).resolve().parent
    pin=runpy.run_path(str(source/'pinned-package.py'))
    # This exact approved config retains PackageRequired/TrustedOnly and the
    # existing local-package policy. A present signature is checked by pacman.
    runpy.run_path(str(source/'repository-snapshot.py'))['read'](target)
    destination=target/'usr/share/wilsof'
    if Path(base).resolve()!=destination.resolve():record=stage(record,destination)
    inside='/usr/share/wilsof/packages/'+NAME
    # Use only the already enrolled target pacman keyring. This is an additional
    # signer/validity gate, never a replacement for libalpm's own verification.
    proof=subprocess.run(pin['target_command'](target,'gpg','--no-options','--batch',
        '--homedir','/etc/pacman.d/gnupg','--no-auto-key-retrieve','--no-auto-key-import',
        '--trust-model','pgp','--status-fd','1','--verify',inside+'.sig',inside),
        check=True,capture_output=True,text=True,timeout=60)
    signature_status(proof.stdout,record['approval']['primary_fingerprint'])
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
