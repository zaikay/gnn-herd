"""Per-area fit-history scaling for B2; original panel/features stay unchanged."""
import numpy as np
from features.gnn import GNNWindows


def area_scale(panel,fit_origin,first_target='2011-01'):
    start=panel.index(first_target); stop=panel.index(fit_origin)+1
    if stop<=start:raise ValueError('No training history for area scale')
    scale=np.ones(len(panel.codes),dtype=np.float64)
    history=panel.targets[panel.observed,start:stop]
    if not np.isfinite(history).all() or (history<0).any():raise ValueError('Invalid observed training history')
    scale[panel.observed]+=history.mean(axis=1,dtype=np.float64)
    return scale


class B2Windows(GNNWindows):
    def __init__(self,panel,cfg,scale):
        super().__init__(panel,cfg)
        scale=np.asarray(scale,dtype=np.float64)
        if scale.shape!=(len(panel.codes),) or not np.isfinite(scale).all() or (scale<1).any():raise ValueError('Positive fit-frozen area scales >= 1 required')
        self.scale=scale.copy()
        changed=panel.observed&(scale!=1)
        if changed.any():
            counts=panel.inputs[changed].astype(np.float64)
            self.values[:,changed,0]=np.log1p(counts.T/scale[None,changed]).astype(np.float32)
            base=np.cumsum(counts,axis=1,dtype=np.float64)
            self.values[:,changed,1]=np.log1p(base.T/scale[None,changed]).astype(np.float32)
