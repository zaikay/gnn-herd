"""Verify completed B campaign/evaluation on CPU, without forward passes or fits."""
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits


def main():
    import torch
    from models.b_validation import ROOT,ORDER,SEEDS,fit_path
    from evaluation.b_gate_c import require_release,load_predictions,OUT,dm_family
    from evaluation.gate_c_io import context_from_panel,load_baselines
    from evaluation.gate_c_metrics import evaluate,compare
    from evaluation.gate_c_findings import findings
    torch.set_num_threads(1)
    cfg,info=require_release(); ctx=context_from_panel(cfg)
    totals=[]; checkpoint_count=0
    for condition in ORDER:
        marker=json.loads((ROOT/condition/'condition_complete.json').read_text())
        records=pd.read_csv(ROOT/condition/'fit_records.csv')
        np.testing.assert_allclose(records.fit_seconds.sum()/3600,marker['recorded_fit_hours'])
        np.testing.assert_allclose(records.loc[~records.reused_screen,'fit_seconds'].sum()/3600,marker['new_fit_hours'])
        for origin in dict.fromkeys(ctx.fit_origins):
            for seed in SEEDS:
                path=fit_path(condition,seed,origin)
                saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
                assert saved['completed_epochs']==saved['total_epochs']==65
                for value in saved['model'].values():
                    assert value.device.type=='cpu'
                    if value.is_floating_point():
                        assert torch.isfinite(value.coalesce().values() if value.is_sparse else value).all()
                curve=pd.read_csv(path/'training_curve.csv'); assert curve.epoch.tolist()==list(range(1,66))
                checkpoint_count+=1
        totals.append(marker)
    with threadpool_limits(limits=1):
        b,_=load_predictions(ctx); baseline,_,_=load_baselines(cfg,ctx)
        recomputed=evaluate({**baseline,**b},ctx)
        saved_scores=pd.read_csv(OUT/'scores.csv',dtype={'outcome':str})
        keys=['model','outcome','group']
        left=saved_scores.set_index(keys).sort_index(); right=recomputed['scores'].set_index(keys).sort_index()
        assert left.index.equals(right.index)
        np.testing.assert_allclose(left,right,rtol=1e-11,atol=1e-10)
        saved_seed=pd.read_csv(OUT/'seed_metrics.csv',dtype={'outcome':str}).set_index(['model','seed','outcome','group']).sort_index()
        new_seed=recomputed['seed'].set_index(['model','seed','outcome','group']).sort_index()
        np.testing.assert_allclose(saved_seed,new_seed,rtol=1e-11,atol=1e-10)
        dm=compare(recomputed['origin'],True)
        old_dm=pd.read_csv(OUT/'dm_tests.csv',dtype={'outcome':str})
        assert len(dm)==len(dm_family())==20 and set(map(tuple,dm[['model_a','model_b','outcome']].to_numpy()))==set(dm_family())
        np.testing.assert_allclose(dm[['statistic','p_raw','p_holm']],old_dm[['statistic','p_raw','p_holm']],rtol=1e-10,atol=1e-12,equal_nan=True)
    report=Path('reports/experiments/b_validation.md')
    links=re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8'))
    for link in links:
        if not link.startswith('http'):assert (report.parent/link).exists(),link
    figure_count=0
    for root in [Path('visuals/t03/b_validation'),Path('data/explore/t03/b_validation'),Path('reports/figures/b_validation')]:
        for path in root.glob('*.png'):
            assert path.with_suffix('.csv').exists()
            assert path.stat().st_size<5_000_000
            figure_count+=1
    answer,comparison=findings(saved_scores,dm)
    summary={'conditions':totals,'fit_identities_and_checkpoints_checked':checkpoint_count,
        'new_fits':sum(m['fits']-m['reused'] for m in totals),'reused_screen_fits':sum(m['reused'] for m in totals),
        'new_fit_hours':sum(m['new_fit_hours'] for m in totals),'fit_hours_including_reused':sum(m['recorded_fit_hours'] for m in totals),
        'score_rows_reproduced':len(saved_scores),'seed_rows_reproduced':len(saved_seed),'dm_family_size':20,
        'figures_with_csv_checked':figure_count,'report_links_checked':len(links),'gate_c_report_finding':answer,
        'real_vs_shuffled':comparison.to_dict('records'),'gpu_use_by_audit':False,'new_fits_by_audit':0,'sealed_test_forecasts_or_losses':0}
    Path('reports/experiments/t03_b_completion_verification.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
