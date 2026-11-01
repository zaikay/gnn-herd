"""Calendar-and-fit-record cost projection only; never loads panel/test arrays."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.protocol import splits,training_calendar


def project(cfg,b_records,boosting_records,observed_areas):
    dates=splits(cfg); refits=dates.loc[dates.block.eq('test'),'fit_origin'].drop_duplicates().tolist()
    seeds=cfg['tuning']['seeds']; schedule=[]; detail=[]
    for origin in refits:
        samples,eligible=training_calendar(origin,cfg['splits']['training_first_target'])
        schedule.append({'fit_origin':origin,'sample_origins':len(samples),'batches_per_epoch':int(np.ceil(len(samples)/2)),
                         'eligible_target_cells':int(eligible.sum())*observed_areas,'seeds':len(seeds)})
    calendar=pd.DataFrame(schedule)
    for kind,records in [('GPU B',b_records),('CPU boosting',boosting_records)]:
        for condition,condition_records in records.groupby('condition'):
            recent=sorted(condition_records.fit_origin.unique())[-4:]
            for seed in seeds:
                reference=condition_records.loc[condition_records.fit_origin.isin(recent)&condition_records.seed.eq(seed)]
                if len(reference)!=4:raise ValueError('Four recent fit timings per seed required')
                if kind=='GPU B':
                    work=np.array([65*np.ceil(len(training_calendar(o,cfg['splits']['training_first_target'])[0])/2) for o in reference.fit_origin])
                    rates=reference.fit_seconds.to_numpy()/work
                else:
                    rates=reference.seconds.to_numpy()/reference.rows.to_numpy()
                for row in calendar.itertuples():
                    future_work=65*row.batches_per_epoch if kind=='GPU B' else row.eligible_target_cells
                    detail.append({'device':kind,'condition':condition,'seed':seed,'fit_origin':row.fit_origin,
                        'reference_first':recent[0],'reference_last':recent[-1],
                        'seconds_low':float(np.quantile(rates,.25)*future_work),
                        'seconds_central':float(np.median(rates)*future_work),'seconds_high':float(np.quantile(rates,.75)*future_work)})
    detail=pd.DataFrame(detail)
    summary=detail.groupby(['device','condition'],as_index=False).agg(fits=('seed','size'),
        hours_low=('seconds_low','sum'),hours_central=('seconds_central','sum'),hours_high=('seconds_high','sum'))
    for column in ('hours_low','hours_central','hours_high'):summary[column]/=3600
    return calendar,detail,summary


def saved_cost_projection(cfg,observed_areas):
    from models.b_validation import ROOT,ORDER
    from models.screen_cpu import OLD,CONDITIONS
    b=pd.concat([pd.read_csv(ROOT/c/'fit_records.csv') for c in ORDER],ignore_index=True)
    old=pd.read_csv(OLD/'fit_records.csv'); parts=[]
    for condition in CONDITIONS:
        selection=json.loads((OLD/f'{condition}_selection.json').read_text())
        parts.append(old.loc[old.condition.eq(condition)&old.config_id.eq(selection['selected_config_id'])])
    boost=pd.concat(parts).drop_duplicates(['condition','seed','fit_origin'])
    return project(cfg,b,boost,observed_areas)
