"""Host admission stays authoritative when the build root hides host artifacts."""
import hashlib,json,os,runpy,stat
from pathlib import Path
from types import SimpleNamespace
import pytest
import subprocess
from build_fixture import layout
ROOT=Path(__file__).resolve().parents[1]

def setup(tmp_path,monkeypatch):
    api=runpy.run_path(str(ROOT/'scripts/artifact-lifecycle.py'))
    catalog=tmp_path/'catalog.json';work=str(tmp_path/'work');out=str(tmp_path/'out')
    record={'workflow':'native-build','state':'ACTIVE','purpose':'Sequential isolated ISO build from '+'a'*40,'budget_bytes':api['MAX_BUDGET'],'artifacts':[{'path':work,'kind':'build-workspace','classification':'DISPOSABLE'},{'path':work+'-profile','kind':'cache','classification':'DISPOSABLE'},{'path':out,'kind':'iso','classification':'PROTECTED'}]}
    catalog.write_text(json.dumps({'schema':1,'inventory_complete':True,'workflows':[record]}))
    receipt=tmp_path/'admission.json'
    data={'schema':1,'scope':'host-admitted-isolated-build','catalog_sha256':hashlib.sha256(catalog.read_bytes()).hexdigest(),'workflow':'native-build','source_commit':'a'*40,'work':work,'out':out}
    receipt.write_text(json.dumps(data));receipt.chmod(0o400)
    original=Path.stat
    def info(p,*a,**kw):
        s=original(p,*a,**kw)
        if p==receipt:return SimpleNamespace(st_mode=s.st_mode,st_uid=0,st_size=s.st_size,st_nlink=1)
        return s
    monkeypatch.setattr(Path,'stat',info)
    return api,catalog,receipt,data,work,out

def test_host_preadmitted_record_is_checked_without_reallocating(tmp_path,monkeypatch):
    api,cat,p,data,work,out=setup(tmp_path,monkeypatch)
    before=cat.read_bytes()
    assert api['validate_build_admission'](str(cat),str(p),'native-build','a'*40,work,out)['state']=='ACTIVE'
    assert cat.read_bytes()==before and not Path(work).exists() and not Path(out).exists()

@pytest.mark.parametrize('bad',['hash','source','work','workflow','mode','symlink','extra-field','inactive'])
def test_changed_external_admission_refuses_before_output(tmp_path,monkeypatch,bad):
    api,cat,p,data,work,out=setup(tmp_path,monkeypatch)
    if bad=='hash':data['catalog_sha256']='0'*64
    elif bad=='source':data['source_commit']='b'*40
    elif bad=='work':data['work']=str(tmp_path/'elsewhere')
    elif bad=='workflow':data['workflow']='other'
    elif bad=='mode':p.chmod(0o600)
    elif bad=='extra-field':data['approved']=True
    elif bad=='inactive':
        c=json.loads(cat.read_text());c['workflows'][0]['state']='COMPLETE';cat.write_text(json.dumps(c));data['catalog_sha256']=hashlib.sha256(cat.read_bytes()).hexdigest()
    if bad=='symlink':
        p.rename(tmp_path/'real');p.symlink_to(tmp_path/'real')
    elif bad!='mode':
        p.chmod(0o600);p.write_text(json.dumps(data));p.chmod(0o400)
    with pytest.raises(ValueError):api['validate_build_admission'](str(cat),str(p),'native-build','a'*40,work,out)
    assert not Path(work).exists() and not Path(out).exists()


def test_wrapper_refuses_untrusted_host_receipt_without_mutating_catalog(tmp_path):
    source,_,_,env=layout(tmp_path)
    receipt=tmp_path/'untrusted-admission.json';receipt.write_text('{}')
    env['WILSOF_HOST_BUILD_ADMISSION']=str(receipt)
    catalog=Path(env['WILSOF_ARTIFACT_CATALOG']);before=catalog.read_bytes()
    result=subprocess.run(['sh',str(source/'scripts/build-iso.sh'),'--build'],env=env,capture_output=True,text=True)
    assert result.returncode!=0 and 'admission' in result.stderr
    assert catalog.read_bytes()==before
    assert not Path(env['CAPTURE']).exists() and not Path(env['WILSOF_ISO_OUTDIR']).exists()


def preserved_setup(tmp_path,monkeypatch,profile='PROTECTED'):
    import copy
    api=runpy.run_path(str(ROOT/'scripts/artifact-lifecycle.py'))
    monkeypatch.setattr(os,'statvfs',lambda _:SimpleNamespace(f_bavail=64*1024**3,f_frsize=1))
    old=tmp_path/'old-work';old.mkdir();(old/'sentinel').write_text('preserve old build')
    prior={'schema':1,'inventory_complete':True,'workflows':[{'workflow':'old','state':'CLEANUP_PENDING','budget_bytes':api['MAX_BUDGET'],'artifacts':[{'path':str(old),'kind':'build-workspace','classification':'DISPOSABLE'}]}]}
    catalog=tmp_path/'catalog.json';catalog.write_text(json.dumps(prior));before=copy.deepcopy(prior)
    work,out=str(tmp_path/'new-work'),str(tmp_path/'new-out')
    reason='Owner requests one corrected candidate while all existing build data is retained'
    artifacts=[{'path':work,'kind':'build-workspace','classification':'PROTECTED','exception_reason':reason,'dependencies':['a'*40],'cleanup_condition':'Retain; no cleanup without owner approval'},
               {'path':work+'-profile','kind':'cache','classification':profile,'dependencies':['a'*40],'cleanup_condition':'Retain until new candidate acceptance'},
               {'path':out,'kind':'iso','classification':'PROTECTED','dependencies':['a'*40],'cleanup_condition':'Preserve candidate'}]
    api['register'](str(catalog),{'schema':1,'owner':'wilsof-build','workflow':'new','purpose':'Sequential isolated ISO build from '+'a'*40,'budget_bytes':api['MAX_BUDGET'],'artifacts':artifacts})
    assert json.loads(catalog.read_text())['workflows'][:-1]==before['workflows']
    receipt=tmp_path/'admission.json'
    data={'schema':1,'scope':'host-admitted-isolated-build','catalog_sha256':hashlib.sha256(catalog.read_bytes()).hexdigest(),'workflow':'new','source_commit':'a'*40,'work':work,'out':out,
          'preservation':{'reason':reason,'profile_classification':profile}}
    receipt.write_text(json.dumps(data));receipt.chmod(0o400)
    real=Path.stat
    def root_receipt(path,*args,**kwargs):
        observed=real(path,*args,**kwargs)
        if path==receipt:return SimpleNamespace(st_mode=observed.st_mode,st_uid=0,st_size=observed.st_size,st_nlink=observed.st_nlink)
        return observed
    monkeypatch.setattr(Path,'stat',root_receipt)
    return api,catalog,receipt,data,work,out,old


@pytest.mark.parametrize('profile',['DISPOSABLE','PROTECTED'])
def test_root_receipt_accepts_exact_individual_preservation_without_reallocation(tmp_path,monkeypatch,profile):
    api,cat,receipt,data,work,out,old=preserved_setup(tmp_path,monkeypatch,profile)
    before=cat.read_bytes()
    result=api['validate_build_admission'](str(cat),str(receipt),'new','a'*40,work,out)
    assert result['state']=='ACTIVE' and result['budget_bytes']==25*1024**3
    assert api['audit'](str(cat))['violations']==[]
    assert cat.read_bytes()==before and (old/'sentinel').read_text()=='preserve old build'
    assert not Path(work).exists() and not Path(out).exists()


@pytest.mark.parametrize('bad',['missing','none','extra','blank','long','wrong-type','wrong-profile','profile-mismatch','reason-mismatch','artifact-reason-missing','workspace-disposable','output-disposable','budget','mode','hash','extra-field'])
def test_preservation_admission_refuses_changed_authority_before_output(tmp_path,monkeypatch,bad):
    api,cat,p,data,work,out,old=preserved_setup(tmp_path,monkeypatch)
    state=json.loads(cat.read_text());record=state['workflows'][-1]
    if bad=='missing':data.pop('preservation')
    elif bad=='none':data['preservation']=None
    elif bad=='extra':data['preservation']['approved']=True
    elif bad=='blank':data['preservation']['reason']='  '
    elif bad=='long':data['preservation']['reason']='x'*1025
    elif bad=='wrong-type':data['preservation']['reason']=True
    elif bad=='wrong-profile':data['preservation']['profile_classification']='ARCHIVE'
    elif bad=='profile-mismatch':data['preservation']['profile_classification']='DISPOSABLE'
    elif bad=='reason-mismatch':data['preservation']['reason']+=' changed'
    elif bad=='artifact-reason-missing':record['artifacts'][0].pop('exception_reason')
    elif bad=='workspace-disposable':record['artifacts'][0]['classification']='DISPOSABLE'
    elif bad=='output-disposable':record['artifacts'][2]['classification']='DISPOSABLE'
    elif bad=='budget':record['budget_bytes']+=1
    elif bad=='extra-field':data['approved']=True
    cat.write_text(json.dumps(state));data['catalog_sha256']=hashlib.sha256(cat.read_bytes()).hexdigest()
    if bad=='hash':data['catalog_sha256']='0'*64
    p.chmod(0o600);p.write_text(json.dumps(data));p.chmod(0o600 if bad=='mode' else 0o400)
    before=cat.read_bytes()
    with pytest.raises(ValueError):api['validate_build_admission'](str(cat),str(p),'new','a'*40,work,out)
    assert cat.read_bytes()==before and (old/'sentinel').read_text()=='preserve old build'
    assert not Path(work).exists() and not Path(out).exists()


def test_preservation_registration_keeps_capacity_and_global_limits(tmp_path,monkeypatch):
    api,cat,p,data,work,out,old=preserved_setup(tmp_path,monkeypatch)
    assert api['MAX_BUDGET']==25*1024**3 and api['RESERVE']==5*1024**3
    assert api['LIMITS']=={'iso':2,'qa-disk':2,'build-workspace':1}
    record=json.loads(cat.read_text())['workflows'][-1]
    record['workflow']='another';record['artifacts']=[dict(a,path=a['path']+'-another') for a in record['artifacts']]
    monkeypatch.setattr(os,'statvfs',lambda _:SimpleNamespace(f_bavail=30*1024**3-1,f_frsize=1))
    before=cat.read_bytes()
    with pytest.raises(ValueError):api['register'](str(cat),record)
    assert cat.read_bytes()==before and (old/'sentinel').read_text()=='preserve old build'
