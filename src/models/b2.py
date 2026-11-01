"""B architecture with scaled input channels and a raw-count rate head."""
import numpy as np
import torch
from torch.nn import functional as F
from models.screen_architectures import ScreenNetwork


class B2Network(ScreenNetwork):
    def __init__(self,edges,observed,width,scale,graph_enabled=True):
        super().__init__('B',edges,observed,width,graph_enabled,channels=6)
        scale=np.asarray(scale,dtype=np.float32)
        if scale.shape!=(len(observed),) or not np.isfinite(scale).all() or (scale<1).any():raise ValueError('Invalid B2 scale')
        self.register_buffer('area_scale',torch.as_tensor(scale))
        self.unit_scale=bool((scale==1).all())

    def forward(self,inputs,base=None):
        if self.unit_scale:return super().forward(inputs)
        hidden=inputs.new_zeros(inputs.shape[0],inputs.shape[2],self.width)
        for current in inputs.unbind(dim=1):
            current=current*self.observed[None,:,None]
            reset,update=torch.sigmoid(self.gates(torch.cat((current,hidden),dim=-1))).chunk(2,dim=-1)
            candidate=self.candidate_layer(torch.cat((current,reset*hidden),dim=-1))
            hidden=(update*hidden+(1-update)*torch.tanh(candidate))*self.observed[None,:,None]
        logits=self.head(hidden)+self.late_correction(hidden)
        # The common numerical floor is applied in raw-count units, not scaled units.
        return (F.softplus(logits)*self.area_scale[None,:,None]).clamp_min(1e-6)*self.observed[None,:,None]
