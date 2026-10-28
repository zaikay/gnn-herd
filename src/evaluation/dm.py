"""Adapt origin-averaged loss series to dieboldmariano 1.1.0's interface."""
from math import isfinite


def dm_loss_inputs(loss_a, loss_b, horizon):
    a, b = list(map(float, loss_a)), list(map(float, loss_b))
    if len(a) != len(b) or not 0 < horizon < len(a):
        raise ValueError('Aligned loss series and 0 < horizon < origins required')
    if not all(isfinite(x) and x >= 0 for x in a + b):
        raise ValueError('Losses must be finite and nonnegative')
    return ([0.0] * len(a), a, b), {
        'loss': lambda actual, predicted: predicted,
        'h': horizon, 'harvey_correction': True,
        'variance_estimator': 'bartlett', 'one_sided': False,
    }


def dm_from_losses(loss_a, loss_b, horizon):
    from importlib.metadata import version
    from dieboldmariano import dm_test
    if version('dieboldmariano') != '1.1.0':
        raise RuntimeError('Protocol requires dieboldmariano 1.1.0')
    args, kwargs = dm_loss_inputs(loss_a, loss_b, horizon)
    return dm_test(*args, **kwargs)
