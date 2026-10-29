"""Frozen six-channel historical GNN windows and per-horizon training masks."""
import numpy as np
import pandas as pd

from evaluation.protocol import training_calendar


class GNNWindows:
    def __init__(self,panel,cfg):
        self.panel,self.cfg = panel,cfg
        self.lookback = cfg['splits']['lookback_months']
        if cfg['gnn_design']['channel_names'] != ['log1p_count','log1p_cumulative_base','month_sin','month_cos','observed_flag','isolate_flag']:
            raise ValueError('Unexpected frozen GNN input design')
        counts = panel.inputs
        base = np.cumsum(counts,axis=1,dtype=np.float64)
        months = pd.PeriodIndex(panel.months,freq='M').month.to_numpy()
        degree = np.bincount(panel.edges.ravel(),minlength=len(panel.codes))
        values = np.zeros((len(panel.months),len(panel.codes),6),dtype=np.float32)
        values[:,:,0] = np.log1p(counts.T)
        values[:,:,1] = np.log1p(base.T)
        values[:,:,2] = np.sin(2*np.pi*months[:,None]/12)
        values[:,:,3] = np.cos(2*np.pi*months[:,None]/12)
        values[:,:,4] = panel.observed[None,:]
        values[:,:,5] = (degree==0)[None,:]
        values[:,~panel.observed,:] = 0
        self.values = values

    def at(self,origin):
        end = self.panel.index(origin)+1
        if end<self.lookback:
            raise ValueError('Insufficient approved historical input months')
        return self.values[end-self.lookback:end].copy()

    def training(self,fit_origin):
        samples,calendar = training_calendar(fit_origin,self.cfg['splits']['training_first_target'])
        if self.panel.months[-1] != str(fit_origin):
            raise ValueError('Training panel must be truncated at the fit origin')
        targets = np.zeros((len(samples),len(self.panel.codes),12),dtype=np.float32)
        mask = np.broadcast_to(calendar[:,None,:],targets.shape).copy()
        mask &= self.panel.observed[None,:,None]
        for i,sample in enumerate(samples):
            for h in np.flatnonzero(calendar[i]):
                targets[i,self.panel.observed,h] = self.panel.targets[self.panel.observed,self.panel.index(str(sample+h+1))]
        return samples.astype(str).to_numpy(),targets,mask
