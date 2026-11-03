"""Draft-v7 candidate evidence from saved validation forecasts, no test access."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.dm import dm_from_losses

OUT=Path('data/explore/t03/v7_chain_evidence')
DRAFT=Path('reports/protocol/protocol_v7_draft.md')
SEEDS=(11,29,47)
CANDIDATES=(
    ('A1','Accuracy','combination','own','mae','1','all',False),
    ('A2','Accuracy','combination','neighbours','mae','1','all',False),
    ('A3','Accuracy','combination','own','mae','1-3','all',False),
    ('A4','Accuracy','combination','neighbours','mae','1-3','all',False),
    ('A5','Accuracy','combination','own','mae','6','all',False),
    ('A6','Accuracy','combination','own','mae','total_12','all',True),
    ('A7','Accuracy','combination','own','mase','1','all',False),
    ('B1','Behavioural','real','without_base','mae','1','all',False),
    ('B2','Behavioural','real','without_base','mae','total_12','all',False),
    ('B3','Behavioural','real','without_base','mae','1-3','all',False),
    ('B4','Behavioural','real','without_base','mae','1','low',False),
)


def origin_losses(runs,ctx,metric,outcome,group):
    """Area/horizon mean first, then seed mean; exactly one loss per origin."""
    if metric not in ('mae','mase') or group not in ('all','low'):raise ValueError('Unknown loss/group')
    by_seed=[]
    for prediction in runs.values():
        prediction=np.asarray(prediction)
        if prediction.shape!=ctx.truth.shape or not np.isfinite(prediction).all() or (prediction<0).any():raise ValueError('Invalid saved forecasts')
        if outcome=='total_12':
            error=prediction.sum(axis=2).astype(float)-ctx.truth.sum(axis=2)
            factor=12
        else:
            selected=slice(0,3) if outcome=='1-3' else slice(int(outcome)-1,int(outcome))
            error=prediction[:,:,selected].astype(float)-ctx.truth[:,:,selected]
            factor=1
        losses=np.abs(error)
        if metric=='mase':losses=losses/(ctx.scales*factor if losses.ndim==2 else ctx.scales[:,:,None])
        by_seed.append(np.array([losses[t].mean() if group=='all' else losses[t,ctx.groups[t]==0].mean() for t in range(len(ctx.origins))]))
    return np.mean(by_seed,axis=0)


def candidate_test(a,b,h,noninferiority=False):
    """NI contrasts E(loss A - 1.01 loss B); lower-tail alternative."""
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    if a.shape!=b.shape or a.ndim!=1 or not np.isfinite([a,b]).all() or min(a.min(),b.min())<0:raise ValueError('Aligned finite nonnegative losses required')
    if b.mean()<=0:raise ValueError('Positive reference mean required for relative effect')
    boundary=1.01 if noninferiority else 1.
    result={'candidate_loss':float(a.mean()),'reference_loss':float(b.mean()),
        'gain_reference_minus_candidate':float((b-a).mean()),'gain_percent':float(100*(b.mean()-a.mean())/b.mean()),
        'relative_excess_percent':float(100*(a.mean()/b.mean()-1)),
        'null_reference_multiplier':boundary,'mean_test_differential':float((a-boundary*b).mean()),
        'noninferiority_margin_slack':float((1.01*b-a).mean()) if noninferiority else np.nan,
        'dm_statistic':np.nan,'p_two_sided':np.nan,'p_lower_loss':np.nan,'p_same_convention':np.nan,'status':'defined'}
    try:
        statistic,p=dm_from_losses(a,boundary*b,h)
        if not np.isfinite([statistic,p]).all() or not 0<=p<=1:raise ValueError('Invalid DM output')
        lower=p/2 if statistic<0 else 1-p/2
        result.update(dm_statistic=float(statistic),p_two_sided=float(p),p_lower_loss=float(lower),
            p_same_convention=float(lower if noninferiority else p))
    except (ArithmeticError,ValueError) as error:result['status']='undefined: '+str(error)
    return result


def read_combination(ctx):
    from evaluation.b2_ensemble_combination import ROOT
    runs={};hashes={}
    from models.b2_runtime import sha
    for seed in SEEDS:
        parts=[];dates=[]
        for path in sorted(ROOT.glob(f'learned_B2_ensemble_seed{seed}_part*.npz')):
            with np.load(path,allow_pickle=False) as data:
                np.testing.assert_array_equal(data['codes'],ctx.codes)
                parts.append(data['prediction'].copy());dates.extend(data['origins'])
            hashes[str(path)]=sha(path)
        np.testing.assert_array_equal(dates,ctx.origins)
        runs[seed]=np.concatenate(parts)
    return runs,hashes


def main():
    from threadpoolctl import threadpool_limits
    from evaluation.b2_gate_c import require_release
    from evaluation.gate_c_io import context_from_panel,load_baselines,read_prediction
    from evaluation.b2_ensemble_combination import ensemble
    from models.b2_runtime import CAMPAIGN,sha
    cfg,_,_,_=require_release()
    with threadpool_limits(limits=1):
        ctx=context_from_panel(cfg);baseline,_,baseline_provenance=load_baselines(cfg,ctx)
        combination,hashes=read_combination(ctx)
        runs={'combination':combination,'own':baseline['gradient_boosting_own'],'neighbours':baseline['gradient_boosting_neighbours']}
        for condition in ('real','without_base'):
            runs[condition]={}
            for seed in SEEDS:
                path=CAMPAIGN/condition/f'predictions_seed{seed}.npz'
                runs[condition][seed]=read_prediction(path,ctx);hashes[str(path)]=sha(path)
        point={m:{'ensemble':ensemble(values)} for m,values in runs.items()}
        records=[];series=[]
        for view,values in (('seed_averaged_losses',runs),('forecast_ensembles',point)):
            for cid,chain,candidate,reference,metric,outcome,group,ni in CANDIDATES:
                a=origin_losses(values[candidate],ctx,metric,outcome,group)
                b=origin_losses(values[reference],ctx,metric,outcome,group)
                h=12 if outcome=='total_12' else 3 if outcome=='1-3' else int(outcome)
                result=candidate_test(a,b,h,ni)
                records.append({'candidate_id':cid,'chain':chain,'aggregation':view,'candidate':candidate,'reference':reference,
                    'metric':metric,'outcome':outcome,'group':group,'test':'NI 1 percent' if ni else 'superiority',
                    'origins':len(ctx.origins),'DM_h':h,'HAC_max_lag':h-1,**result})
                series.extend({'candidate_id':cid,'aggregation':view,'origin':date,'candidate_loss':float(x),'reference_loss':float(y),
                    'tested_differential':float(x-(1.01 if ni else 1)*y)} for date,x,y in zip(ctx.origins,a,b))
    evidence=pd.DataFrame(records); assert len(evidence)==22 and evidence.origins.eq(36).all()
    OUT.mkdir(parents=True,exist_ok=True)
    evidence.to_csv(OUT/'validation_evidence.csv',index=False);pd.DataFrame(series).to_csv(OUT/'origin_losses.csv',index=False)
    policy={'scope':'validation only; chain order unset; no test-block access','candidate_count':11,'aggregation_views':2,
        'chains_alpha_each':.025,'superiority_p_convention':'existing two-sided DM; lower-tail p also displayed, not silently substituted',
        'NI_null':'E[L_combination - 1.01 L_own] >= 0; alternative < 0',
        'pooled_1_3':'within-origin mean of absolute errors across areas/horizons 1,2,3, then seeds; DM h=3, 36 origins',
        'NI_p_convention':'one-sided lower tail of margin-shifted HLN DM, df=n-1',
        'ordering':'A/B identifiers reproduce candidate listing, NOT a fixed testing sequence',
        'input_sha256':hashes,'baselines':baseline_provenance,'source_sha256':{p:sha(p) for p in ('src/evaluation/v7_chain_evidence.py','src/evaluation/dm.py')},
        'model_refits':0,'gpu_use':False,'test_forecasts_or_losses':0}
    write_draft(evidence,policy)
    from visuals.v7_chain_evidence import render
    render(evidence,OUT)
    Path('reports/experiments/t03_v7_chain_evidence_checks.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf-8')
    print(evidence[['candidate_id','aggregation','gain_reference_minus_candidate','gain_percent','dm_statistic','p_two_sided','p_lower_loss']].to_string(index=False))


def write_draft(evidence,policy):
    from evaluation.graph_diagnostics_report import table
    # Preserve any supplied sections outside section 4 on later regenerations.
    if DRAFT.exists():
        old=DRAFT.read_text(encoding='utf-8'); start=old.find('## 4. Confirmatory testing')
        if start<0:raise RuntimeError('Existing v7 draft has no section 4; merge explicitly before replacing')
        next_section=old.find('\n## ',start+4)
        prefix=old[:start];suffix=old[next_section:] if next_section>=0 else ''
    else:
        prefix='# Protocol v7 draft - confirmatory testing amendment\n\n3 November 2026. **DRAFT - DO NOT TAG.** No existing v7 draft was found in this workspace. This file records only the requested replacement section 4 and validation evidence; no other final-test provisions are invented. Final chain order remains for the researcher. Test block stays sealed.\n\n'
        suffix=''
    text='''## 4. Confirmatory testing

Replace the proposed five-test Holm family with **two separate fixed-sequence chains, each at alpha = 0.025**: Accuracy and Behavioural. Within each chain, test in the researcher's fixed order and stop that chain at its first non-rejection. A stopped chain cannot restart at a later candidate; no alpha is transferred between chains. Undefined tests cannot reject and stop their chain. Orders must be written before any final-test scoring and remain unchanged afterward. **Both orders are currently UNSET.** Candidate IDs below are labels in the supplied listing, not a chosen sequence; the validation tables do not execute or rank chains.

### Conventions and unresolved draft context

Use the existing origin-averaged Diebold Mariano adapter (dieboldmariano 1.1.0), Harvey-Leybourne-Newbold correction, Bartlett HAC through lag h-1 and Student t reference with n-1 degrees of freedom. All validation evidence uses 36 origins, not 108 seed-origin observations. For pooled horizons 1-3, average absolute errors over those three horizons within each origin/group and then over seeds; **h=3** (HAC lags 0-2). This is not absolute error of a three-month sum and not three independent tests. Horizon 1 uses h=1, horizon 6 h=6, and twelve-month total h=12. MASE retains the existing training-only seasonal scales and pooled fallback. Low maturity is the dynamic group at each origin; no area is dropped from other comparisons.

The historical convention scores each seed's forecast, averages area/horizon losses within origin, and then averages the three seed losses before DM. Its results are shown first. A separate forecast-ensemble view averages forecasts across seeds BEFORE scoring. These are different estimands: the absence of the referenced v7 draft means its final aggregation cannot be inferred. Both are explicitly shown rather than silently replacing one with the other. The researcher can identify the intended aggregation when supplying the final orders.

Combination means the already saved **expanding-window learned mixture of neighbour boosting and the B2 real ensemble**, with one shared weight per maturity/band pooled across three boosting-seed pairs. It is not the matched-individual-B2 mixture and does not use descriptive all-36-origin weights. In the forecast-ensemble view, average its three boosting-seed-paired combination forecasts; each boosting/B2 control is also averaged across its three seeds first. No weights are re-estimated for this task.

Superiority evidence retains the existing **two-sided** DM p-value. The directional lower-loss p-value is also displayed to make the alternative explicit; changing superiority tests to one-sided is not silently assumed by this amendment. Under the existing convention, a superiority rejection requires the two-sided p < 0.025 and the candidate's mean loss to be lower. Non-inferiority is necessarily directional, as specified next. No Holm adjustment is applied to these candidate evidence tables or within a fixed-sequence chain.

### One-percent non-inferiority candidate

Let Lc and Lo be the origin-level twelve-month total MAE losses of the combination and own-lag boosting. Test **H0: E[Lc - 1.01 Lo] >= 0**, versus **H1: E[Lc - 1.01 Lo] < 0**. Apply the same h=12 HLN/Bartlett DM calculation to Lc and 1.01 Lo; the p-value for this candidate is the **one-sided lower tail**. This uses a 1% relative mean-loss margin and includes reference-loss variation/covariance. The unshifted gain and percentage gain remain reported. Positive margin slack = 1.01 mean(Lo) - mean(Lc) favours non-inferiority. The displayed two-sided NI p-value concerns this shifted boundary, not equality with unscaled own boosting.

### Validation candidate evidence - descriptive only

Effects: gain = reference mean loss minus candidate mean loss; positive means lower candidate error. Percentage gain divides that gain by the reference mean loss. Monthly MAE units are systems/area/month; total MAE units systems/area/twelve-month window; MASE unitless. These validation p-values follow model/combination development and are not confirmatory evidence. No final-test observations are opened. All raw p-values are unadjusted. No chain order is recommended from these tables.

'''
    labels={'seed_averaged_losses':'Historical convention: seed-averaged origin losses','forecast_ensembles':'Separate view: seed-average forecasts scored once'}
    for view,title in labels.items():
        part=evidence.loc[evidence.aggregation.eq(view)].copy()
        part['comparison']=part.candidate+' vs '+part.reference
        text+='#### '+title+'\n\n'
        text+=table(part[['candidate_id','chain','comparison','metric','outcome','group','candidate_loss','reference_loss','gain_reference_minus_candidate','gain_percent']])+'\n\n'
        for col in ('p_two_sided','p_lower_loss','p_same_convention'):
            part[col]=part[col].map(lambda x:'undefined' if not np.isfinite(x) else f'{x:.8g}')
        text+=table(part[['candidate_id','test','DM_h','dm_statistic','p_two_sided','p_lower_loss','p_same_convention','noninferiority_margin_slack']])+'\n\n'
    text+='''The `p_same_convention` column is the existing two-sided p for superiority and the margin-shifted one-sided p for NI. Directional p-values are supplementary for superiority until explicitly chosen. The two aggregation views are alternative descriptive calculations, not additional registered hypotheses or extra alpha allocations.

Candidate listing: A1 combination/own MAE h1; A2 combination/neighbour MAE h1; A3 combination/own pooled MAE h1-3; A4 combination/neighbour pooled MAE h1-3; A5 combination/own MAE h6; A6 total-MAE 1% NI against own; A7 combination/own MASE h1. B1 real/without-base MAE h1; B2 same total; B3 same pooled MAE h1-3; B4 same h1, low maturity only.

Evidence CSV: [candidate effects and p-values](../../data/explore/t03/v7_chain_evidence/validation_evidence.csv), [origin losses and tested differentials](../../data/explore/t03/v7_chain_evidence/origin_losses.csv), [evidence figure and plotted CSV](../../data/explore/t03/v7_chain_evidence/index.md), [provenance](../experiments/t03_v7_chain_evidence_checks.json). Generator: `evaluation.v7_chain_evidence`; log `logs/t03_v7_chain_evidence.log`. No model fits, weight re-estimation, GPU use, test scoring, git mutation or tag. **Stop for researcher final orders; do not freeze or execute this draft.**
'''
    DRAFT.write_text(prefix+text+suffix,encoding='utf-8')


if __name__=='__main__':main()
