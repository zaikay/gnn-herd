"""Targeted check for the saved-loss percentage calculation."""
import numpy as np
import pandas as pd

from evaluation.test_exploratory_relative import add_percentages


def test_relative_difference_uses_own_loss_and_leaves_zero_denominator_undefined():
    saved = pd.DataFrame({'difference': [2., -3., 0., -1.], 'own_loss': [8., 6., 0., 0.]})
    result = add_percentages(saved)
    np.testing.assert_allclose(result.difference_percent, [25., -50., np.nan, np.nan], equal_nan=True)
    pd.testing.assert_frame_equal(result.drop(columns='difference_percent'), saved)
