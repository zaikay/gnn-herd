import numpy as np

from geography.conditions import shuffle_graph, edge_set


def test_shuffle_preserves_degrees_cross_state_edges_and_seed():
    edges = np.array([[0,1],[1,2],[2,3],[3,4],[4,5],[0,5],[0,6]])
    states = np.array(['1']*6+['2','2'])
    result,diagnostics = shuffle_graph(edges,states,11)
    repeat,_ = shuffle_graph(edges,states,11)
    np.testing.assert_array_equal(result,repeat)
    np.testing.assert_array_equal(np.bincount(result.ravel(),minlength=8),np.bincount(edges.ravel(),minlength=8))
    assert {(a,b) for a,b in edge_set(result) if states[a]!=states[b]} == {(0,6)}
    assert len(edge_set(result)) == len(edges)
    assert not any(a==b for a,b in result)
    assert diagnostics.target_reached.all()
    assert diagnostics.accepted_swaps.sum() == 60
    assert np.bincount(result.ravel(),minlength=8)[7] == 0


def test_unmixable_state_is_flagged_without_relaxing_control():
    edges = np.array([[0,1]])
    result,diagnostics = shuffle_graph(edges,np.array(['1','1']),29)
    np.testing.assert_array_equal(result,edges)
    assert diagnostics.mixing_review_required.iloc[0]
    assert diagnostics.accepted_swaps.iloc[0] == 0
