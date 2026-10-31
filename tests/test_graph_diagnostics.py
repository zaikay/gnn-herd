import numpy as np

from evaluation.graph_diagnostics import column_correlations, neighbour_gap


def test_correlations_are_within_area_and_flag_undefined():
    x = np.array([[1, 1, 3, np.nan], [2, 2, 3, np.nan],
                  [3, 3, 3, np.nan], [4, 4, 3, np.nan]], dtype=float)
    y = np.array([[2, 8, 1, 1], [4, 6, 2, 2], [6, 4, 3, 3], [8, 2, 4, 4]])
    r, n, status = column_correlations(x, y)
    np.testing.assert_allclose(r[:2], [1, -1])
    assert np.isnan(r[2:]).all()
    assert status.tolist() == ['defined', 'defined', 'constant_gap',
                               'no_neighbours_or_insufficient_pairs']
    assert n.tolist() == [4, 4, 4, 0]


def test_correlations_use_pairwise_finite_origins_and_constant_error():
    x = np.array([[1, 1], [2, 2], [3, 3], [4, 4]], dtype=float)
    y = np.array([[3, 7], [np.nan, 7], [7, 7], [9, 7]])
    r, n, status = column_correlations(x, y)
    assert r[0] == 1 and n[0] == 3
    assert np.isnan(r[1]) and status[1] == 'constant_signed_error'


def test_neighbour_gap_arithmetic_mean_and_isolates():
    level = np.array([[2., 4., 8., 99.], [3., 5., 9., 100.]])
    gap = neighbour_gap(level, np.array([[0, 1], [0, 2]]))
    np.testing.assert_allclose(gap[:, :3], [[4, -2, -6], [4, -2, -6]])
    assert np.isnan(gap[:, 3]).all()


def test_empty_graph_has_no_defined_gap():
    assert np.isnan(neighbour_gap(np.ones((3, 2)), np.empty((0, 2)))).all()
