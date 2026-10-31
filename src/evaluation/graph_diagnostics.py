"""CPU-only graph diagnostics from saved validation forecasts/curves/checkpoints."""
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from evaluation.gate_c_io import frozen_context,load_gnn_predictions,campaign_path,CONDITIONS
from evaluation.gate_c_metrics import OUTCOMES
from features.panel import load_panel

OUT=Path('data/explore/t03/graph_diagnostics')
DEGREE_EDGES=[-1,0,1,2,4,8,16,np.inf]
DEGREE_LABELS=['0','1','2','3-4','5-8','9-16','17+']


def column_correlations(x,y):
    """Within-area Pearson correlations across origins; never pool areas."""
    valid=np.isfinite(x)&np.isfinite(y)
    n=valid.sum(axis=0)
    xm=np.divide(np.where(valid,x,0).sum(axis=0),n,out=np.zeros(x.shape[1]),where=n>0)
    ym=np.divide(np.where(valid,y,0).sum(axis=0),n,out=np.zeros(y.shape[1]),where=n>0)
    xc=np.where(valid,x-xm,0); yc=np.where(valid,y-ym,0)
    xx=np.square(xc).sum(axis=0); yy=np.square(yc).sum(axis=0)
    denominator=np.sqrt(xx*yy)
    r=np.divide((xc*yc).sum(axis=0),denominator,out=np.full(x.shape[1],np.nan),where=(n>=3)&(denominator>0))
    reason=np.full(x.shape[1],'defined',dtype=object)
    reason[n<3]='no_neighbours_or_insufficient_pairs'
    reason[(n>=3)&(xx==0)]='constant_gap'
    reason[(n>=3)&(xx>0)&(yy==0)]='constant_signed_error'
    return r,n,reason


def neighbour_gap(level,edges):
    """Arithmetic neighbour mean minus own level; empty neighbour set is unknown."""
    edges=np.asarray(edges,dtype=int).reshape(-1,2)
    source=np.r_[edges[:,0],edges[:,1]]; target=np.r_[edges[:,1],edges[:,0]]
    degree=np.bincount(source,minlength=level.shape[1])
    total=np.zeros((level.shape[1],level.shape[0]))
    np.add.at(total,source,level[:,target].T)
    mean=np.divide(total,degree[:,None],out=np.full_like(total,np.nan),where=degree[:,None]>0).T
    return mean-level


def toy_and_checkpoint_checks(panel,root,selections,isolate_full_indices):
    import torch
    from models.core_gnn import graph_operator,CoreGNN
    torch.set_num_threads(1)
    edges=np.array([[1,2]]+[[3,i] for i in range(4,9)],dtype=int)
    observed=np.ones(9,dtype=bool); degrees=np.bincount(edges.ravel(),minlength=9)
    labels=['isolate','pair_a','pair_b','hub_5']+[f'leaf_{i}' for i in range(1,6)]
    operators={condition:graph_operator(edges,observed,condition) for condition in ('real','within_state_shuffled','no_graph')}
    entries=[]; summaries=[]
    for condition,operator in operators.items():
        matrix=operator.to_dense().numpy()
        for i in range(9):
            neighbours=np.flatnonzero((matrix[i]>0)&(np.arange(9)!=i))
            summaries.append({'condition':condition,'node':labels[i],'degree':int(degrees[i]),
                'self_weight':float(matrix[i,i]),'neighbour_weights':json.dumps(matrix[i,neighbours].tolist()),
                'neighbour_weight_sum':float(matrix[i,neighbours].sum()),'row_sum':float(matrix[i].sum())})
            for j in range(9):
                entries.append({'condition':condition,'receiver':labels[i],'sender':labels[j],
                                'receiver_degree':int(degrees[i]),'sender_degree':int(degrees[j]),'weight':float(matrix[i,j])})
    pd.DataFrame(entries).to_csv(OUT/'operator_toy_weights.csv',index=False)
    pd.DataFrame(summaries).to_csv(OUT/'operator_summary.csv',index=False)
    torch.manual_seed(11)
    reference=CoreGNN(operators['no_graph'],observed,32)
    inputs=torch.randn(2,24,9,6)
    values={}
    for condition,operator in operators.items():
        model=CoreGNN(operator,observed,32)
        with torch.no_grad():
            for name,parameter in model.named_parameters():parameter.copy_(dict(reference.named_parameters())[name])
            values[condition]=model(inputs)[:,0,:]
    for condition in ('real','within_state_shuffled'):
        torch.testing.assert_close(values[condition],values['no_graph'],rtol=0,atol=0)
    checks=[]
    for alias,condition in CONDITIONS.items():
        config=selections[condition]['configuration_id']
        path=root/condition/f'c{config}_seed11_2020-08/checkpoint.pt'
        saved=torch.load(path,map_location='cpu',weights_only=False)
        actual=saved['model']['operator'].coalesce()
        assert actual.device.type=='cpu' and saved['completed_epochs']==65
        graph=panel.edges
        if condition=='within_state_shuffled':
            with np.load('data/processed/t03_graphs/shuffled_seed11.npz',allow_pickle=False) as data:graph=data['edges']
        expected=graph_operator(graph,panel.observed,'real' if condition=='real_without_installed_base' else condition).coalesce()
        torch.testing.assert_close(actual.indices(),expected.indices(),rtol=0,atol=0)
        torch.testing.assert_close(actual.values(),expected.values(),rtol=0,atol=0)
        indices=actual.indices().numpy(); weights=actual.values().numpy()
        diagonal=np.zeros(len(panel.codes)); use=indices[0]==indices[1]; diagonal[indices[0,use]]=weights[use]
        assert (diagonal>0).all()
        for i in isolate_full_indices:
            row=indices[0]==i
            assert row.sum()==1 and indices[1,row][0]==i and weights[row][0]==1
        checks.append({'condition':condition,'checkpoint':path.as_posix(),'map_location':'cpu',
            'completed_epochs':saved['completed_epochs'],'operator_matches_actual_code':True,
            'identity_diagonal_present':True,'observed_isolate_rows_identity':len(isolate_full_indices),
            'minimum_observed_self_weight':float(diagonal[panel.observed].min()),
            'maximum_observed_self_weight':float(diagonal[panel.observed].max())})
    pd.DataFrame(checks).to_csv(OUT/'checkpoint_operator_checks.csv',index=False)
    return {'same_weights_isolated_toy_max_difference':0.,'checkpoint_checks':checks}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with threadpool_limits(limits=1):
        cfg,signature,ctx=frozen_context()
        predictions,provenance=load_gnn_predictions(cfg,ctx,signature)
        root=campaign_path(signature)
        panel=load_panel(through=ctx.origins[-1])
        degree_full=np.bincount(panel.edges.ravel(),minlength=len(panel.codes))
        degrees=degree_full[panel.observed]
        effective=np.bincount(ctx.edges.ravel(),minlength=len(ctx.codes))
        isolates=degrees==0
        assert int(isolates.sum())==15
        selections={name:json.loads((root/name/'selection.json').read_text()) for name in CONDITIONS.values()}
        checks=toy_and_checkpoint_checks(panel,root,selections,np.flatnonzero(panel.observed & (degree_full==0)))
        own=np.stack([panel.targets[panel.observed,panel.index(o)] for o in ctx.origins]).astype(np.float64)
        trailing=np.stack([panel.targets[panel.observed,panel.index(o)-11:panel.index(o)+1].mean(axis=1,dtype=np.float64) for o in ctx.origins])
        gaps={'origin':neighbour_gap(own,ctx.edges),'trailing12':neighbour_gap(trailing,ctx.edges),
              'log_input':neighbour_gap(np.log1p(own),ctx.edges)}
        mae={}; signed={}; seed_groups=[]
        for model,seed_predictions in predictions.items():
            mean_signed=np.zeros((len(ctx.origins),len(ctx.codes),13)); mean_absolute=np.zeros((len(ctx.codes),13))
            for seed,prediction in seed_predictions.items():
                monthly=prediction.astype(np.float64)-ctx.truth
                total=prediction.sum(axis=2).astype(np.float64)-ctx.truth.sum(axis=2)
                errors=np.concatenate((monthly,total[:,:,None]),axis=2)
                mean_signed+=errors/3; mean_absolute+=np.abs(errors).mean(axis=0)/3
                for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                    means=np.mean([errors[t,np.ones(len(ctx.codes),bool) if group is None else ctx.groups[t]==group].mean(axis=0) for t in range(len(ctx.origins))],axis=0)
                    for h,outcome in enumerate(OUTCOMES):
                        seed_groups.append({'model':model,'seed':seed,'outcome':outcome,'group':label,'mean_signed_error':float(means[h])})
            mae[model]=mean_absolute; signed[model]=mean_signed
        ratio=np.divide(mae['gnn_real'],mae['gnn_no_graph'],out=np.full_like(mae['gnn_real'],np.nan),where=mae['gnn_no_graph']>0)
        ratio[(mae['gnn_no_graph']==0)&(mae['gnn_real']>0)]=np.inf
        area=[]
        for i,code in enumerate(ctx.codes):
            for h,outcome in enumerate(OUTCOMES):
                area.append({'postcode':code,'outcome':outcome,'degree':int(degrees[i]),'effective_degree':int(effective[i]),
                    'observed_isolate':bool(isolates[i]),'real_mae':float(mae['gnn_real'][i,h]),
                    'no_graph_mae':float(mae['gnn_no_graph'][i,h]),'mae_ratio':float(ratio[i,h]),
                    'ratio_defined':bool(np.isfinite(ratio[i,h]))})
        area=pd.DataFrame(area)
        area.to_csv(OUT/'degree_area_ratios.csv.gz',index=False)
        area.loc[area.observed_isolate].to_csv(OUT/'isolated_area_mae.csv',index=False)
        isolate_summary=area.loc[area.observed_isolate].groupby('outcome',as_index=False).agg(
            areas=('postcode','size'),real_mae=('real_mae','mean'),no_graph_mae=('no_graph_mae','mean'),median_area_ratio=('mae_ratio','median'))
        isolate_summary['ratio_of_mean_mae']=isolate_summary.real_mae/isolate_summary.no_graph_mae
        isolate_summary.to_csv(OUT/'isolates_mae.csv',index=False)
        area['degree_bin']=pd.cut(area.degree,DEGREE_EDGES,labels=DEGREE_LABELS)
        binned=[]
        for (outcome,bin_name),part in area.groupby(['outcome','degree_bin'],observed=True):
            finite=part.loc[np.isfinite(part.mae_ratio),'mae_ratio']
            binned.append({'outcome':outcome,'degree_bin':str(bin_name),'areas':len(part),
                'median_ratio':finite.median(),'q25_ratio':finite.quantile(.25),'q75_ratio':finite.quantile(.75),
                'ratio_of_mean_mae':part.real_mae.mean()/part.no_graph_mae.mean(),
                'undefined_or_infinite_ratios':len(part)-len(finite)})
        pd.DataFrame(binned).to_csv(OUT/'degree_binned.csv',index=False)
        pull_summaries=[]
        for mode,gap in gaps.items():
            records=[]
            for model,errors in (('gnn_real',signed['gnn_real']),('gnn_no_graph',signed['gnn_no_graph']),
                                  ('real_minus_no_graph',signed['gnn_real']-signed['gnn_no_graph'])):
                for h,outcome in enumerate(OUTCOMES):
                    r,n,reason=column_correlations(gap,errors[:,:,h])
                    for i,code in enumerate(ctx.codes):
                        records.append({'postcode':code,'outcome':outcome,'model':model,'degree':int(degrees[i]),
                            'correlation':float(r[i]),'paired_origins':int(n[i]),'status':reason[i]})
                    valid=r[np.isfinite(r)]
                    pull_summaries.append({'level_definition':mode,'model':model,'outcome':outcome,
                        'defined_areas':len(valid),'undefined_areas':len(r)-len(valid),
                        'median_correlation':float(np.median(valid)) if len(valid) else np.nan,
                        'mean_correlation':float(np.mean(valid)) if len(valid) else np.nan,
                        'share_positive':float(np.mean(valid>0)) if len(valid) else np.nan})
            pd.DataFrame(records).to_csv(OUT/f'pull_correlations_{mode}.csv.gz',index=False)
        pd.DataFrame(pull_summaries).to_csv(OUT/'pull_summary.csv',index=False)
        seed_groups=pd.DataFrame(seed_groups); seed_groups.to_csv(OUT/'signed_error_by_seed.csv',index=False)
        signed_groups=seed_groups.groupby(['model','outcome','group'],as_index=False).agg(mean_signed_error=('mean_signed_error','mean'),seed_sd=('mean_signed_error','std'))
        signed_groups.to_csv(OUT/'signed_error_maturity.csv',index=False)
        curve_rows=[]; selected_curves=[]
        for condition,selection in selections.items():
            i=selection['configuration_id']
            for fit_origin in dict.fromkeys(ctx.fit_origins):
                for seed in (11,29,47):
                    folder=root/condition/f'c{i}_seed{seed}_{fit_origin}'
                    curve=pd.read_csv(folder/'training_curve.csv'); assert int(curve.epoch.iloc[-1])==65
                    complete=json.loads((folder/'complete.json').read_text())
                    curve_rows.append({'condition':condition,'fit_origin':fit_origin,'seed':seed,**selection['configuration'],
                        'final_training_loss':float(curve.training_poisson_loss.iloc[-1]),
                        'last5_mean_training_loss':float(curve.training_poisson_loss.tail(5).mean()),
                        'last10_loss_decrease':float(curve.training_poisson_loss.iloc[-11]-curve.training_poisson_loss.iloc[-1]),
                        'fit_seconds':complete['wall_seconds'],'mean_epoch_seconds':complete['mean_epoch_seconds']})
                    if seed==11 and fit_origin in cfg['splits']['tuning_origins']:
                        curve=curve.copy(); curve['condition']=condition; curve['fit_origin']=fit_origin
                        selected_curves.append(curve)
        pd.DataFrame(curve_rows).to_csv(OUT/'selected_training_fit.csv',index=False)
        pd.concat(selected_curves,ignore_index=True).to_csv(OUT/'selected_training_curves.csv',index=False)
        # Four matched width-64/rate-.003 fits provide measured screening timing.
        reference=[]
        for condition in ('real','no_graph'):
            for anchor in cfg['splits']['tuning_origins']:
                record=json.loads((root/condition/f'c3_seed11_{anchor}/complete.json').read_text())
                assert record['hidden_size']==64 and record['epochs']==65
                reference.append({'condition':condition,'anchor':anchor,'seconds':record['wall_seconds']})
        pd.DataFrame(reference).to_csv(OUT/'screening_time_reference.csv',index=False)
        baseline=pd.read_csv('data/processed/t02_baselines/be4f68799849cb4c/fit_records.csv')
        estimates=[]
        for condition in ('gradient_boosting_own','gradient_boosting_neighbours'):
            for anchor in cfg['splits']['tuning_origins']:
                for leaves in (31,63):
                    part=baseline.loc[baseline.condition.eq(condition)&baseline.fit_origin.eq(anchor)&baseline.seed.eq(11)]
                    part=part.loc[part.parameters.map(lambda value:ast.literal_eval(value)['max_leaf_nodes']==leaves)]
                    estimates.append({'condition':condition,'anchor':anchor,'proposed_learning_rate':.05,
                        'max_leaf_nodes':leaves,'reference_mean_seconds':part.seconds.mean(),'reference_matches':len(part)})
        pd.DataFrame(estimates).to_csv(OUT/'boosting_extra_budget.csv',index=False)
        degree_association=[]
        for outcome,part in area.groupby('outcome'):
            use=part.degree.gt(0)&np.isfinite(part.mae_ratio)
            degree_association.append({'outcome':outcome,'spearman_degree_mae_ratio':part.loc[use,'degree'].corr(part.loc[use,'mae_ratio'],method='spearman'),'areas':int(use.sum())})
        pd.DataFrame(degree_association).to_csv(OUT/'degree_association.csv',index=False)
        summary={'observed_areas':len(ctx.codes),'original_observed_isolates':int(isolates.sum()),
            'effective_observed_isolates':int((effective==0).sum()),'undefined_ratios':int((~area.ratio_defined).sum()),
            'screening_reference_four_fit_hours':sum(r['seconds'] for r in reference)/3600,
            'boosting_reference_eight_fit_hours':sum(r['reference_mean_seconds'] for r in estimates)/3600,
            'operator_checks':checks,'new_fits':0,'gpu_use':False,'test_forecasts_or_losses':0}
        (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        for path in OUT.glob('*'):
            if path.is_file() and path.stat().st_size>=5_000_000:raise ValueError(f'Output exceeds 5 MB: {path}')
        print(json.dumps({k:v for k,v in summary.items() if k!='operator_checks'},indent=2))


if __name__=='__main__':
    main()
