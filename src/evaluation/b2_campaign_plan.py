"""Pre-run B2 graph eligibility, main selection, test family and seed partition."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.baselines import validation_rows

CORE=('real','shuffled','no_graph','without_base')
OPTIONAL=('learned','identity')
SEEDS=(11,29,47)
OUTCOMES=('1','6','12','total_12')


def graph_screen_decision(real_mae,learned_mae,identity_mae):
    if not np.isfinite([real_mae,learned_mae,identity_mae]).all() or min(real_mae,learned_mae,identity_mae)<0:
        raise ValueError('Finite nonnegative two-anchor monthly MAEs required')
    include=bool(learned_mae<real_mae and learned_mae<identity_mae)
    review=bool(identity_mae<real_mae and identity_mae<=.98*real_mae)
    return {'main_candidate_by_graph_MAE':'learned' if learned_mae<real_mae else 'real',
            'include_learned_and_identity':include,'main':None if review else ('learned' if include else 'real'),
            'requires_researcher_review':review,'edge_policy':'use_real_if_learned_fails_identity',
            'scores':{'real':float(real_mae),'learned':float(learned_mae),'identity':float(identity_mae)}}


def dm_family(main,include):
    if main not in ('real','learned') or (main=='learned' and not include):raise ValueError('Main model is not in campaign')
    opponents=['no_graph','shuffled','gradient_boosting_own','gradient_boosting_neighbours','without_base']
    pairs=[(main,other) for other in opponents]
    if include:pairs += [('learned','real'),('learned','identity')]
    return [(a,b,h) for a,b in pairs for h in OUTCOMES]


def seed_assignment(machines):
    if machines==1:return {'A':list(SEEDS)}
    if machines==2:return {'A':[11],'B':[29,47]}
    if machines==3:return {'A':[11],'B':[29],'C':[47]}
    raise ValueError('One to three machines supported')


def job_plan(cfg,include=False,machines=1):
    mapping=seed_assignment(machines)
    host={s:name for name,seeds in mapping.items() for s in seeds}
    rows=[]
    for condition in CORE+(OPTIONAL if include else ()):
        for fit_origin in validation_rows(cfg).fit_origin.drop_duplicates():
            for seed in SEEDS:
                reuse=bool(seed==11 and fit_origin in ('2019-08','2020-08') and condition in ('real','no_graph','learned','identity'))
                rows.append({'condition':condition,'fit_origin':fit_origin,'seed':seed,'machine':host[seed],
                    'epochs':100,'configuration_id':3,'reuse_screen':reuse,'new_fit':not reuse})
    return pd.DataFrame(rows)


def write_plan():
    from evaluation.frozen import frozen_protocol
    cfg,_=frozen_protocol('protocol-v2')
    out=Path('data/explore/t03/b2_campaign_preparation'); out.mkdir(parents=True,exist_ok=True)
    summary=[]
    for include in (False,True):
        for count in (1,):
            jobs=job_plan(cfg,include,count)
            name=f'jobs_{4+2*include}conditions_{count}machines.csv'
            jobs.to_csv(out/name,index=False)
            for machine,part in jobs.groupby('machine'):
                summary.append({'conditions':4+2*include,'machines':count,'machine':machine,'seeds':','.join(map(str,sorted(part.seed.unique()))),
                    'fit_identities':len(part),'reused_screen_fits':int(part.reuse_screen.sum()),'new_fits':int(part.new_fit.sum())})
    pd.DataFrame(summary).to_csv(out/'seed_partition_summary.csv',index=False)
    pd.DataFrame(dm_family('real',False),columns=['main','opponent','outcome']).to_csv(out/'dm_family_core20.csv',index=False)
    pd.DataFrame(dm_family('learned',True),columns=['main','opponent','outcome']).to_csv(out/'dm_family_extended28.csv',index=False)
    (out/'index.md').write_text('# B2 campaign preparation: calendar/rules only\n\nSingle original laptop; all seeds 11,29,47. Architecture and selection rules supplied by researcher on 2 November 2026. No fits or test evaluation.\n\n'+'\n'.join(f'- [{p.name}]({p.name}): `evaluation.b2_campaign_plan`.' for p in sorted(out.iterdir()) if p.name!='index.md')+'\n',encoding='utf-8')
    print(pd.DataFrame(summary).to_string(index=False))


if __name__=='__main__':write_plan()
