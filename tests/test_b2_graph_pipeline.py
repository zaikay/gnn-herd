import numpy as np
import pandas as pd
import pytest
from evaluation.b2_graph_screen_report import summarise
from evaluation.gate_c_metrics import Context
from evaluation.b2_gate_c import compare
from evaluation.b2_campaign_plan import dm_family


def context(n=2):
    origins=pd.period_range('2019-01',periods=n,freq='M').astype(str).to_numpy()
    return Context(origins,np.array(['0001','0002','0003']),np.full((n,3,12),4.),
        np.ones((n,3)),np.tile([0,1,2],(n,1)),np.array([[0,1]]),origins)


def test_synthetic_screen_scores_and_main_fallback():
    ctx=context(); values={name:{11:np.full(ctx.truth.shape,value)} for name,value in
        [('real',8.),('no_graph',9.),('learned',7.97),('identity',7.96)]}
    bundle,decision=summarise(values,ctx)
    assert decision['main']=='real' and not decision['requires_researcher_review']
    assert len(bundle['scores'])==4*13*4
    assert set(bundle['origin'].group)=={'all','low','medium','high'}
    assert np.isclose(bundle['scores'].query("model=='real' and outcome=='1' and group=='all'").mae.iloc[0],4)


@pytest.mark.parametrize('include',[False,True])
def test_synthetic_full_family_and_Holm_slots(include,monkeypatch):
    import evaluation.dm
    calls=[]
    def dm(a,b,h):
        calls.append((a,b,h))
        if len(calls)==2:raise ValueError('Synthetic undefined slot')
        return 1.,.01
    monkeypatch.setattr(evaluation.dm,'dm_from_losses',dm)
    main='learned' if include else 'real'; decision={'main':main,'include_learned_and_identity':include}
    names={m for a,b,h in dm_family(main,include) for m in (a,b)}
    records=[{'model':m,'seed':s,'origin':o,'outcome':h,'group':'all','mae':i+1.}
        for m in sorted(names) for s in (11,29,47) for i,o in enumerate(context(36).origins) for h in ('1','6','12','total_12')]
    result=compare(pd.DataFrame(records),decision)
    size=28 if include else 20
    assert len(result)==len(calls)==size
    assert result.p_raw.isna().sum()==1
    assert np.allclose(result.p_holm.dropna(),size*.01)
    assert all(len(a)==36 for a,b,h in calls)


def test_campaign_refuses_before_screen_without_gpu(monkeypatch,tmp_path):
    import models.b2_runtime as runtime
    monkeypatch.setattr(runtime,'SCREEN',tmp_path)
    with pytest.raises(RuntimeError,match='four-fit'):runtime.require_screen()
