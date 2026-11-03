"""Audit retained B2 condition artifacts on CPU, without scoring forecasts."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from models.b2_runtime import CAMPAIGN,authority,require_screen,screen_artifact_hashes,sha


def verify(condition):
    from evaluation.baselines import validation_rows
    from models.b2_validation import fit_path,reuse_path,conditions
    from models.b2_adaptive import make_model
    from features.panel import load_panel
    from features.b2 import area_scale
    cfg,info=authority(); decision=require_screen()
    assert condition in conditions(decision)
    assert json.loads((CAMPAIGN/'manifest.json').read_text())=={**info,'screen_decision':decision,'screen_artifacts':screen_artifact_hashes()}
    root=CAMPAIGN/condition; marker=json.loads((root/'condition_complete.json').read_text())
    assert marker['condition']==condition and marker['fits']==36 and marker['seeds']==[11,29,47]
    assert marker['epochs']==100 and marker['last_target']=='2022-10' and marker['validation_origins']==36
    assert marker['test_forecasts_or_losses']==0
    rows=validation_rows(cfg); panel=load_panel(through=rows.origin.max())
    records=pd.read_csv(root/'fit_records.csv',dtype={'fit_origin':str})
    expected={(s,o) for s in (11,29,47) for o in rows.fit_origin.unique()}
    assert len(records)==36 and set(zip(records.seed,records.fit_origin))==expected
    hashes={}; reuse_count=0
    for row in records.itertuples():
        path=fit_path(condition,row.seed,row.fit_origin)
        reuse=reuse_path(condition,row.seed,row.fit_origin) is not None
        assert bool(row.reused_screen)==reuse
        reuse_count+=reuse
        saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
        assert saved['completed_epochs']==saved['total_epochs']==100
        assert [r['epoch'] for r in saved['epoch_records']]==list(range(1,101))
        fit_panel=panel.through(row.fit_origin); scale=area_scale(fit_panel,row.fit_origin)
        model=make_model(fit_panel,condition,row.seed,scale)
        model.load_state_dict(saved['model'],strict=True)
        np.testing.assert_array_equal(model.area_scale.numpy(),scale.astype(np.float32))
        assert sum(p.numel() for p in model.parameters())==row.parameter_count
        for tensor in model.state_dict().values():
            assert torch.isfinite(tensor.coalesce().values() if tensor.is_sparse else tensor).all()
        complete=json.loads((path/'complete.json').read_text())
        assert complete['epochs']==100
        np.testing.assert_allclose(complete['fit_seconds'],row.fit_seconds,rtol=1e-12)
        np.testing.assert_allclose(saved['epoch_records'][-1]['training_poisson_loss'],row.training_loss,rtol=1e-12)
        hashes[str(path/'checkpoint.pt')]=sha(path/'checkpoint.pt')
        del model,saved
    assert reuse_count==marker['reused']
    np.testing.assert_allclose(records.fit_seconds.sum()/3600,marker['recorded_fit_hours'],rtol=1e-12)
    np.testing.assert_allclose(records.loc[~records.reused_screen,'fit_seconds'].sum()/3600,marker['new_fit_hours'],rtol=1e-12)
    shapes={}
    for seed in (11,29,47):
        path=root/f'predictions_seed{seed}.npz'
        with np.load(path,allow_pickle=False) as data:
            np.testing.assert_array_equal(data['codes'],panel.codes[panel.observed])
            np.testing.assert_array_equal(data['origins'],rows.origin.to_numpy())
            assert data['prediction'].shape==(36,int(panel.observed.sum()),12)
            assert np.isfinite(data['prediction']).all() and (data['prediction']>=0).all()
            shapes[str(seed)]=list(data['prediction'].shape)
        hashes[str(path)]=sha(path)
    result={'condition':condition,'unique_fits':36,'epochs':100,'reused_screen_fits':reuse_count,
        'new_fit_hours':marker['new_fit_hours'],'recorded_fit_hours_including_reuse':marker['recorded_fit_hours'],
        'forecast_shapes':shapes,'artifact_sha256':hashes,'source_and_reuse_provenance_match':True,
        'gpu_use':False,'new_fits':0,'forecast_losses_computed':False,'test_forecasts_or_losses':0}
    destination=Path(f'reports/experiments/t03_b2_{condition}_completion_verification.json')
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--condition',required=True,choices=('real','shuffled','no_graph','without_base'))
    verify(parser.parse_args().condition)
