"""Reserve unallocated bytes once; existing allocation is already absent from free."""
from pathlib import Path
import json
import pytest
from test_artifact_lifecycle import api,request

@pytest.mark.parametrize('margin',[1,-1])
def test_concurrent_reservation_counts_only_unallocated_bytes(tmp_path,monkeypatch,margin):
    m=api();catalog=tmp_path/'catalog.json';old=request(tmp_path,'running');old['budget_bytes']=8192
    m.register(str(catalog),old)
    artifact=Path(old['artifacts'][0]['path']);artifact.write_bytes(b'existing allocation')
    allocated=m.usage(artifact)[0];assert 0<allocated<old['budget_bytes']
    new=request(tmp_path,'small-independent-stage');new['budget_bytes']=1024;new['artifacts'][0]['kind']='evidence'
    available=m.RESERVE+new['budget_bytes']+old['budget_bytes']-allocated+margin
    monkeypatch.setattr(m.os,'statvfs',lambda p:type('Space',(),{'f_bavail':available,'f_frsize':1})())
    before=catalog.read_bytes()
    if margin>0:
        m.register(str(catalog),new)
        assert len(json.loads(catalog.read_text())['workflows'])==2
    else:
        with pytest.raises(ValueError,match='capacity'):m.register(str(catalog),new)
        assert catalog.read_bytes()==before
    assert artifact.read_bytes()==b'existing allocation' and not Path(new['artifacts'][0]['path']).exists()
