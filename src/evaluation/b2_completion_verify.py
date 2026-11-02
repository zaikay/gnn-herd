"""Saved-artifact B2 completion/epoch audit on CPU; no model forward or fitting."""
import hashlib
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd


def main():
    import torch
    from models.b2_screen import ROOT,path_for,choose_epochs,selected_real_mae
    from models.screen_cpu import ANCHORS
    torch.set_num_threads(1)
    manifest=json.loads((ROOT/'manifest.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in manifest['sources'].items())
    assert hashlib.sha256(Path('reports/protocol/protocol_v5_b2_screen.md').read_bytes()).hexdigest()==manifest['note_sha256']
    selected=json.loads((ROOT/'selection.json').read_text()); decision=json.loads((ROOT/'epoch_decision.json').read_text())
    chosen=selected['config_id']
    expected=[(i,a,'real',65) for i in range(6) for a in ANCHORS]
    expected += [(chosen,a,'no_graph',65) for a in ANCHORS]
    expected += [(chosen,a,c,100) for a in ANCHORS for c in ('real','no_graph')]
    records=[]
    for i,anchor,condition,epochs in expected:
        path=path_for(i,anchor,condition,epochs)
        record=json.loads((path/'complete.json').read_text()); records.append(record)
        checkpoint=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
        assert checkpoint['completed_epochs']==checkpoint['total_epochs']==epochs
        for value in checkpoint['model'].values():
            assert value.device.type=='cpu'
            if value.is_floating_point():assert torch.isfinite(value.coalesce().values() if value.is_sparse else value).all()
        curve=pd.read_csv(path/'training_curve.csv'); assert curve.epoch.tolist()==list(range(1,epochs+1))
        with np.load(path/'prediction.npz',allow_pickle=False) as data:
            assert data['prediction'].shape==(2634,12) and np.isfinite(data['prediction']).all() and (data['prediction']>=0).all()
            assert data['scale'].shape==(2641,) and (data['scale']>=1).all()
            assert str(data['origin'])==anchor
        if epochs==100 and record['mode']=='continuation65':
            origin=json.loads((path/'continuation.json').read_text())
            assert hashlib.sha256(Path(origin['source']).read_bytes()).hexdigest()==origin['sha256']
            old=pd.read_csv(path_for(i,anchor,condition,65)/'training_curve.csv')
            np.testing.assert_array_equal(curve.training_poisson_loss.iloc[:65],old.training_poisson_loss)
    mae65=selected_real_mae(chosen,65); mae100=selected_real_mae(chosen,100)
    np.testing.assert_allclose([mae65,mae100],[decision['mae65'],decision['mae100']],rtol=1e-12)
    assert decision['selected_epochs']==choose_epochs(mae65,mae100) and not decision['pending_100']
    assert set(decision['applies_to'])=={'real','no_graph','learned_graph','identity_control'}
    frame=pd.DataFrame(records)
    primary_hours=frame.loc[frame.epochs.eq(65),'fit_seconds'].sum()/3600
    extension_hours=frame.loc[frame.epochs.eq(100),'new_segment_seconds'].sum()/3600
    scores=pd.read_csv('data/explore/t03/b2_screen/scores.csv',dtype={'outcome':str})
    monthly=scores.loc[scores.group.eq('all')&scores.outcome.ne('total_12')].groupby('model').mae.mean().to_dict()
    report=Path('reports/experiments/b2_screen.md')
    for link in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')):
        if not link.startswith('http'):assert (report.parent/link).exists(),link
    result={'primary_fits':14,'extensions':4,'retained_checkpoints':len(records),'selected_config_id':chosen,
        'selected_configuration':selected['configuration'],'selected_epochs':decision['selected_epochs'],
        'mae65':mae65,'mae100':mae100,'relative_improvement_percent':100*(mae65-mae100)/mae65,
        'primary_fit_hours':float(primary_hours),'additional_extension_hours':float(extension_hours),
        'total_fit_hours_without_double_counting':float(primary_hours+extension_hours),
        'mean_monthly_mae_by_model':monthly,'gpu_use_by_audit':False,'study_fits_by_audit':0,'test_forecasts_or_losses':0}
    Path('reports/experiments/t03_b2_completion_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
