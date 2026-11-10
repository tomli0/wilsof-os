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
