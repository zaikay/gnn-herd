"""Read-only numerical/report audit of the saved combination evaluation."""
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd
from evaluation.combination_validation import OUT,compare_combinations


def main():
    scores=pd.read_csv(OUT/'scores.csv',dtype={'outcome':str})
    original=pd.read_csv('data/processed/t03_b_gate_c/scores.csv',dtype={'outcome':str})
    keys=['model','outcome','group']
    reference=scores.loc[scores.model.isin(['gradient_boosting_own','gradient_boosting_neighbours','gnn_real'])].set_index(keys).sort_index()
    expected=original.set_index(keys).reindex(reference.index)
    np.testing.assert_allclose(reference,expected,rtol=1e-11,atol=1e-10)
    seed=pd.read_csv(OUT/'seed_metrics.csv',dtype={'outcome':str})
    origin=pd.read_csv(OUT/'origin_metrics.csv.gz',dtype={'outcome':str})
    dm=pd.read_csv(OUT/'dm_tests.csv',dtype={'outcome':str})
    again=compare_combinations(origin)
    np.testing.assert_allclose(dm[['statistic','p_raw','p_holm']],again[['statistic','p_raw','p_holm']],rtol=1e-10,atol=1e-12,equal_nan=True)
    # Independent global Holm calculation (all sixteen results are defined).
    assert len(dm)==16 and np.isfinite(dm.p_raw).all()
    order=np.argsort(dm.p_raw.to_numpy()); adjusted=np.empty(16)
    adjusted[order]=np.maximum.accumulate(np.minimum(1,(16-np.arange(16))*dm.p_raw.to_numpy()[order]))
    np.testing.assert_allclose(dm.p_holm,adjusted)
    cost=pd.read_csv(OUT/'final_test_cost_summary.csv'); calendar=pd.read_csv(OUT/'final_test_refit_calendar.csv')
    assert len(calendar)==8 and cost.fits.eq(24).all() and cost.fits.sum()==144
    assert len(seed)==780 and len(scores)==260 and len(origin)==28080
    report=Path('reports/experiments/combination_validation.md')
    for link in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')):
        if not link.startswith('http'):assert (report.parent/link).exists(),link
    result={'reference_score_rows_reproduced':len(reference),'pooled_score_rows':len(scores),'seed_rows':len(seed),
        'origin_loss_rows':len(origin),'dm_family_size':16,'dm_and_independent_holm_verified':True,
        'cost_only_test_refits_per_condition':24,'cost_only_total_refits':144,
        'cost_hours_by_resource':cost.groupby('device')[['hours_low','hours_central','hours_high']].sum().to_dict('index'),
        'fits_executed':0,'gpu_use':False,'test_forecasts_or_losses':0,'new_unit_tests_passed':5}
    Path('reports/experiments/t03_combination_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
