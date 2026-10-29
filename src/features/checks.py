"""Short real-panel leakage and mask checks; no fitting or forecasts."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.frozen import frozen_protocol
from evaluation.protocol import training_calendar
from evaluation.baselines import validation_rows
from features.panel import Panel, load_panel
from features.builder import FeatureBuilder


def main():
    cfg, signature = frozen_protocol()
    rows = validation_rows(cfg)
    through = str(pd.Period(rows.origin.max(),freq='M')+12)
    panel = load_panel(through=through)
    origins = ['2010-01','2018-11','2019-08','2020-08','2021-08','2021-10']
    comparisons = 0
    for origin in origins:
        changed = panel.targets.copy()
        changed[:,panel.months > origin] = 9876543
        alternative = Panel(panel.codes,panel.months,changed,panel.observed,panel.edges)
        left,right = FeatureBuilder(panel),FeatureBuilder(alternative)
        for spatial in (False,True):
            for h in range(1,13):
                np.testing.assert_array_equal(left.at(origin,h,spatial,False),right.at(origin,h,spatial,False))
                assert np.all(left.at(origin,h,spatial,False)[~panel.observed] == 0)
                comparisons += 1
    eligibility = []
    for fit_origin in rows.fit_origin.drop_duplicates():
        sample,mask = training_calendar(fit_origin,cfg['splits']['training_first_target'])
        count = 0
        for i,origin in enumerate(sample):
            for h in np.flatnonzero(mask[i])+1:
                assert pd.Period(cfg['splits']['training_first_target'],freq='M') <= origin+h <= pd.Period(fit_origin,freq='M')
                count += 1
        eligibility.append({'fit_origin':fit_origin,'eligible_sample_horizon_cells':count})
    assert rows.last_target.max() <= cfg['splits']['test']['first_origin']
    result = {'protocol_sha256':signature,'feature_mutation_checks_passed':comparisons,
              'origins_checked':origins,'eligibility':eligibility,'unknown_nodes_zero_input':True,
              'last_target_available_to_runner':through,'test_forecasts_or_losses':0,'model_fits':0}
    Path('reports/experiments/t02_leakage_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
