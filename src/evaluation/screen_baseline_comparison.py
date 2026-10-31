"""Descriptive anchor-matched bands; independent of architecture selection."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

BANDS={'1-3':(0,3),'4-6':(3,6),'7-12':(6,12),'1-12':(0,12)}


def read_anchors(path,ctx):
    with np.load(path,allow_pickle=False) as data:
        np.testing.assert_array_equal(data['codes'],ctx.codes)
        origins=data['origins'].astype(str)
        value=data['prediction']
        if len(set(origins))!=len(origins) or value.shape!=(len(origins),len(ctx.codes),12):
            raise ValueError('Invalid baseline axes')
        if not np.isfinite(value).all() or (value<0).any():raise ValueError('Invalid baseline forecasts')
        lookup={o:i for i,o in enumerate(origins)}
        if any(o not in lookup for o in ctx.origins):raise ValueError('Baseline missing a screen anchor')
        return value[[lookup[o] for o in ctx.origins]].copy()


def load_anchor_baselines(ctx):
    from models.screen_cpu import ROOT,OLD,CONDITIONS
    selected=json.loads((ROOT/'boosting_selection.json').read_text())
    original=json.loads((OLD/'run_manifest.json').read_text())
    current=json.loads((ROOT/'cpu_manifest.json').read_text())
    if original['panel_sha256']!=current['panel_sha256']:raise ValueError('Baseline panel provenance differs')
    result={}; hashes={}
    for condition in CONDITIONS:
        path=OLD/f'{condition}_seed11.npz'
        result[f'{condition}_frozen']=read_anchors(path,ctx)
        hashes[path.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
        decision=selected[condition]
        if bool(decision['improved'])!=(decision['winner']['tuning_mae']<decision['old_tuning_mae']):
            raise ValueError('Inconsistent extra-search selection')
        if decision['improved']:
            marker=ROOT/f'{condition}_updated_complete.json'
            if not marker.exists():raise ValueError('Improved baseline full validation incomplete')
            complete=json.loads(marker.read_text())
            if complete['parameters']!=decision['winner']['parameters'] or complete['test_forecasts_or_losses']:
                raise ValueError('Updated baseline authority mismatch')
            path=ROOT/f'{condition}_updated_seed11.npz'
            result[f'{condition}_improved']=read_anchors(path,ctx)
            hashes[path.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result,{'seed':11,'anchors':list(map(str,ctx.origins)),'prediction_sha256':hashes}


def band_scores(predictions,ctx):
    """Pool monthly cells within a band; root pooled MSE, never mean RMSE."""
    ctx.validate()
    records=[]
    for model,prediction in predictions.items():
        prediction=np.asarray(prediction,dtype=float)
        if prediction.shape!=ctx.truth.shape or not np.isfinite(prediction).all() or (prediction<0).any():
            raise ValueError('Invalid band prediction array')
        errors=prediction-ctx.truth
        for band,(start,stop) in BANDS.items():
            for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                per_origin=[]
                for t,origin in enumerate(ctx.origins):
                    use=np.ones(len(ctx.codes),bool) if group is None else ctx.groups[t]==group
                    e=errors[t,use,start:stop]
                    values={'mae':float(np.abs(e).mean()),'mase':float((np.abs(e)/ctx.scales[t,use,None]).mean()),
                            'mse':float(np.square(e).mean())}
                    per_origin.append(values)
                    records.append({'model':model,'anchor':str(origin),'band':band,'group':label,
                                    **values,'rmse':float(np.sqrt(values['mse']))})
                pooled={k:float(np.mean([r[k] for r in per_origin])) for k in ('mae','mase','mse')}
                records.append({'model':model,'anchor':'both_anchors','band':band,'group':label,
                                **pooled,'rmse':float(np.sqrt(pooled['mse']))})
    return pd.DataFrame(records)


def gains(scores,baseline_names):
    """Positive absolute/percentage gain means the candidate has lower error."""
    keys=['anchor','band','group']
    records=[]
    for candidate in 'ABC':
        for condition in ('real','no_graph'):
            name=f'{candidate}_{condition}'
            own=scores.loc[scores.model.eq(name)]
            if own.empty:raise ValueError('Missing screen candidate')
            references=list(baseline_names)+(['C_base'] if candidate=='C' else [])
            for reference in references:
                base=scores.loc[scores.model.eq(reference)]
                joined=own.merge(base,on=keys,suffixes=('_candidate','_baseline'),validate='one_to_one')
                if len(joined)!=len(own):raise ValueError('Misaligned reference bands')
                for row in joined.to_dict('records'):
                    record={k:row[k] for k in keys}|{'candidate':candidate,'condition':condition,'reference':reference}
                    for metric in ('mae','mase','rmse'):
                        x=row[metric+'_candidate']; b=row[metric+'_baseline']
                        record.update({metric+'_candidate':x,metric+'_baseline':b,metric+'_gain':b-x,
                                       metric+'_gain_percent':100*(b-x)/b if b>0 else np.nan})
                    records.append(record)
    return pd.DataFrame(records)


def write_comparisons(combined,ctx,out):
    from evaluation.graph_diagnostics_report import table
    baseline,provenance=load_anchor_baselines(ctx)
    values={name:seeds[11] for name,seeds in combined.items()}|baseline
    scores=band_scores(values,ctx); comparison=gains(scores,list(baseline))
    out=Path(out)
    scores.to_csv(out/'anchor_band_scores.csv',index=False)
    comparison.to_csv(out/'anchor_band_comparisons.csv',index=False)
    (out/'anchor_baseline_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    pooled=scores.loc[scores.anchor.eq('both_anchors')&scores.band.ne('1-12')]
    improvement=comparison.loc[comparison.anchor.eq('both_anchors')&comparison.band.ne('1-12')]
    text='''## Descriptive comparisons with anchor-matched boosting

All models use **seed 11 at August 2019 and August 2020**, including each frozen boosting selection and any extra-search improved selection. The unchanged architecture-selection rule uses candidate real-graph monthly MAE only; these comparisons do not enter selection. C_base is C's strictly prior-quarter boosting forecast, which differs from the frozen own-lag baseline fitted at the anchor itself.

Bands 1–3, 4–6 and 7–12 pool individual monthly forecast errors, **not** sums of forecasts over each band. MAE/MASE average monthly cells within each area group and give equal weight to the two anchors; RMSE is the square root of pooled squared errors. MASE uses the same training-only anchor scales for every model. These are descriptive, single-seed comparisons; no significance tests or behavioural claims. Positive gain means the candidate lowers the reference error. A zero reference error has undefined percentage gain, retained as NaN.

[Every anchor, band and maturity group's scores](../../data/explore/t03/architecture_screen/anchor_band_scores.csv); [paired candidate/baseline errors and absolute/percentage gains](../../data/explore/t03/architecture_screen/anchor_band_comparisons.csv); [saved-baseline hashes](../../data/explore/t03/architecture_screen/anchor_baseline_provenance.json).

### Overall, pooled across both anchors

'''+table(pooled.loc[pooled.group.eq('all'),['model','band','mae','mase','rmse']])
    text+='\n\n### Gains against each boosting reference (C also against its own base)\n\n'
    text+=table(improvement.loc[improvement.group.eq('all'),['candidate','condition','reference','band','mae_gain','mase_gain','rmse_gain']])
    text+='\n\n### Maturity terciles, pooled across both anchors\n\n'
    text+=table(pooled.loc[pooled.group.ne('all'),['model','band','group','mae','mase','rmse']])
    text+='\n\nPer-anchor maturity comparisons and C gains are retained in the complete linked CSVs. No improved-baseline column is manufactured if neither extra selection wins.\n\n'
    return text
