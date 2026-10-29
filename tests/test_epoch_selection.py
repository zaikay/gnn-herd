import numpy as np
import pandas as pd
import pytest

from evaluation.epoch_selection import select_epoch


def test_negative_loss_uses_decrease_share_and_available_edge_window():
    curve = pd.DataFrame({'epoch':np.arange(1,76),'training_poisson_loss':[-1.]*10+[-101.]*65})
    epoch,result = select_epoch(curve)
    assert epoch==15
    assert result.smoothed_loss.iloc[0]==-1
    assert result.share_total_decrease.iloc[13]==pytest.approx(.8)
    assert result.share_total_decrease.iloc[14]==1


def test_no_total_decrease_rejected():
    with pytest.raises(ValueError,match='no positive'):
        select_epoch(pd.DataFrame({'epoch':np.arange(1,76),'training_poisson_loss':np.ones(75)}))
