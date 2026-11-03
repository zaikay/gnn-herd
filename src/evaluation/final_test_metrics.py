"""Pure v7 ensemble, fixed-weight, fixed-sequence and descriptive statistics."""
import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from evaluation.gate_c_metrics import evaluate
from evaluation.v7_chain_evidence import CANDIDATES,origin_losses,candidate_test

BANDS=((0,3,'1-3'),(3,6,'4-6'),(6,12,'7-12'))
ALIASES={'own':'gradient_boosting_own','neighbours':'gradient_boosting_neighbours','real':'B2_real','without_base':'B2_without_base','combination':'combination'}


def forecast_ensembles(predictions,seeds):
    result={}
    for name,runs in predictions.items():
        if set(runs)!=set(seeds):raise ValueError('Incomplete fixed seed set')
        arrays=[np.asarray(runs[s],dtype=float) for s in seeds]
        if any(a.shape!=arrays[0].shape or not np.isfinite(a).all() or (a<0).any() for a in arrays):raise ValueError('Invalid forecast arrays')
        result[name]=np.mean(arrays,axis=0,dtype=np.float64)
    return result


def fixed_combination(neighbour,graph,groups,weights):
    if neighbour.shape!=graph.shape or groups.shape!=graph.shape[:2]:raise ValueError('Misaligned fixed combination')
    result=np.empty_like(graph,dtype=float)
    for t in range(len(graph)):
        for group,label in enumerate(('low','medium','high')):
            selected=groups[t]==group
            for start,stop,band in BANDS:
                w=weights[label][band]
                result[t,selected,start:stop]=w*neighbour[t,selected,start:stop]+(1-w)*graph[t,selected,start:stop]
    return result


def chains(point,ctx,spec,test=candidate_test):
    definitions={row[0]:row for row in CANDIDATES}
    rows=[]
    for chain,order in spec['chains'].items():
        stopped=False
        for position,cid in enumerate(order,1):
            if cid=='B4':raise ValueError('B4 was dropped before final test')
            _,_,candidate,reference,metric,outcome,group,ni=definitions[cid]
            row={'chain':chain,'position':position,'candidate_id':cid,'candidate':ALIASES[candidate],
                'reference':ALIASES[reference],'metric':metric,'outcome':outcome,'group':group,'alpha':spec['alpha_each'],
                'p_one_sided':np.nan,'status':'not_tested_after_stop','dm_statistic':np.nan}
            if stopped:
                rows.append(row);continue
            a=origin_losses({'ensemble':point[ALIASES[candidate]]},ctx,metric,outcome,group)
            b=origin_losses({'ensemble':point[ALIASES[reference]]},ctx,metric,outcome,group)
            h=12 if outcome=='total_12' else 3 if outcome=='1-3' else int(outcome)
            try:result=test(a,b,h,ni)
            except (ValueError,ArithmeticError) as error:
                row.update(status='undefined_stop',reason=str(error));rows.append(row);stopped=True;continue
            row.update({k:result[k] for k in ('candidate_loss','reference_loss','gain_reference_minus_candidate','gain_percent','dm_statistic','mean_test_differential','noninferiority_margin_slack')})
            p=result['p_lower_loss'];row['p_one_sided']=p
            favourable=result['mean_test_differential']<0
            reject=bool(result['status']=='defined' and np.isfinite(p) and p<spec['alpha_each'] and favourable)
            row['status']='rejected' if reject else 'undefined_stop' if result['status']!='defined' else 'not_rejected_stop'
            row['test']='NI 1 percent' if ni else 'directional superiority'
            stopped=not reject;rows.append(row)
    return pd.DataFrame(rows)


def hac_interval(differences,h,confidence=.95):
    d=np.asarray(differences,dtype=float);n=len(d)
    if not np.isfinite(d).all() or not 0<h<n:raise ValueError('Invalid HAC interval input')
    centred=d-d.mean()
    long_run=centred@centred/n
    for lag in range(1,h):long_run+=2*(1-lag/h)*(centred[lag:]@centred[:-lag])/n
    factor=np.sqrt((n+1-2*h+h*(h-1)/n)/n)
    if long_run<=0 or factor<=0:return float(d.mean()),np.nan,np.nan
    half=student_t.ppf((1+confidence)/2,n-1)*np.sqrt(long_run/n)/factor
    return float(d.mean()),float(d.mean()-half),float(d.mean()+half)


def intervals(point,ctx,spec):
    rows=[]
    for other in ('B2_no_graph','B2_shuffled'):
        for outcome in (*map(str,range(1,13)),'total_12'):
            a=origin_losses({'ensemble':point['B2_real']},ctx,'mae',outcome,'all')
            b=origin_losses({'ensemble':point[other]},ctx,'mae',outcome,'all')
            h=12 if outcome=='total_12' else int(outcome)
            mean,lo,hi=hac_interval(a-b,h,spec['interval_confidence'])
            rows.append({'candidate':'B2_real','reference':other,'outcome':outcome,'origins':len(a),'DM_h':h,
                'mean_MAE_difference':mean,'lower95':lo,'upper95':hi,'interpretation':'negative favours real; pointwise descriptive'})
    return pd.DataFrame(rows)


def target_periods(point,ctx,first,last):
    records=[];coverage=[]
    for i,origin in enumerate(ctx.origins):
        for h in range(1,13):
            target=str(pd.Period(origin,freq='M')+h)
            marked='post_eligibility_JulSep2025' if first=='2025-07' and last=='2025-09' else 'synthetic_marked_months'
            period=marked if first<=target<=last else 'other_test_targets'
            coverage.append({'origin':origin,'horizon':h,'target_month':target,'period':period})
            for name,prediction in point.items():
                for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                    use=np.ones(len(ctx.codes),bool) if group is None else ctx.groups[i]==group
                    error=prediction[i,use,h-1]-ctx.truth[i,use,h-1]
                    records.append({'model':name,'period':period,'origin':origin,'horizon':h,'target_month':target,'group':label,
                        'areas':int(use.sum()),'mae':float(np.abs(error).mean()),'mase':float((np.abs(error)/ctx.scales[i,use]).mean()),
                        'mse':float(np.square(error).mean()),'mean_signed_error':float(error.mean())})
    cells=pd.DataFrame(records);summaries=[]
    for key,part in cells.groupby(['model','period','group']):
        summaries.append(dict(zip(('model','period','group'),key),mae=part.mae.mean(),mase=part.mase.mean(),
            rmse=float(np.sqrt(part.mse.mean())),mean_signed_error=part.mean_signed_error.mean(),
            origin_horizon_cells=len(part),unique_target_months=part.target_month.nunique(),unique_origins=part.origin.nunique()))
    return pd.DataFrame(summaries),pd.DataFrame(coverage),cells


def analyse(predictions,ctx,spec):
    ctx.validate();point=forecast_ensembles(predictions,spec['seeds'])
    point['combination']=fixed_combination(point['gradient_boosting_neighbours'],point['B2_real'],ctx.groups,spec['weights'])
    point['combination_no_graph_sensitivity']=fixed_combination(point['gradient_boosting_neighbours'],point['B2_no_graph'],ctx.groups,spec['weights'])
    individual=evaluate(predictions,ctx,seeds=spec['seeds'])
    primary=evaluate({m:{'ensemble':p} for m,p in point.items()},ctx,seeds=('ensemble',))
    period,coverage,period_cells=target_periods(point,ctx,spec['battery_target_first'],spec['battery_target_last'])
    return {'individual':individual,'ensemble':primary,'chains':chains(point,ctx,spec),
        'intervals':intervals(point,ctx,spec),'target_periods':period,'target_coverage':coverage,'target_period_cells':period_cells},point
