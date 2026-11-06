"""EXPLORATORY section 8: frozen-weight network sensitivities, no fitting."""
from dataclasses import replace
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from evaluation.test_exploratory import SCOPE,OUT,FINAL,OWN,NEIGH,scores,gains
from evaluation.final_test_metrics import fixed_combination,forecast_ensembles

NEW='combination_without_base_sensitivity'
PAIRS=(('combination','B2_real'),('combination_no_graph_sensitivity','B2_no_graph'),(NEW,'B2_without_base'))
PERIODS=(('full_test','2022-10','2024-09'),('first_half','2022-10','2023-09'),('second_half','2023-10','2024-09'))

def period_scores(origin):
    if origin.duplicated(['model','group','outcome','origin']).any():raise ValueError('Duplicate origin cells')
    frames=[]
    for name,start,end in PERIODS:
        selected=origin.loc[origin.origin.between(start,end)]
        expected=set(pd.period_range(start,end,freq='M').astype(str))
        for _,part in selected.groupby(['model','group','outcome']):
            if set(part.origin)!=expected:raise ValueError('Incomplete origin period')
        frame=scores(selected);frame['period']=name;frame['origins']=len(expected);frames.append(frame)
    return pd.concat(frames,ignore_index=True)

def main():
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):run()

def run():
    from models.final_test_runtime import authorize,PANEL,ROOT,calendar,sha
    from features.sealed_panel import load_prefix
    from evaluation.final_test import context
    from evaluation.gate_c_metrics import evaluate
    permit=authorize();locked=json.loads((FINAL/'complete.json').read_text())
    if permit.signature!=locked['signature']:raise ValueError('Final evaluation signature mismatch')
    def verify():
        for path,digest in locked['artifact_sha256'].items():
            if sha(path)!=digest:raise ValueError('Confirmatory artifact changed')
    verify();inputs={};runs={};identifiers=[]
    for model in (NEIGH,'B2_real','B2_no_graph','B2_without_base'):
        runs[model]={}
        for seed in permit.spec['seeds']:
            path=ROOT/model/f'predictions_seed{seed}.npz';digest=sha(path)
            if digest!=locked['forecast_sha256'][str(path)]:raise ValueError('Forecast changed')
            inputs[str(path)]=digest
            with np.load(path,allow_pickle=False) as d:
                runs[model][seed]=d['prediction'].copy();identifiers.append((d['origins'].copy(),d['codes'].copy()))
    # The test is already released/evaluated. Read only through its existing last target.
    panel=load_prefix(PANEL,permit.spec['last_target'],replace(permit,max_month=permit.spec['last_target']))
    ctx=context(panel,calendar(permit.spec['first_origin'],permit.spec['last_origin']),permit.cfg)
    for dates,codes in identifiers:
        np.testing.assert_array_equal(dates,ctx.origins);np.testing.assert_array_equal(codes,ctx.codes)
    point=forecast_ensembles(runs,permit.spec['seeds'])
    hybrids={hybrid:fixed_combination(point[NEIGH],point[network],ctx.groups,permit.spec['weights']) for hybrid,network in PAIRS}
    evaluated=evaluate({name:{'ensemble':pred} for name,pred in hybrids.items()},ctx,seeds=('ensemble',))
    saved=pd.read_csv(FINAL/'ensemble_origin.csv.gz',dtype={'outcome':str})
    keys=['model','origin','outcome','group'];columns=['mae','mase','mse','mean_signed_error']
    # Independently reproduce both existing hybrids before scoring the new sensitivity.
    a=evaluated['origin'].loc[lambda d:d.model.ne(NEW)].set_index(keys).sort_index()
    b=saved.loc[saved.model.isin([p[0] for p in PAIRS[:2]])].set_index(keys).sort_index()
    np.testing.assert_allclose(a[columns],b[columns],rtol=1e-10,atol=1e-10)
    origin=pd.concat([saved.loc[saved.model.isin([OWN,NEIGH,'B2_real','B2_no_graph','B2_without_base'])],evaluated['origin']],ignore_index=True)
    all_scores=period_scores(origin);claims=[];contrasts=[]
    for period,part in all_scores.groupby('period'):
        d=gains(part,('combination_no_graph_sensitivity',NEW),(OWN,NEIGH));d['period']=period;claims.append(d)
        for hybrid,network in PAIRS:
            d=gains(part,(hybrid,),(network,));d['period']=period
            signed=part.set_index(['model','outcome','group']).mean_signed_error
            d['hybrid_signed_error']=[signed.loc[(hybrid,o,g)] for o,g in zip(d.outcome,d.group)]
            d['network_signed_error']=[signed.loc[(network,o,g)] for o,g in zip(d.outcome,d.group)]
            contrasts.append(d)
    claims=pd.concat(claims,ignore_index=True);contrasts=pd.concat(contrasts,ignore_index=True)
    flags=claims.loc[claims.not_lower];summary=claims.groupby(['period','candidate','reference','metric'],as_index=False).agg(cells=('not_lower','size'),not_lower_cells=('not_lower','sum'))
    outputs={}
    for name,frame in [('exploratory_hybrid_sensitivity_scores',all_scores),('exploratory_hybrid_sensitivity_claims',claims),('exploratory_hybrid_sensitivity_flags',flags),('exploratory_hybrid_sensitivity_summary',summary),('exploratory_hybrid_network_comparison',contrasts)]:
        frame=frame.copy();frame.insert(0,'scope',SCOPE);frame.to_csv(OUT/(name+'.csv'),index=False);outputs[name]=frame
    weights=pd.DataFrame([dict(scope=SCOPE,maturity=g,band=band,boosting_weight=w,network_weight=1-w) for g,bands in permit.spec['weights'].items() for band,w in bands.items()]);weights.to_csv(OUT/'exploratory_sensitivity_frozen_weights.csv',index=False)
    from visuals.test_exploratory_hybrids import render
    render(all_scores,OUT)
    from evaluation.graph_diagnostics_report import table
    section='## EXPLORATORY 8. Frozen-weight hybrid sensitivities\n\n5 November 2026. EXPLORATORY post-test sensitivity, no fits or weight estimation. New hybrid = w times neighbour boosting ensemble + (1-w) times B2 without-installed-base ensemble. The same nine frozen six-decimal weights and origin-dependent maturity/bands are used in all three hybrid versions. Three seed forecasts are averaged before mixing/scoring. No confirmatory result, model choice or testing chain changes.\n\n'
    section+='### EXPLORATORY 8.1 Frozen weights and scoring\n\n'+table(weights.drop(columns='scope'))+'\n\n'
    section+='Every horizon 1-12 and the twelve-month total, all areas and each dynamic maturity tercile, are scored for the full test and both twelve-origin halves. MAE/MASE/signed errors average equal-area origin losses; RMSE roots pooled MSE. Total MASE divides by twelve times the monthly training scale. Monthly MAE/RMSE/signed-error units are systems/area/month; total units systems/area/twelve-month window; MASE is unitless. Halves split origins, so target windows overlap. Saved forecasts are unchanged; only already-evaluated targets through September 2025 are reread for the new mixture. Main and no-graph hybrids reproduce all four saved origin-level loss columns within 1e-10 tolerance.\n\n'
    section+='EXPLORATORY all-area overview, horizons 1,6,12,total (complete monthly/maturity scores linked below):\n\n'+table(all_scores.loc[all_scores.model.isin([p[0] for p in PAIRS])&all_scores.group.eq('all')&all_scores.outcome.isin(['1','6','12','total_12'])][['period','model','outcome','mae','mase','rmse','mean_signed_error']])+'\n\n'
    section+='![EXPLORATORY hybrid sensitivities](../../data/explore/t03/test_exploratory/exploratory_hybrid_sensitivities.png)\n\n'
    section+=f'### EXPLORATORY 8.2 Claim checks\n\nFor the two sensitivity hybrids against both boosting ensembles, **{len(flags)} of {len(claims)}** metric/reference/maturity/outcome/period cells are not strictly lower. Ties are flagged. All flagged cells are supplied separately. These include full-test and both half-period checks; no p-values or new significance tests are computed. Percentage gain = 100(reference-candidate)/reference, undefined for zero reference.\n\n'+table(summary)+'\n\n'
    section+='### EXPLORATORY 8.3 Each hybrid against its own network\n\nPositive gains indicate lower hybrid error. The table shows full-test all-area values at 1,6,12,total; the complete CSV covers all horizons, maturity groups and both halves, and includes signed errors for each member.\n\n'+table(contrasts.loc[contrasts.period.eq('full_test')&contrasts.group.eq('all')&contrasts.outcome.isin(['1','6','12','total_12'])])+'\n\n'
    for name in outputs:section+=f'- [EXPLORATORY {name}](../../data/explore/t03/test_exploratory/{name}.csv)\n'
    section+='\n[EXPLORATORY exact weights](../../data/explore/t03/test_exploratory/exploratory_sensitivity_frozen_weights.csv). [EXPLORATORY provenance](../../data/explore/t03/test_exploratory/exploratory_hybrid_sensitivity_provenance.json). Generators: `evaluation.test_exploratory_hybrids`, `visuals.test_exploratory_hybrids`; log `logs/t03_test_exploratory_hybrids.log`.\n\n'
    report=Path('reports/experiments/test_exploratory.md');text=report.read_text(encoding='utf-8');marker='## EXPLORATORY complete outputs and provenance'
    if '## EXPLORATORY 8.' in text:
        start=text.index('## EXPLORATORY 8.');end=text.index(marker,start);text=text[:start]+text[end:]
    assert marker in text;report.write_text(text.replace(marker,section+marker,1),encoding='utf-8');verify()
    provenance=dict(scope=SCOPE,input_sha256=inputs,weights=permit.spec['weights'],panel_sha256=sha(PANEL),last_target=permit.spec['last_target'],score_rows=len(all_scores),claim_cells=len(claims),not_lower_cells=len(flags),confirmatory_artifacts_unchanged=len(locked['artifact_sha256']),fits=0,gpu=False,saved_main_and_no_graph_origin_loss_reproduction=True,
        source_sha256={p:sha(p) for p in ['src/evaluation/test_exploratory_hybrids.py','src/visuals/test_exploratory_hybrids.py']})
    (OUT/'exploratory_hybrid_sensitivity_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    names=[n+'.csv' for n in outputs]+['exploratory_sensitivity_frozen_weights.csv','exploratory_hybrid_sensitivities.png','exploratory_hybrid_sensitivities.csv','exploratory_hybrid_sensitivity_provenance.json']
    index=OUT/'index.md';old=index.read_text(encoding='utf-8');old='\n'.join(line for line in old.splitlines() if not any(n in line for n in names));index.write_text(old+'\n'+'\n'.join(f'- EXPLORATORY [{n}]({n}); evaluation.test_exploratory_hybrids / visuals.test_exploratory_hybrids.' for n in names)+'\n',encoding='utf-8')
    for name in names:assert (OUT/name).stat().st_size<5_000_000
    print(json.dumps(provenance,indent=2))

if __name__=='__main__':main()
