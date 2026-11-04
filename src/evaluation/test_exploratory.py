"""EXPLORATORY post-test checks from immutable saved loss tables; no fitting."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
import pandas as pd
from evaluation.v7_chain_evidence import candidate_test
from evaluation.final_test_metrics import hac_interval

SCOPE='EXPLORATORY - post-test; unadjusted descriptive inference'
OUT=Path('data/explore/t03/test_exploratory')
FINAL=Path('data/processed/t03_final_test/evaluation')
OWN='gradient_boosting_own'
NEIGH='gradient_boosting_neighbours'
OUTCOMES=tuple(map(str,range(1,13)))+('total_12',)

def scores(origin):
    result=origin.groupby(['model','outcome','group'],as_index=False)[['mae','mase','mse','mean_signed_error']].mean()
    result['rmse']=np.sqrt(result.mse)
    return result

def gains(frame,candidates,references):
    records=[]
    for candidate in candidates:
        for reference in references:
            a=frame.loc[frame.model.eq(candidate)].set_index(['outcome','group'])
            b=frame.loc[frame.model.eq(reference)].set_index(['outcome','group'])
            if set(a.index)!=set(b.index) or a.index.has_duplicates or b.index.has_duplicates:raise ValueError('Mismatched score cells')
            for key in a.index:
                for metric in ('mae','mase','rmse'):
                    x,y=a.loc[key,metric],b.loc[key,metric]
                    records.append(dict(candidate=candidate,reference=reference,outcome=key[0],group=key[1],metric=metric,
                        candidate_loss=x,reference_loss=y,gain_percent=100*(y-x)/y if y>0 else np.nan,not_lower=bool(x>=y)))
    return pd.DataFrame(records)

def compare(origin,pairs,groups=('all',),outcomes=OUTCOMES):
    records=[]
    for candidate,reference in pairs:
        for group in groups:
            for outcome in outcomes:
                part=origin.loc[origin.group.eq(group)&origin.outcome.eq(outcome)]
                a=part.loc[part.model.eq(candidate)].set_index('origin').mae.sort_index()
                b=part.loc[part.model.eq(reference)].set_index('origin').mae.sort_index()
                if a.index.has_duplicates or b.index.has_duplicates or not a.index.equals(b.index) or not len(a):raise ValueError('Unaligned origin losses')
                h=12 if outcome=='total_12' else int(outcome)
                result=candidate_test(a.to_numpy(),b.to_numpy(),h)
                mean,lo,hi=hac_interval(a.to_numpy()-b.to_numpy(),h)
                records.append(dict(candidate=candidate,reference=reference,group=group,outcome=outcome,origins=len(a),
                    mean_MAE_difference=mean,lower95=lo,upper95=hi,**result))
    return pd.DataFrame(records)

def main():
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):run()

def run():
    # Require the reviewed results commit before any post-test calculation.
    committed=subprocess.run(['git','show','HEAD:reports/experiments/protocol_v7_final_test_results.md'],capture_output=True,check=True).stdout
    report=Path('reports/experiments/protocol_v7_final_test_results.md')
    if committed.replace(b'\r\n',b'\n')!=report.read_bytes().replace(b'\r\n',b'\n'):raise RuntimeError('Commit reviewed results first')
    locked=json.loads((FINAL/'complete.json').read_text())
    for path,digest in locked['artifact_sha256'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise RuntimeError('Confirmatory artifact changed')
    inputs={}
    def read(path):
        path=Path(path);inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        return pd.read_csv(path,dtype={'outcome':str})
    test=read(FINAL/'ensemble_origin.csv.gz')
    validation=read('data/processed/t03_b2_ensemble_combination/ensemble_origin.csv.gz')
    validation['model']=validation.model.replace({OWN+'_ensemble':OWN,NEIGH+'_ensemble':NEIGH})
    individual=read(FINAL/'individual_origin.csv.gz')
    OUT.mkdir(parents=True,exist_ok=True)
    outputs={}
    def save(name,frame):
        frame=frame.copy();frame.insert(0,'scope',SCOPE);frame.to_csv(OUT/(name+'.csv'),index=False);outputs[name]=frame;return frame
    claim=save('exploratory_claim_checks',gains(scores(test),('combination','B2_real'),(OWN,NEIGH)))
    ranges=claim.loc[claim.outcome.ne('total_12')].groupby(['candidate','reference','metric','group'],as_index=False).agg(min_gain_percent=('gain_percent','min'),max_gain_percent=('gain_percent','max'),not_lower_horizons=('not_lower','sum'))
    save('exploratory_gain_ranges',ranges)
    save('exploratory_model_dm',compare(test,[('B2_real',OWN),('B2_real',NEIGH),('combination','B2_real')]))
    neighbour=[]
    for period,data in [('test',test),('validation',validation)]:
        d=compare(data,[(NEIGH,OWN)],('all','low','medium','high'));d['period']=period;neighbour.append(d)
    neighbour=save('exploratory_neighbour_dm',pd.concat(neighbour,ignore_index=True))
    side=neighbour.drop(columns='scope').pivot(index=['group','outcome'],columns='period',values=['candidate_loss','reference_loss','gain_percent','p_two_sided']).reset_index()
    side.columns=['_'.join(filter(None,c)) if isinstance(c,tuple) else c for c in side.columns]
    save('exploratory_neighbour_side_by_side',side)
    metric_parts=[]
    for period,data in [('test',test),('validation',validation)]:
        part=gains(scores(data),(NEIGH,),(OWN,));part['period']=period;metric_parts.append(part)
    metric_side=pd.concat(metric_parts).pivot(index=['group','outcome','metric'],columns='period',values=['candidate_loss','reference_loss','gain_percent','not_lower']).reset_index()
    metric_side.columns=['_'.join(filter(None,c)) if isinstance(c,tuple) else c for c in metric_side.columns]
    save('exploratory_neighbour_metric_side_by_side',metric_side)
    base=save('exploratory_installed_base',compare(test,[('B2_real','B2_without_base')],('all','low','medium','high')))
    save('exploratory_B1_B2',base.loc[base.group.eq('all')&base.outcome.isin(['1','total_12'])].drop(columns='scope').assign(hypothesis=lambda d:d.outcome.map({'1':'B1','total_12':'B2'})))
    effect=gains(scores(test),('B2_without_base',),('B2_real',))
    # Negative gains here mean removal worsens error. Include both signed errors.
    signed=scores(test).loc[lambda d:d.model.isin(['B2_real','B2_without_base']),['model','outcome','group','mean_signed_error']]
    effect=effect.merge(signed.rename(columns={'model':'candidate','mean_signed_error':'removed_base_signed_error'}),on=['candidate','outcome','group']).merge(signed.rename(columns={'model':'reference','mean_signed_error':'real_signed_error'}),on=['reference','outcome','group'])
    save('exploratory_installed_base_effect',effect)
    bias=test.loc[test.group.eq('all')&test.outcome.ne('total_12')&test.model.isin([OWN,NEIGH,'B2_real','combination'])].copy()
    bias['horizon']=bias.outcome.astype(int);bias['target_month']=[str(pd.Period(o,freq='M')+h) for o,h in zip(bias.origin,bias.horizon)]
    save('exploratory_signed_error',bias)
    national=read('data/explore/t02/national_monthly.csv')
    national=national.loc[national.month.between(bias.target_month.min(),bias.target_month.max())]
    save('exploratory_national_actuals',national)
    seed_rows=[]
    for seed in (11,29,47):
        part=individual.loc[individual.seed.eq(seed)]
        gain=gains(scores(part).loc[lambda d:d.group.eq('all')&d.outcome.isin(['1','6','12','total_12'])],('B2_real',),(OWN,NEIGH));gain['seed']=seed;gain['reference_view']='matched individual boosting seed'
        seed_rows.append(gain)
        reference=pd.concat([scores(part).loc[lambda d:d.model.eq('B2_real')],scores(test).loc[lambda d:d.model.isin([OWN,NEIGH])]])
        gain=gains(reference.loc[lambda d:d.group.eq('all')&d.outcome.isin(['1','6','12','total_12'])],('B2_real',),(OWN,NEIGH));gain['seed']=seed;gain['reference_view']='boosting three-seed forecast ensemble';seed_rows.append(gain)
    save('exploratory_seed_robustness',pd.concat(seed_rows,ignore_index=True))
    from visuals.test_exploratory import render
    render(outputs,OUT)
    from evaluation.graph_diagnostics_report import table
    text='# EXPLORATORY post-test analyses\n\n4 November 2026. Every analysis below is exploratory, after review of the final test. No fits, tuning, new weights or confirmatory amendments. Saved forecast-derived loss tables are the inputs; national actuals reuse the existing CER summary. No target matrix is reopened.\n\n'
    text+='## EXPLORATORY conventions\n\nThree-seed forecasts are averaged before scoring in the main test and validation comparisons. Equal-area losses are averaged per origin, then equally over origins. Maturity terciles and training-only MASE denominators are inherited unchanged. RMSE is the square root of pooled MSE, not mean origin RMSE. Total errors score the sum of twelve forecasts. All DM tests use the existing HLN/Bartlett adapter, lag h-1, n-1 t reference; h=12 for total. Negative candidate-minus-reference differences favour the candidate. Pointwise 95% intervals use the approved HAC/HLN-inverted method. Descriptive p-values are two-sided and unadjusted; exploratory B1/B2 lower-tail p-values are also shown. Multiplicity and post-test selection preclude confirmatory interpretation. Undefined values remain missing.\n\n'
    text+='## EXPLORATORY 1. Claim checks\n\nStrictly lower is required: ties and higher errors are flagged `not_lower`. Percentage gain = 100(reference-candidate)/reference; zero denominators are undefined. Ranges below cover monthly horizons 1-12; total is reported separately in the complete cell table. Broad improvement claims must be limited by every flagged cell.\n\n'+table(outputs['exploratory_gain_ranges'].drop(columns='scope'))+'\n\n'
    failures=claim.loc[claim.not_lower]
    text+=f'EXPLORATORY: {len(failures)} of {len(claim)} metric/model/reference/maturity/outcome cells are not lower.\n\n'+table(failures.drop(columns='scope'))+'\n\n'
    for title,name in [('2. B2/boosting and combination/B2 descriptive DM and intervals','exploratory_model_dm'),('3. Neighbour boosting: test and validation side by side','exploratory_neighbour_side_by_side'),('4. Installed-base B1/B2 after the stopped chain','exploratory_B1_B2')]:
        frame=outputs[name].drop(columns='scope').copy()
        for col in frame.columns:
            if col.startswith('p_'):frame[col]=frame[col].map(lambda x:f'{x:.8g}' if np.isfinite(x) else 'undefined')
        text+='## EXPLORATORY '+title+'\n\n'+table(frame)+'\n\n'
    text+='EXPLORATORY B1/B2 do not resume the stopped behavioural chain. Original B1/B2 remain untested confirmatorily. The complete installed-base tables include every maturity/horizon and signed errors for both models. Removing base is the candidate in the effect table: negative percentage gain means worse error after removal.\n\n'
    text+='## EXPLORATORY 5. Signed errors and national actuals\n\nSigned error is forecast minus actual, systems/area/month, averaged across observed matched areas. Heatmaps show origin by horizon; the adjacent national plot uses target month, November 2022-September 2025, without counting repeated forecast targets multiple times. National totals include unmatched CER postcodes; matched-panel totals are also supplied. The panels have different aggregation units and do not identify causes or battery effects.\n\n![EXPLORATORY signed error and national actuals](../../data/explore/t03/test_exploratory/exploratory_signed_error.png)\n\n'
    text+='## EXPLORATORY 6. Individual seed robustness\n\nBoth matched individual-seed boosting and primary boosting-ensemble references are supplied. These answer different questions; seeds are not independent origin replications. No seed is selected. All MAE, MASE and RMSE cells at horizons 1,6,12,total are in the CSV.\n\n'+table(outputs['exploratory_seed_robustness'].loc[lambda d:d.metric.eq('mae')].drop(columns='scope'))+'\n\n'
    text+='## EXPLORATORY complete outputs and provenance\n\nGenerator: `evaluation.test_exploratory`; visual generator: `visuals.test_exploratory`. Log: `logs/t03_test_exploratory.log`. Every CSV has an explicit exploratory scope column. No frozen or confirmatory artifact is overwritten.\n\n'
    for name in outputs:text+=f'- [EXPLORATORY {name}](../../data/explore/t03/test_exploratory/{name}.csv)\n'
    text+='\n[EXPLORATORY output index](../../data/explore/t03/test_exploratory/index.md). Private copies: visuals/t03/test_exploratory/ and reports/figures/test_exploratory/.\n'
    Path('reports/experiments/test_exploratory.md').write_text(text,encoding='utf-8')
    for path,digest in locked['artifact_sha256'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
    provenance={'scope':SCOPE,'results_commit':subprocess.run(['git','log','-1','--format=%h'],capture_output=True,text=True,check=True).stdout.strip(),'inputs':inputs,'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['src/evaluation/test_exploratory.py','src/visuals/test_exploratory.py']},'confirmatory_artifacts_unchanged':len(locked['artifact_sha256']),'claim_cells':len(claim),'not_lower_cells':len(failures),'fits':0,'gpu':False,'target_matrix_access':False}
    (OUT/'exploratory_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps(provenance,indent=2))

if __name__=='__main__':main()
