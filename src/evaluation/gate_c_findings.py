"""Descriptive Gate C statements from released validation score tables."""
import numpy as np
import pandas as pd

from evaluation.gate_c_metrics import REPORTED


def findings(scores,dm):
    overall=scores.loc[scores.group.eq('all')].set_index(['model','outcome'])
    records=[]
    for outcome in REPORTED:
        real=overall.loc[('gnn_real',outcome)]
        shuffled=overall.loc[('gnn_shuffled',outcome)]
        test=dm.loc[dm.model_a.eq('gnn_real') & dm.model_b.eq('gnn_shuffled') & dm.outcome.eq(outcome)].iloc[0]
        records.append({'outcome':outcome,'real_mae':float(real.mae),'shuffled_mae':float(shuffled.mae),
            'real_minus_shuffled_mae_percent':float((real.mae/shuffled.mae-1)*100),
            'real_mase':float(real.mase),'shuffled_mase':float(shuffled.mase),
            'mae_direction':'lower' if real.mae<shuffled.mae else 'higher' if real.mae>shuffled.mae else 'equal',
            'mase_direction':'lower' if real.mase<shuffled.mase else 'higher' if real.mase>shuffled.mase else 'equal',
            'p_holm':float(test.p_holm)})
    comparison=pd.DataFrame(records)
    worse=comparison.mae_direction.eq('higher').all() and comparison.mase_direction.eq('higher').all()
    better=comparison.mae_direction.eq('lower').all() and comparison.mase_direction.eq('lower').all()
    answer=('No: real graph is worse than shuffled on both MAE and MASE for every reported outcome.' if worse else
            'Real graph has lower MAE and MASE for every reported outcome; inspect corrected DM results and limitations.' if better else
            'The real-versus-shuffled finding is mixed across outcomes or metrics; inspect the outcome table.')
    return answer,comparison


def executive_summary(scores,dm):
    answer,comparison=findings(scores,dm)
    overall=scores.loc[scores.group.eq('all')].set_index(['model','outcome'])
    lines=['## Gate C finding','','**'+answer+'** This is validation development evidence for the frozen T-GCN implementation, not a claim that geography never matters or that individual behaviour was identified.','']
    for opponent,label in (('gnn_no_graph','no-graph GNN'),('gradient_boosting_own','own-history boosting'),('gradient_boosting_neighbours','neighbour-history boosting')):
        if all(overall.loc[('gnn_real',h),'mae']>overall.loc[(opponent,h),'mae'] for h in REPORTED):
            p=dm.loc[dm.model_b.eq(opponent),'p_holm']
            evidence=' All four MAE-loss comparisons have Holm-adjusted p < 0.05.' if len(p)==4 and np.isfinite(p).all() and p.lt(.05).all() else ''
            lines.append(f'Real graph also has higher primary MAE than {label} at every reported outcome.'+evidence)
    if 'gnn_no_base' in set(scores.model):
        p=dm.loc[dm.model_b.eq('gnn_no_base'),'p_holm']
        if all(overall.loc[('gnn_real',h),'mase']<overall.loc[('gnn_no_base',h),'mase'] for h in REPORTED):
            lines += ['','Removing the explicit installed-base channel worsens MASE at every reported outcome. Primary-MAE differences are mixed and none of the four ablation comparisons has Holm-adjusted p < 0.05.' if len(p)==4 and p.ge(.05).all() else
                      'Removing the installed-base channel worsens MASE at every reported outcome; see the primary-MAE ablation tests.']
    lines += ['','The corrected family contains '+str(len(dm))+' comparisons. P-values are conditional on the frozen development protocol and fixed seeds; seed spread is reported separately. Review Gate C before any further experiments or hybrids. No tuning change, refit or sealed-test evaluation is proposed here.','']
    return lines,comparison
