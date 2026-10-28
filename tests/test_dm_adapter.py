from math import sqrt

import pytest

from evaluation.dm import dm_loss_inputs


def test_dm_adapter_against_hand_computed_bartlett_hln_statistic():
    # Origin loss differences: [1,2,1,3,2,3]; n=6; mean=2.
    # Centred: [-1,0,-1,1,0,1]. gamma0=4/6, gamma1=-1/6.
    # h=2 Bartlett weight at lag1=1/2, so long-run variance=1/2.
    # Variance(mean)=1/12; HLN factor=sqrt(5/9).
    # Corrected statistic=2/sqrt(1/12)*sqrt(5/9)=sqrt(80/3).
    args, options = dm_loss_inputs([2, 4, 3, 5, 5, 7], [1, 2, 2, 2, 3, 4], 2)
    actual, a, b = args
    loss = options['loss']
    differences = [loss(y, p) - loss(y, q) for y, p, q in zip(actual, a, b)]
    assert differences == [1, 2, 1, 3, 2, 3]
    n = len(differences)
    mean = sum(differences) / n
    centred = [d - mean for d in differences]
    gamma0 = sum(d*d for d in centred) / n
    gamma1 = sum(centred[i]*centred[i-1] for i in range(1, n)) / n
    assert gamma0 == pytest.approx(2/3)
    assert gamma1 == pytest.approx(-1/6)
    h = options['h']
    variance_mean = (gamma0 + 2*(1-1/h)*gamma1) / n
    hln = sqrt((n+1-2*h+h*(h-1)/n)/n)
    statistic = mean/sqrt(variance_mean)*hln
    assert statistic == pytest.approx(sqrt(80/3), rel=1e-12)
    assert options['variance_estimator'] == 'bartlett'
    assert options['harvey_correction'] and not options['one_sided']
    # Sign must reverse when the model order reverses.
    reverse, reverse_options = dm_loss_inputs(b, a, 2)
    assert sum(reverse_options['loss'](y,p)-reverse_options['loss'](y,q)
               for y,p,q in zip(*reverse))/n == -mean


def test_dm_adapter_rejects_misaligned_or_nonfinite_losses():
    with pytest.raises(ValueError):
        dm_loss_inputs([1, 2], [1], 1)
    with pytest.raises(ValueError):
        dm_loss_inputs([1, float('nan')], [1, 2], 1)
