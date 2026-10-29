"""P7 state assignment from approved LGA polygons; never repair or fill gaps."""
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import union_all, clip_by_rect

from evaluation.frozen import frozen_protocol
from geography.graph import spatial_areas


def valid_polygons(frame, label):
    bad = frame.geometry.isna() | frame.geometry.is_empty | ~frame.geometry.is_valid
    bad |= ~frame.geometry.geom_type.isin(['Polygon','MultiPolygon'])
    if bad.any():
        raise ValueError(f'{label}: {int(bad.sum())} invalid/missing polygons; researcher review required')


def assign_states(poas, states, numerical_area_tolerance_m2=1.0):
    """One square metre permits floating-point overlay noise, never gap filling."""
    valid_polygons(poas,'POA'); valid_polygons(states,'State')
    if poas.crs.to_epsg()!=9473 or states.crs.to_epsg()!=9473:
        raise ValueError('State overlaps require EPSG:9473')
    if poas.postcode.duplicated().any() or states.state_code.duplicated().any():
        raise ValueError('Duplicate POA/state identifiers')
    result = []
    for row in poas.itertuples():
        area = row.geometry.area
        overlaps = []
        pieces = []
        for j in states.sindex.query(row.geometry,predicate='intersects'):
            state = states.iloc[j]
            # Exact bounding-box restriction avoids overlaying the complete
            # state coastline for a small POA. If fast clipping produces an
            # invalid intermediate, use the untouched state polygon instead.
            local = clip_by_rect(state.geometry,*row.geometry.bounds)
            if not local.is_valid:
                local = state.geometry
            piece = row.geometry.intersection(local)
            overlap = piece.area
            if overlap>0:
                overlaps.append((str(state.state_code),str(state.state_name),float(overlap)))
                pieces.append(piece)
        overlaps.sort(key=lambda item:(-item[2],item[0]))
        # Union only the local intersections: subtracting the entire national
        # coastline for every POA is needlessly costly and gives the same set.
        gap = float(row.geometry.difference(union_all(pieces)).area) if pieces else float(area)
        shares = {code:overlap/area for code,name,overlap in overlaps}
        excess = max(0.0,sum(x[2] for x in overlaps)-area)
        result.append({'postcode':row.postcode,'state_code':overlaps[0][0] if overlaps else '',
            'state_name':overlaps[0][1] if overlaps else '', 'poa_area_m2':area,
            'covered_area_m2':sum(x[2] for x in overlaps),'uncovered_area_m2':gap,
            'overlap_excess_m2':excess,'cross_border':len(overlaps)>1,
            'overlap_shares':json.dumps(shares,sort_keys=True),
            'coverage_ok':bool(overlaps) and gap<=numerical_area_tolerance_m2 and excess<=numerical_area_tolerance_m2})
    return pd.DataFrame(result)


def main():
    cfg,signature = frozen_protocol('protocol-v1.1')
    # Frozen prose field starts with "existing "; the file path is unchanged.
    source = Path(cfg['state_assignment']['source'].removeprefix('existing '))
    output = Path('data/explore/t03'); output.mkdir(parents=True,exist_ok=True)
    poas = gpd.read_file(source,layer='POA_2021_AUST_GDA2020')
    poas['postcode'] = poas.POA_CODE_2021.astype(str)
    poas,_ = spatial_areas(poas)
    lgas = gpd.read_file(source,layer=cfg['state_assignment']['layer'])
    missing = lgas.geometry.isna()
    pd.DataFrame(lgas.loc[missing].drop(columns='geometry')).to_csv(output/'nonspatial_state_carrier_rows.csv',index=False)
    lgas = lgas.loc[~missing].copy()
    valid_polygons(lgas,'Spatial LGA'); valid_polygons(poas,'POA')
    lgas = lgas.to_crs(9473); poas = poas.to_crs(9473)
    valid_polygons(lgas,'Projected LGA')
    states = lgas.rename(columns={'STATE_CODE_2021':'state_code','STATE_NAME_2021':'state_name'})
    states['state_code'] = states.state_code.astype(str)
    states = states[['state_code','state_name','geometry']].dissolve(by=['state_code','state_name'],as_index=False)
    result = assign_states(poas,states)
    result.to_csv(output/'state_assignment.csv',index=False)
    summary = {'protocol_sha256':signature,'postal_areas':len(result),'states':len(states),
        'cross_border_areas':int(result.cross_border.sum()),'coverage_failures':int((~result.coverage_ok).sum()),
        'uncovered_area_m2':float(result.uncovered_area_m2.sum()),
        'largest_uncovered_area_m2':float(result.uncovered_area_m2.max()),
        'numerical_area_tolerance_m2':1.0,'nonspatial_lga_rows':int(missing.sum()),
        'rule':'largest EPSG:9473 land-area overlap; exact ties by state code; no repair or gap filling'}
    (output/'state_assignment_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if not result.coverage_ok.all():
        raise ValueError('State coverage gaps/overlaps: stop for researcher review; see state_assignment.csv')


if __name__=='__main__':
    main()
