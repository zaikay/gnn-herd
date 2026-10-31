"""Protocol-v3-screen candidates; independent of the frozen core architecture."""
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def neighbour_operator(edges, observed):
    observed=np.asarray(observed,dtype=bool)
    pairs=np.asarray(edges,dtype=int).reshape(-1,2)
    pairs=pairs[observed[pairs].all(axis=1)]
    row=np.r_[pairs[:,0],pairs[:,1]]; col=np.r_[pairs[:,1],pairs[:,0]]
    degree=np.bincount(row,minlength=len(observed))
    values=1/degree[row] if len(row) else np.empty(0)
    operator=torch.sparse_coo_tensor(torch.tensor(np.array([row,col]),dtype=torch.long),
        torch.tensor(values,dtype=torch.float32),(len(observed),len(observed))).coalesce()
    return operator,degree>0


class ScreenNetwork(nn.Module):
    def __init__(self,candidate,edges,observed,width=64,graph_enabled=True,channels=6):
        super().__init__()
        if candidate not in ('A','B','C'):raise ValueError('Unknown screen candidate')
        self.candidate=candidate; self.width=width; self.graph_enabled=graph_enabled
        operator,has=neighbour_operator(edges,observed)
        self.register_buffer('operator',operator)
        self.register_buffer('observed',torch.as_tensor(observed,dtype=torch.bool))
        self.register_buffer('has_neighbour',torch.as_tensor(has,dtype=torch.bool))
        self.gates=nn.Linear(channels+width,2*width)
        self.candidate_layer=nn.Linear(channels+width,width)
        self.head=nn.Linear(width,12)
        if candidate=='A':
            self.neighbour_gates=nn.Linear(channels+width,2*width,bias=False)
            self.neighbour_candidate=nn.Linear(channels+width,width,bias=False)
        else:
            self.neighbour_head=nn.Linear(width,12,bias=False)
            nn.init.zeros_(self.neighbour_head.weight)
        if candidate=='C':
            nn.init.zeros_(self.head.weight); nn.init.zeros_(self.head.bias)

    def mean(self,values):
        values=values*self.observed[None,:,None]
        b,n,f=values.shape
        result=torch.sparse.mm(self.operator,values.permute(1,0,2).reshape(n,b*f))
        return result.reshape(n,b,f).permute(1,0,2)*self.observed[None,:,None]

    def neighbour_contribution(self,values):
        if not self.graph_enabled:return torch.zeros_like(values)
        return self.mean(values)

    def late_correction(self,hidden):
        if not self.graph_enabled:return hidden.new_zeros((*hidden.shape[:2],12))
        gap=(self.mean(hidden)-hidden)*self.has_neighbour[None,:,None]
        return self.neighbour_head(gap)

    def forward(self,inputs,base=None):
        if inputs.ndim!=4 or inputs.shape[2]!=len(self.observed):raise ValueError('Misaligned screen inputs')
        hidden=inputs.new_zeros(inputs.shape[0],inputs.shape[2],self.width)
        for current in inputs.unbind(dim=1):
            current=current*self.observed[None,:,None]
            z=torch.cat((current,hidden),dim=-1)
            gates=self.gates(z)
            if self.candidate=='A':gates=gates+self.neighbour_gates(self.neighbour_contribution(z))
            reset,update=torch.sigmoid(gates).chunk(2,dim=-1)
            z=torch.cat((current,reset*hidden),dim=-1)
            candidate=self.candidate_layer(z)
            if self.candidate=='A':candidate=candidate+self.neighbour_candidate(self.neighbour_contribution(z))
            hidden=(update*hidden+(1-update)*torch.tanh(candidate))*self.observed[None,:,None]
        logits=self.head(hidden)
        if self.candidate!='A':logits=logits+self.late_correction(hidden)
        if self.candidate=='C':
            if base is None or base.shape!=logits.shape:raise ValueError('C needs aligned OOS base forecasts')
            rates=base*torch.exp(logits)
        else:rates=F.softplus(logits).clamp_min(1e-6)
        return rates*self.observed[None,:,None]
