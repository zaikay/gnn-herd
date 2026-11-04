"""EXPLORATORY section 7: origin halves and control claim checks, saved losses only."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from evaluation.test_exploratory import scores,gains,SCOPE,OUT,FINAL,OWN,NEIGH

MODELS=(OWN,NEIGH,'B2_real','B2_no_graph','B2_shuffled','B2_without_base','combination','combination_no_graph_sensitivity')
HALVES=(('2022-10','2023-09'),('2023-10','2024-09'))
REPORTED=('1','6','12','total_12')

def half_scores(origin):
    """Equal-origin losses, root after pooling squared errors; require exact coverage."""
    data=origin.loc[origin.group.eq('all')&origin.outcome.isin(REPORTED)].copy()
    if set(data.model)!=set(MODELS):raise ValueError('Missing or unexpected models')
    if data.duplicated(['model','outcome','origin']).any():raise ValueError('Duplicate origin loss')
    result=[]
    for start,end in HALVES:
        selected=data.loc[data.origin.between(start,end)]
        expected=set(pd.period_range(start,end,freq='M').astype(str))
        for model in MODELS:
            for outcome in REPORTED:
                part=selected.loc[selected.model.eq(model)&selected.outcome.eq(outcome)]
                if set(part.origin)!=expected:raise ValueError('Incomplete half calendar')
                result.append(dict(model=model,outcome=outcome,group='all',first_origin=start,last_origin=end,origins=len(part),
                    mae=part.mae.mean(),rmse=float(np.sqrt(part.mse.mean())),mean_signed_error=part.mean_signed_error.mean()))
    if set(data.origin)!=set(pd.period_range('2022-10','2024-09',freq='M').astype(str)):raise ValueError('Unexpected test calendar')
    return pd.DataFrame(result)

def main():
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):run()

def run():
    locked=json.loads((FINAL/'complete.json').read_text())
    def verify():
        for path,digest in locked['artifact_sha256'].items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise ValueError('Confirmatory artifact changed')
    verify()
    source=FINAL/'ensemble_origin.csv.gz'
    origin=pd.read_csv(source,dtype={'outcome':str})
    halves=half_scores(origin)
    controls=gains(scores(origin),('B2_no_graph','B2_shuffled','B2_without_base'),(OWN,NEIGH))
    assert len(halves)==64 and len(controls)==936
    flags=controls.loc[controls.not_lower]
    summary=controls.groupby(['candidate','reference','metric','group'],as_index=False).agg(cells=('not_lower','size'),not_lower_cells=('not_lower','sum'),minimum_gain_percent=('gain_percent','min'),maximum_gain_percent=('gain_percent','max'))
    for name,frame in [('exploratory_half_scores',halves),('exploratory_control_claim_checks',controls),('exploratory_control_claim_flags',flags),('exploratory_control_claim_summary',summary)]:
        frame=frame.copy();frame.insert(0,'scope',SCOPE);frame.to_csv(OUT/(name+'.csv'),index=False)
    from visuals.test_exploratory_halves import render
    render(halves,OUT)
    from evaluation.graph_diagnostics_report import table
    section='## EXPLORATORY 7. Test-origin halves and B2 control claim checks\n\n'
    section+='EXPLORATORY, post-test, saved three-seed forecast-ensemble losses only. Halves split **forecast origins**, not target months: October 2022-September 2023 and October 2023-September 2024, twelve origins each. Their target windows overlap; these are descriptive strata, not independent experiments or a change to the final test. No fits, new tests of significance, tuning or confirmatory changes.\n\n'
    section+='### EXPLORATORY 7.1 All-area half scores\n\nEqual-origin MAE and signed error; RMSE = square root of mean origin MSE. Signed error = forecast minus actual. Monthly units: systems/area/month; total units: systems/area/twelve-month window. All eight models and four outcomes are shown.\n\n'+table(halves)+'\n\n'
    section+='![EXPLORATORY half scores](../../data/explore/t03/test_exploratory/exploratory_half_scores.png)\n\n'
    section+=f'### EXPLORATORY 7.2 Control claim checks\n\nOf **{len(controls)}** control/reference/metric/maturity/outcome cells, **{len(flags)}** are not strictly lower. Ties count as not lower. Percentage gain = 100(reference-candidate)/reference; undefined for zero reference. Checks cover all 12 monthly horizons and the total, all areas plus dynamic maturity terciles, MAE/MASE/RMSE. MASE denominators are inherited unchanged. The summary ranges below include the total; complete values and every flagged cell are supplied in the CSVs.\n\n'+table(summary)+'\n\n'
    for name in ['exploratory_half_scores','exploratory_control_claim_checks','exploratory_control_claim_flags','exploratory_control_claim_summary']:
        section+=f'- [EXPLORATORY {name} CSV](../../data/explore/t03/test_exploratory/{name}.csv)\n'
    section+='\nGenerators: `evaluation.test_exploratory_halves`, `visuals.test_exploratory_halves`. Log: `logs/t03_test_exploratory_halves.log`. [EXPLORATORY provenance](../../data/explore/t03/test_exploratory/exploratory_halves_provenance.json).\n\n'
    report=Path('reports/experiments/test_exploratory.md');text=report.read_text(encoding='utf-8')
    marker='## EXPLORATORY complete outputs and provenance'
    if '## EXPLORATORY 7.' in text:
        start=text.index('## EXPLORATORY 7.');end=text.index(marker,start);text=text[:start]+text[end:]
    assert marker in text
    report.write_text(text.replace(marker,section+marker,1),encoding='utf-8')
    verify()
    provenance={'scope':SCOPE,'input':str(source),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'half_rows':len(halves),'control_claim_cells':len(controls),'control_not_lower_cells':len(flags),'confirmatory_artifacts_unchanged':len(locked['artifact_sha256']),'fits':0,'gpu':False,'target_access':False,
        'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['src/evaluation/test_exploratory_halves.py','src/visuals/test_exploratory_halves.py']}}
    (OUT/'exploratory_halves_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    index=OUT/'index.md';old=index.read_text(encoding='utf-8');old='\n'.join(line for line in old.splitlines() if not any(n in line for n in ['exploratory_half_scores','exploratory_control_claim','exploratory_halves_provenance']))
    names=['exploratory_half_scores.png','exploratory_half_scores.csv','exploratory_control_claim_checks.csv','exploratory_control_claim_flags.csv','exploratory_control_claim_summary.csv','exploratory_halves_provenance.json']
    index.write_text(old+'\n'+'\n'.join(f'- EXPLORATORY [{n}]({n}); evaluation.test_exploratory_halves / visuals.test_exploratory_halves.' for n in names)+'\n',encoding='utf-8')
    print(json.dumps(provenance,indent=2))

if __name__=='__main__':main()
