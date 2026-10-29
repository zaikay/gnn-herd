"""Origin-relative features; neither fitting nor target look-ahead occurs here."""
import numpy as np
import pandas as pd

from evaluation.protocol import training_calendar


class FeatureBuilder:
    def __init__(self, panel, lookback=24):
        self.panel, self.lookback = panel, lookback
        self.values = panel.inputs
        self.base = np.cumsum(self.values, axis=1, dtype=np.float64)
        n = len(panel.codes)
        all_source = np.r_[panel.edges[:, 0], panel.edges[:, 1]]
        all_target = np.r_[panel.edges[:, 1], panel.edges[:, 0]]
        self.isolated = np.bincount(all_source, minlength=n) == 0
        usable = panel.observed[all_target]
        source, target = all_source[usable], all_target[usable]
        degree = np.bincount(source, minlength=n)
        neighbour_sum = np.zeros_like(self.values, dtype=np.float64)
        np.add.at(neighbour_sum, source, self.values[target])
        self.neighbours = np.divide(neighbour_sum, degree[:, None],
            out=np.zeros_like(neighbour_sum), where=degree[:, None] > 0)
        self.neighbour_base = np.cumsum(self.neighbours, axis=1, dtype=np.float64)
        self.has_neighbour = degree > 0
        self._cache = {}

    def names(self, spatial):
        own = [f'own_lag_{k}' for k in range(1, self.lookback+1)]
        own += ['own_rolling_3','own_rolling_6','own_rolling_12','target_month_sin','target_month_cos',
                'own_cumulative_base','observed_flag','isolate_flag','horizon']
        return own + ([f'neighbour_lag_{k}' for k in range(1, self.lookback+1)] +
                      ['neighbour_cumulative_base','has_observed_neighbour_flag'] if spatial else [])

    def at(self, origin, horizon, spatial=False, observed_only=True):
        if not 1 <= horizon <= 12:
            raise ValueError('Frozen protocol supports horizons 1..12')
        t = self.panel.index(origin)
        if t < self.lookback-1:
            raise ValueError('Not enough historical inputs')
        key = (str(origin), bool(spatial))
        if key not in self._cache:
            indices = t - np.arange(self.lookback)
            own = np.log1p(self.values[:, indices])
            rolling = np.stack([np.log1p(self.values[:, t-k+1:t+1].mean(axis=1)) for k in (3,6,12)], axis=1)
            columns = [own, rolling, np.zeros((len(own), 2)), np.log1p(self.base[:, t])[:, None],
                       self.panel.observed[:, None], self.isolated[:, None], np.zeros((len(own), 1))]
            if spatial:
                columns.extend([np.log1p(self.neighbours[:, indices]),
                                np.log1p(self.neighbour_base[:, t])[:, None], self.has_neighbour[:, None]])
            self._cache[key] = np.concatenate(columns, axis=1).astype(np.float32)
        x = self._cache[key].copy()
        month = (pd.Period(origin, freq='M') + horizon).month
        x[:, self.lookback+3] = np.sin(2*np.pi*month/12)
        x[:, self.lookback+4] = np.cos(2*np.pi*month/12)
        x[:, self.lookback+8] = horizon
        x[~self.panel.observed] = 0
        return x[self.panel.observed] if observed_only else x

    def training(self, fit_origin, first_target='2011-01', spatial=False):
        sample_origins, eligible = training_calendar(fit_origin, first_target)
        n = int(self.panel.observed.sum())
        total = int(eligible.sum()) * n
        x = np.empty((total, len(self.names(spatial))), dtype=np.float32)
        y = np.empty(total, dtype=np.float64)
        row = 0
        for i, origin in enumerate(sample_origins):
            for h in np.flatnonzero(eligible[i]) + 1:
                x[row:row+n] = self.at(str(origin), int(h), spatial)
                target_index = self.panel.index(str(origin+h))
                if origin+h > pd.Period(fit_origin, freq='M'):
                    raise AssertionError('Training target exceeds fit origin')
                y[row:row+n] = self.panel.targets[self.panel.observed, target_index]
                row += n
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError('Nonfinite training data')
        return x, y

    def targets(self, origin):
        t = self.panel.index(origin)
        if t+12 >= len(self.panel.months):
            raise ValueError('Targets outside permitted panel view')
        return self.panel.targets[self.panel.observed, t+1:t+13].astype(np.float64)
