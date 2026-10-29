"""Frozen first-order graph-convolutional GRU; no training on import."""
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def graph_operator(edges, observed, condition='real'):
    observed = np.asarray(observed,dtype=bool)
    n = len(observed)
    if condition not in {'real','no_graph','within_state_shuffled'}:
        raise ValueError('Unapproved graph condition')
    # Computational identity is never written back to the border graph.
    source = list(range(n)); target = list(range(n))
    if condition!='no_graph':
        for a,b in edges:
            if observed[a] and observed[b]:
                source.extend((int(a),int(b))); target.extend((int(b),int(a)))
    degree = np.bincount(source,minlength=n).astype(np.float64)
    weights = (degree[source]*degree[target])**-.5
    return torch.sparse_coo_tensor(torch.tensor([source,target],dtype=torch.long),
                                  torch.tensor(weights,dtype=torch.float32),(n,n)).coalesce()


class CoreGNN(nn.Module):
    def __init__(self,operator,observed,hidden_size,input_channels=6,horizons=12,rate_floor=1e-6):
        super().__init__()
        self.register_buffer('operator',operator)
        self.register_buffer('observed',torch.as_tensor(observed,dtype=torch.bool))
        self.hidden_size = hidden_size
        self.rate_floor = rate_floor
        self.gates = nn.Linear(input_channels+hidden_size,2*hidden_size)
        self.candidate = nn.Linear(input_channels+hidden_size,hidden_size)
        self.head = nn.Linear(hidden_size,horizons)

    def message(self,values):
        values = values*self.observed[None,:,None]
        b,n,f = values.shape
        result = torch.sparse.mm(self.operator,values.permute(1,0,2).reshape(n,b*f))
        return result.reshape(n,b,f).permute(1,0,2)*self.observed[None,:,None]

    def forward(self,inputs):
        if inputs.ndim!=4 or inputs.shape[2]!=len(self.observed):
            raise ValueError('Expected batch x time x node x channel tensor')
        hidden = inputs.new_zeros(inputs.shape[0],inputs.shape[2],self.hidden_size)
        for t in range(inputs.shape[1]):
            current = inputs[:,t]*self.observed[None,:,None]
            reset,update = torch.sigmoid(self.gates(self.message(torch.cat((current,hidden),dim=-1)))).chunk(2,dim=-1)
            candidate = torch.tanh(self.candidate(self.message(torch.cat((current,reset*hidden),dim=-1))))
            hidden = (update*hidden+(1-update)*candidate)*self.observed[None,:,None]
        return F.softplus(self.head(hidden)).clamp_min(self.rate_floor)*self.observed[None,:,None]


def poisson_loss(rates,targets,mask):
    if not bool(mask.any()):
        raise ValueError('No eligible target cells')
    mu = rates[mask].clamp_min(1e-6)
    return (mu-targets[mask]*mu.log()).mean()
