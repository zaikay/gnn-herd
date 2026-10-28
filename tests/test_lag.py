import pandas as pd

from audit.lag import recent_tail


def test_recent_tail_sums_nationally_and_keeps_last_24():
    months = pd.period_range("2020-01", periods=30, freq="M").astype(str).tolist()
    panel = pd.DataFrame({"postcode": ["0800"] * 30 + ["2000"] * 30,
                          "month": months + months, "count": [1] * 30 + [2] * 30})
    tail = recent_tail(panel)
    assert len(tail) == 24
    assert tail.index[0] == "2020-07"
    assert tail.index[-1] == "2022-06"
    assert tail.eq(3).all()
