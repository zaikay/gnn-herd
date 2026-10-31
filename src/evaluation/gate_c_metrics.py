"""Gate C metrics on supplied arrays only: no model loading or training."""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from evaluation.baselines import holm
from evaluation.dm import dm_from_losses

REPORTED = ('1','6','12','total_12')
OUTCOMES = tuple(map(str,range(1,13)))+('total_12',)
BASELINES = ('seasonal_naive','gradient_boosting_own','gradient_boosting_neighbours')
GNN_MODELS = ('gnn_real','gnn_shuffled','gnn_no_graph','gnn_no_base')


@dataclass
class Context:
    origins: np.ndarray
    codes: np.ndarray
    truth: np.ndarray
    scales: np.ndarray
    groups: np.ndarray
    edges: np.ndarray
    fit_origins: np.ndarray

    def validate(self):
        o,n = len(self.origins),len(self.codes)
        if self.truth.shape!=(o,n,12) or self.scales.shape!=(o,n) or self.groups.shape!=(o,n):
            raise ValueError('Misaligned truth/scales/maturity groups')
        if len(self.fit_origins)!=o or len(set(self.origins))!=o or len(set(self.codes))!=n:
            raise ValueError('Duplicate or misaligned origin/area identifiers')
        if any(not isinstance(c,(str,np.str_)) or len(c)!=4 or not c.isdigit() for c in self.codes):
            raise ValueError('Four-character postcode strings required')
        if not pd.PeriodIndex(self.origins,freq='M').is_monotonic_increasing:
            raise ValueError('Origins must be chronological')
        if (pd.PeriodIndex(self.fit_origins,freq='M')>pd.PeriodIndex(self.origins,freq='M')).any():
            raise ValueError('Fit origin cannot follow forecast origin')
        if not np.isfinite(self.truth).all() or (self.truth<0).any():
            raise ValueError('Evaluation includes unknown/invalid truth')
        if not np.isfinite(self.scales).all() or (self.scales<=0).any():
            raise ValueError('Positive training-only MASE scales required')
        if not np.isin(self.groups,[0,1,2]).all():
            raise ValueError('Invalid maturity terciles')
        for group in range(3):
            if not (self.groups==group).any(axis=1).all():
                raise ValueError('Every origin needs nonempty maturity terciles')
        edges = np.asarray(self.edges).reshape(-1,2)
        if len(edges) and (edges.min()<0 or edges.max()>=n or (edges[:,0]==edges[:,1]).any()):
            raise ValueError('Invalid observed-area graph')
        if len({tuple(sorted((int(a),int(b)))) for a,b in edges})!=len(edges):
            raise ValueError('Duplicate observed-area graph edges')


def evaluate(predictions,ctx,seeds=(11,29,47)):
    """Equal-area then equal-origin/seed losses; RMSE roots pooled MSE."""
    ctx.validate()
    origin_records,area_records = [],[]
    for model,seed_predictions in predictions.items():
        if set(seed_predictions)!=set(seeds):
            raise ValueError(f'Incomplete fixed seed set: {model}')
        area_errors=[]; area_signed=[]; area_scaled=[]
        for seed in seeds:
            prediction = np.asarray(seed_predictions[seed])
            if prediction.shape!=ctx.truth.shape or not np.isfinite(prediction).all() or (prediction<0).any():
                raise ValueError(f'Misaligned/nonfinite/negative forecasts: {model}')
            monthly = prediction.astype(np.float64)-ctx.truth.astype(np.float64)
            # Preserve the saved float32 twelve-month-sum convention used for
            # the audited baseline totals; accumulate losses in float64.
            total = prediction.sum(axis=2).astype(np.float64)-ctx.truth.sum(axis=2,dtype=np.float64)
            errors = np.concatenate((monthly,total[:,:,None]),axis=2)
            for t,origin in enumerate(ctx.origins):
                for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                    use = np.ones(len(ctx.codes),bool) if group is None else ctx.groups[t]==group
                    for k,outcome in enumerate(OUTCOMES):
                        e = errors[t,use,k]
                        scale = ctx.scales[t,use]*(12 if outcome=='total_12' else 1)
                        origin_records.append({'model':model,'seed':seed,'origin':origin,
                            'fit_origin':ctx.fit_origins[t],'outcome':outcome,'group':label,'areas':int(use.sum()),
                            'mae':float(np.abs(e).mean()),'mase':float((np.abs(e)/scale).mean()),
                            'mse':float(np.square(e).mean()),'mean_signed_error':float(e.mean())})
            indices = [OUTCOMES.index(h) for h in REPORTED]
            chosen = errors[:,:,indices]
            area_errors.append(np.abs(chosen).mean(axis=0))
            area_signed.append(chosen.mean(axis=0))
            area_scaled.append((np.abs(chosen)/ctx.scales[:,:,None]/np.array([1,1,1,12])[None,None,:]).mean(axis=0))
        absolute = np.mean(area_errors,axis=0); signed=np.mean(area_signed,axis=0); scaled=np.mean(area_scaled,axis=0)
        for i,code in enumerate(ctx.codes):
            for k,outcome in enumerate(REPORTED):
                area_records.append({'model':model,'postcode':code,'outcome':outcome,
                    'mae':float(absolute[i,k]),'mase':float(scaled[i,k]),'mean_signed_error':float(signed[i,k])})
    origin = pd.DataFrame(origin_records)
    seed = origin.groupby(['model','seed','outcome','group'],as_index=False)[['mae','mase','mse','mean_signed_error']].mean()
    seed['rmse'] = np.sqrt(seed.mse)
    summaries=[]
    for (model,outcome,group),part in seed.groupby(['model','outcome','group'],sort=True):
        record={'model':model,'outcome':outcome,'group':group,'mae':part.mae.mean(),
                'mase':part.mase.mean(),'rmse':float(np.sqrt(part.mse.mean())),
                'mean_signed_error':part.mean_signed_error.mean()}
        for metric in ('mae','mase','rmse'):
            record.update({metric+'_seed_sd':part[metric].std(ddof=1),
                           metric+'_seed_min':part[metric].min(),metric+'_seed_max':part[metric].max()})
        summaries.append(record)
    return {'origin':origin,'seed':seed,'scores':pd.DataFrame(summaries),'areas':pd.DataFrame(area_records)}


def comparison_pairs(include_optional):
    pairs=[('gnn_real','gnn_no_graph'),('gnn_real','gnn_shuffled'),
           ('gnn_real','gradient_boosting_own'),('gnn_real','gradient_boosting_neighbours')]
    if include_optional:
        pairs.append(('gnn_real','gnn_no_base'))
    return pairs


def compare(origin,include_optional,seeds=(11,29,47),dm=dm_from_losses):
    """One predeclared MAE family; undefined tests still reserve family slots."""
    selected = origin.loc[origin.group.eq('all') & origin.outcome.isin(REPORTED)]
    if not np.isfinite(selected.mae).all() or (selected.mae<0).any():
        raise ValueError('Origin MAE losses must be finite and nonnegative')
    if selected.duplicated(['model','seed','outcome','origin']).any():
        raise ValueError('Duplicate origin loss records')
    models = set(x for pair in comparison_pairs(include_optional) for x in pair)
    canonical_origins = sorted(selected.origin.unique())
    if not canonical_origins:
        raise ValueError('No comparison origins supplied')
    series={}
    for model in models:
        for outcome in REPORTED:
            part = selected.loc[selected.model.eq(model) & selected.outcome.eq(outcome)]
            if set(part.origin)!=set(canonical_origins):
                raise ValueError('Comparison origin calendars differ or model missing')
            if any(set(p.seed)!=set(seeds) for _,p in part.groupby('origin')):
                raise ValueError('Comparison seed sets differ')
            series[model,outcome] = part.groupby('origin').mae.mean().reindex(canonical_origins).to_numpy()
    records=[]
    for a,b in comparison_pairs(include_optional):
        for outcome in REPORTED:
            h=12 if outcome=='total_12' else int(outcome)
            record={'model_a':a,'model_b':b,'outcome':outcome,'h':h,'origins':len(canonical_origins),
                    'statistic':np.nan,'p_raw':np.nan,'status':'defined'}
            try:
                statistic,p = dm(series[a,outcome],series[b,outcome],h)
                if not np.isfinite(statistic) or not np.isfinite(p) or not 0<=p<=1:
                    raise ValueError('Nonfinite/invalid DM statistic or p-value')
                record.update(statistic=float(statistic),p_raw=float(p))
            except (ArithmeticError,ValueError) as error:
                record['status']='undefined: '+str(error)
            records.append(record)
    result=pd.DataFrame(records)
    result['family_size']=len(result)
    result['p_holm']=holm(result.p_raw)
    return result


def moran(values,edges):
    """Row-standardised rook weights; observed isolates retained with zero rows."""
    values=np.asarray(values,dtype=np.float64)
    edges=np.asarray(edges,dtype=int).reshape(-1,2)
    if not np.isfinite(values).all():
        raise ValueError('Missing/nonfinite area errors are not zero-error cases')
    source=np.r_[edges[:,0],edges[:,1]]; target=np.r_[edges[:,1],edges[:,0]]
    degree=np.bincount(source,minlength=len(values))
    centred=values-values.mean(); s0=int((degree>0).sum())
    if not s0 or centred@centred==0:
        return np.nan
    return float(len(values)/s0*np.sum(centred[source]*centred[target]/degree[source])/(centred@centred))


def spatial_diagnostics(areas,ctx):
    records=[]
    for (model,outcome),part in areas.groupby(['model','outcome']):
        part=part.set_index('postcode').reindex(ctx.codes)
        for column,label in (('mae','absolute'),('mase','training_scaled_absolute'),('mean_signed_error','signed')):
            records.append({'model':model,'outcome':outcome,'error_type':label,
                            'moran_i':moran(part[column].to_numpy(),ctx.edges),'observed_areas':len(ctx.codes),
                            'weights':'row-standardised rook; observed isolates zero rows'})
    difference=pd.DataFrame(columns=['postcode','outcome','real_minus_shuffled_mase'])
    if {'gnn_real','gnn_shuffled'}.issubset(set(areas.model)):
        left=areas.loc[areas.model.eq('gnn_real')].set_index(['postcode','outcome']).mase
        right=areas.loc[areas.model.eq('gnn_shuffled')].set_index(['postcode','outcome']).mase
        if set(left.index)!=set(right.index):
            raise ValueError('Spatial difference area/outcome sets differ')
        difference=(left-right.reindex(left.index)).rename('real_minus_shuffled_mase').reset_index()
    return pd.DataFrame(records),difference
