"""CPU-only completion audit from saved screen forecasts/checkpoints; no forward pass."""
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd


def main():
    import torch
    from models.architecture_screen import ROOT,ANCHORS,jobs,output,fingerprint
    from models.screen_architectures import ScreenNetwork
    from evaluation.gate_c_io import context_from_panel
    from features.panel import load_panel
    torch.set_num_threads(1)
    cfg,expected=fingerprint(); actual=json.loads((ROOT/'gpu_manifest.json').read_text())
    assert all(actual[k]==v for k,v in expected.items())
    assert actual['hardware']==json.loads(Path('data/processed/t03_gnn/machine.json').read_text())
    ctx=context_from_panel(cfg)
    metrics=pd.read_csv('data/explore/t03/architecture_screen/origin.csv',dtype={'outcome':str})
    fits=pd.read_csv('data/explore/t03/architecture_screen/fits.csv')
    selected=pd.read_csv('data/explore/t03/architecture_screen/selection.csv')
    monthly={}; checked=0
    for candidate,anchor,condition in jobs():
        path=output(candidate,anchor,condition)
        saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
        assert saved['completed_epochs']==saved['total_epochs']==65
        assert all(v.device.type=='cpu' for v in saved['model'].values())
        curve=pd.read_csv(path/'training_curve.csv'); assert curve.epoch.tolist()==list(range(1,66))
        panel=load_panel(through=anchor)
        model=ScreenNetwork(candidate,panel.edges,panel.observed,64,condition=='real')
        model.load_state_dict(saved['model'],strict=True)
        assert all(torch.isfinite(p).all() for p in model.parameters())
        complete=json.loads((path/'complete.json').read_text())
        assert sum(p.numel() for p in model.parameters())==complete['parameter_count']
        assert complete['test_forecasts_or_losses']==0
        np.testing.assert_allclose(curve.training_poisson_loss.iloc[-1],complete['training_loss'])
        with np.load(path/'prediction.npz',allow_pickle=False) as data:
            np.testing.assert_array_equal(data['codes'],ctx.codes)
            assert str(data['origin'])==anchor
            pred=data['prediction'].copy()
        assert pred.shape==(2634,12) and np.isfinite(pred).all() and (pred>=0).all()
        i=list(ctx.origins).index(anchor); error=pred.astype(float)-ctx.truth[i]
        monthly[candidate,anchor,condition]=float(np.abs(error).mean())
        part=metrics.loc[metrics.model.eq(f'{candidate}_{condition}')&metrics.origin.eq(anchor)&metrics.group.eq('all')&metrics.outcome.ne('total_12')].copy()
        part['h']=part.outcome.astype(int); part=part.sort_values('h')
        np.testing.assert_allclose(part.mae,np.abs(error).mean(axis=0),rtol=1e-12)
        np.testing.assert_allclose(part.rmse,np.sqrt(np.square(error).mean(axis=0)),rtol=1e-12)
        checked+=12
    for row in selected.itertuples():
        np.testing.assert_allclose(row.mae,np.mean([monthly[row.candidate,a,'real'] for a in ANCHORS]),rtol=1e-12)
        assert row.beats_own_no_graph_both_anchors==all(monthly[row.candidate,a,'real']<monthly[row.candidate,a,'no_graph'] for a in ANCHORS)
    eligible=selected.loc[selected.mae<=selected.mae.min()*1.02]
    chosen=eligible.sort_values(['cost_seconds','mae','candidate']).iloc[0].candidate
    assert chosen==json.loads((ROOT/'selection.json').read_text())['selected']=='B'
    bands=pd.read_csv('data/explore/t03/architecture_screen/anchor_band_scores.csv')
    baseline=bands.loc[bands.model.str.endswith('_frozen')&bands.anchor.eq('both_anchors')&bands.band.eq('1-12')&bands.group.eq('all')]
    projection=pd.read_csv('data/explore/t03/architecture_screen/campaign_projection.csv')
    core=projection.loc[projection.condition.ne('optional_without_base')]
    report=Path('reports/experiments/t03_architecture_screen.md')
    for link in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')):
        if not link.startswith('http'):assert (report.parent/link).exists(),link
    result={'completed_gpu_fits':12,'checkpoint_epochs':65,'retained_checkpoints':12,
        'monthly_mae_and_rmse_rows_checked':checked,'fit_hours':float(fits.fit_seconds.sum()/3600),
        'selected':'B','candidate_c_mae_advantage_over_b_percent':float((selected.loc[selected.candidate.eq('B'),'mae'].iloc[0]/selected.mae.min()-1)*100),
        'b_real_anchor_mae':{a:monthly['B',a,'real'] for a in ANCHORS},
        'b_no_graph_anchor_mae':{a:monthly['B',a,'no_graph'] for a in ANCHORS},
        'frozen_baseline_anchor_mean_mae':dict(zip(baseline.model,baseline.mae)),
        'core_campaign_remaining_fits':int(core.remaining_fits.sum()),
        'core_campaign_remaining_fit_hours':float(core.remaining_projected_fit_hours.sum()),
        'optional_ablation_projected_fit_hours':float(projection.loc[projection.condition.eq('optional_without_base'),'remaining_projected_fit_hours'].iloc[0]),
        'gpu_use_by_audit':False,'new_fits':0,'sealed_test_forecasts_or_losses':0}
    Path('reports/experiments/t03_screen_completion_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
