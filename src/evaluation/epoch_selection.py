"""One-time epoch choice from existing pilot training losses only."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def select_epoch(curve, window=5, fraction=.98):
    np.testing.assert_array_equal(curve.epoch,np.arange(1,76))
    if not np.isfinite(curve.training_poisson_loss).all():
        raise ValueError('Pilot loss contains nonfinite values')
    # Trailing mean, using available epochs at the left edge, defines S_1.
    result = curve.copy()
    result['smoothed_loss'] = result.training_poisson_loss.rolling(window,min_periods=1).mean()
    first,last = result.smoothed_loss.iloc[[0,-1]]
    if first<=last:
        raise ValueError('Pilot has no positive total training-loss decrease')
    result['share_total_decrease'] = (first-result.smoothed_loss)/(first-last)
    epoch = int(result.loc[result.share_total_decrease.ge(fraction),'epoch'].iloc[0])
    return epoch,result


def main():
    records,curves = [],[]
    for width in (32,96):
        path = Path(f'data/processed/t03_gnn/pilot/real_seed11_width{width}_2020-08/training_curve.csv')
        epoch,curve = select_epoch(pd.read_csv(path))
        curve['hidden_size'] = width; curves.append(curve)
        records.append({'hidden_size':width,'first_epoch_98_percent':epoch,
            'smoothed_loss_epoch_1':float(curve.smoothed_loss.iloc[0]),
            'smoothed_loss_epoch_75':float(curve.smoothed_loss.iloc[-1]),
            'share_at_selected_epoch':float(curve.loc[curve.epoch.eq(epoch),'share_total_decrease'].iloc[0]),
            'source':path.as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    fixed = min(75,int(np.ceil(max(r['first_epoch_98_percent'] for r in records)/5)*5))
    result = {'approved_on':'2026-10-29','rule':'trailing 5-epoch mean, min_periods=1; (S1-SE)/(S1-S75)>=0.98; first crossing per width; ceil(max(E)/5)*5 capped at 75',
              'pilot_widths':records,'fixed_epochs':fixed,'uses_validation_or_test_scores':False}
    Path('reports/protocol/protocol_v2_epoch_selection.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    pd.concat(curves,ignore_index=True).to_csv('data/explore/t03/protocol_v2_epoch_selection.csv',index=False)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
