import json

import geopandas as gpd
import pytest
from shapely.geometry import Polygon, box

from geography.states import assign_states, valid_polygons


def frames():
    states = gpd.GeoDataFrame({'state_code':['2','1'],'state_name':['B','A']},
                             geometry=[box(1,0,2,1),box(0,0,1,1)],crs=9473)
    poas = gpd.GeoDataFrame({'postcode':['0800','1000']},
                           geometry=[box(.5,0,1.5,1),box(1,0,2,1)],crs=9473)
    return poas,states


def test_largest_overlap_exact_tie_code_order_and_cross_border():
    poas,states = frames()
    result = assign_states(poas,states,numerical_area_tolerance_m2=0)
    assert result.state_code.tolist() == ['1','2']
    assert result.cross_border.tolist() == [True,False]
    assert result.coverage_ok.all()
    assert json.loads(result.overlap_shares.iloc[0]) == {'1':.5,'2':.5}
    assert result.postcode.iloc[0] == '0800'


def test_gaps_are_reported_without_filling_or_assigning_by_postcode():
    poas,states = frames()
    poas.geometry = [box(-1,0,1,1),box(3,0,4,1)]
    result = assign_states(poas,states,numerical_area_tolerance_m2=0)
    assert not result.coverage_ok.any()
    assert result.uncovered_area_m2.tolist() == [1,1]
    assert result.state_code.tolist() == ['1','']


def test_invalid_polygon_rejected_not_repaired():
    poas,_ = frames()
    poas.loc[0,'geometry'] = Polygon([(0,0),(1,1),(1,0),(0,1),(0,0)])
    with pytest.raises(ValueError,match='invalid'):
        valid_polygons(poas,'toy')


def test_overlapping_states_require_review():
    poas,states = frames()
    states.loc[0,'geometry'] = box(.5,0,2,1)
    result = assign_states(poas,states,numerical_area_tolerance_m2=0)
    assert not result.coverage_ok.iloc[0]
    assert result.overlap_excess_m2.iloc[0] == .5
