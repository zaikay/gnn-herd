"""Small explicitly synthetic arrays, never fitted models or study forecasts."""
import numpy as np
import pandas as pd

from evaluation.gate_c_metrics import Context, BASELINES, GNN_MODELS


def synthetic_fixture(include_optional=True):
    rng=np.random.default_rng(20261031)
    origins=pd.period_range('2018-01',periods=18,freq='M').astype(str).to_numpy(dtype='U7')
    codes=np.array(['0800','1000','2000','3000','4000','5000'])
    truth=rng.poisson(3+np.arange(6)[None,:,None],size=(18,6,12)).astype(np.float64)
    scales=np.broadcast_to(1+np.arange(6)[None,:]/2,(18,6)).copy()
    groups=np.stack([np.roll(np.repeat([0,1,2],2),t%6) for t in range(18)])
    ctx=Context(origins,codes,truth,scales,groups,np.array([[0,1],[1,2],[2,3],[3,4]]),
                np.array([origins[(t//3)*3] for t in range(18)]))
    models=BASELINES+(GNN_MODELS if include_optional else GNN_MODELS[:-1])
    predictions={}
    for i,model in enumerate(models):
        predictions[model]={}
        fixed=np.maximum(0,truth+rng.normal(0,1.5,truth.shape)).astype(np.float32)
        for seed in (11,29,47):
            predictions[model][seed]=(fixed.copy() if model=='seasonal_naive' else
                np.maximum(0,truth+(i-3)*.1+rng.normal(0,1+i*.1,truth.shape)).astype(np.float32))
    return ctx,predictions


