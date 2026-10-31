import json
import numpy as np
import pandas as pd
import pytest
from evaluation.gate_c_metrics import Context
from evaluation.screen_baseline_comparison import band_scores,gains,load_anchor_baselines


def context():
    return Context(np.array(['2019-08','2020-08']),np.array(['0001','0002','0003']),
        np.ones((2,3,12))*10,np.ones((2,3))*2,np.array([[0,1,2],[0,1,2]]),
        np.array([[0,1]]),np.array(['2019-08','2020-08']))


def test_band_metrics_hand_computed_and_pooled_rmse():
    ctx=context(); prediction=ctx.truth.copy()
    prediction[0,:,:3]+=2; prediction[1,:,:3]+=4
    prediction[1,:,3:6]+=6
    scores=band_scores({'toy':prediction},ctx)
    band=scores.loc[scores.anchor.eq('both_anchors')&scores.band.eq('1-3')]
    np.testing.assert_allclose(band.mae,3)
    np.testing.assert_allclose(band.mase,1.5)
    np.testing.assert_allclose(band.rmse,np.sqrt(10))
    next_band=scores.loc[scores.anchor.eq('both_anchors')&scores.band.eq('4-6')]
    np.testing.assert_allclose(next_band.rmse,np.sqrt(18))
    assert len(scores)==3*4*4
    assert set(scores.group)=={'all','low','medium','high'}


def test_gains_sign_and_zero_reference_and_c_base():
    ctx=context()
    values={f'{c}_{g}':ctx.truth+1 for c in 'ABC' for g in ('real','no_graph')}
    values.update({'frozen':ctx.truth+2,'improved':ctx.truth,'C_base':ctx.truth+3})
    comparison=gains(band_scores(values,ctx),['frozen','improved'])
    np.testing.assert_allclose(comparison.loc[comparison.reference.eq('frozen'),'mae_gain'],1)
    np.testing.assert_allclose(comparison.loc[comparison.reference.eq('frozen'),'mae_gain_percent'],50)
    assert comparison.loc[comparison.reference.eq('improved'),'mae_gain_percent'].isna().all()
    assert set(comparison.loc[comparison.reference.eq('C_base'),'candidate'])=={'C'}
    np.testing.assert_allclose(comparison.loc[comparison.reference.eq('C_base'),'mae_gain'],2)


def test_maturity_groups_are_origin_dependent():
    ctx=context(); ctx.groups[1]=[2,0,1]
    prediction=ctx.truth+np.array([1.,3.,9.])[None,:,None]
    scores=band_scores({'toy':prediction},ctx)
    pooled=scores.loc[scores.anchor.eq('both_anchors')&scores.band.eq('1-3')].set_index('group')
    np.testing.assert_allclose(pooled.loc[['low','medium','high'],'mae'],[2,6,5])
    assert pooled.loc['low','rmse']==np.sqrt(5)


def test_loads_frozen_and_improved_predictions_aligned_without_refit(tmp_path,monkeypatch):
    from models import screen_cpu as cpu
    old=tmp_path/'old'; root=tmp_path/'new'; old.mkdir(); root.mkdir()
    monkeypatch.setattr(cpu,'OLD',old); monkeypatch.setattr(cpu,'ROOT',root)
    ctx=context()
    (old/'run_manifest.json').write_text(json.dumps({'panel_sha256':'same'}))
    (root/'cpu_manifest.json').write_text(json.dumps({'panel_sha256':'same'}))
    selections={}
    for condition in cpu.CONDITIONS:
        np.savez_compressed(old/f'{condition}_seed11.npz',prediction=(ctx.truth+np.array([1,2])[:,None,None])[::-1],
                            origins=ctx.origins[::-1],codes=ctx.codes)
        improved=condition==cpu.CONDITIONS[0]
        selections[condition]={'improved':improved,'old_tuning_mae':2.,'winner':{'tuning_mae':1. if improved else 3.,'parameters':{'x':1}}}
    (root/'boosting_selection.json').write_text(json.dumps(selections))
    condition=cpu.CONDITIONS[0]
    (root/f'{condition}_updated_complete.json').write_text(json.dumps({'parameters':{'x':1},'test_forecasts_or_losses':0}))
    np.savez_compressed(root/f'{condition}_updated_seed11.npz',prediction=ctx.truth,origins=ctx.origins,codes=ctx.codes)
    values,provenance=load_anchor_baselines(ctx)
    assert len(values)==3 and len(provenance['prediction_sha256'])==3
    np.testing.assert_array_equal(values[f'{condition}_frozen'][:,0,0],[11,12])
    (root/f'{condition}_updated_complete.json').unlink()
    with pytest.raises(ValueError,match='incomplete'):load_anchor_baselines(ctx)
