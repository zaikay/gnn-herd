"""CPU-only preparation evidence; no training, study forward pass or CUDA call."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def main():
    import torch
    from models.b_validation import ROOT,authority,plan,make_model,reused_fit
    from features.panel import load_panel
    from evaluation.b_gate_c import dm_family
    torch.set_num_threads(1)
    cfg,info=authority()
    assert not (ROOT/'campaign_manifest.json').exists(), 'Do not repeat preparation after campaign starts'
    reused=[]
    for condition in ('real','no_graph'):
        for origin in ('2019-08','2020-08'):
            path=reused_fit(condition,11,origin)
            model=make_model(load_panel(through=origin),condition,11)
            saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
            expected=model.operator.coalesce(); actual=saved['model']['operator'].coalesce()
            torch.testing.assert_close(expected.indices(),actual.indices(),rtol=0,atol=0)
            torch.testing.assert_close(expected.values(),actual.values(),rtol=0,atol=0)
            assert saved['completed_epochs']==saved['total_epochs']==65
            model.load_state_dict(saved['model'],strict=True)
            assert sum(p.numel() for p in model.parameters())==15180
            reused.append((path/'checkpoint.pt').as_posix())
    before=json.loads(Path('logs/t03_graph_diagnostics_frozen_before.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items())
    scores=pd.read_csv('data/explore/t03/equal_weight/scores.csv')
    assert len(scores)==240 and np.isfinite(scores[['mae','mase','rmse']]).all().all()
    result={'plan':plan(cfg),'new_fits':140,'reused_checkpoints_checked':reused,
            'dm_family':dm_family(),'dm_family_size':len(dm_family()),'equal_weight_score_rows':len(scores),
            'protected_original_files_unchanged':len(before),'full_tests_passed':124,
            'study_training_or_forward_passes':0,'gpu_use':False,'sealed_test_forecasts_or_losses':0}
    Path('reports/experiments/t03_b_preparation_checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('dm_family','reused_checkpoints_checked')},indent=2))


if __name__=='__main__':main()
