"""Approved B2 learned adjacency and node-identity controls (protocol v6)."""
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from models.b2 import B2Network


class AdaptiveB2(B2Network):
    def __init__(self,edges,observed,width,scale,condition):
        if condition not in ('learned','identity'):raise ValueError(condition)
        super().__init__(edges,observed,width,scale,graph_enabled=False)
        self.condition=condition
        self.E1=nn.Parameter(torch.empty(len(observed),10))
        self.E2=nn.Parameter(torch.empty(len(observed),10))
        nn.init.normal_(self.E1,std=.01); nn.init.normal_(self.E2,std=.01)
        if int(np.sum(observed))<2:raise ValueError('At least two observed areas required')
        if condition=='identity':
            self.gates=nn.Linear(26+width,2*width)
            self.candidate_layer=nn.Linear(26+width,width)
            del self.neighbour_head

    def adjacency(self):
        logits=F.relu(self.E1@self.E2.T)
        forbidden=torch.eye(len(self.observed),dtype=torch.bool,device=logits.device)|~self.observed[None,:]
        return logits.masked_fill(forbidden,float('-inf')).softmax(dim=1)

    def forward(self,inputs,base=None):
        # One adjacency per forward call; never once per timestep.
        adjacency=self.adjacency() if self.condition=='learned' else None
        identity=torch.cat((self.E1,self.E2),dim=-1) if self.condition=='identity' else None
        hidden=inputs.new_zeros(inputs.shape[0],inputs.shape[2],self.width)
        for current in inputs.unbind(dim=1):
            if identity is not None:current=torch.cat((current,identity[None].expand(current.shape[0],-1,-1)),dim=-1)
            current=current*self.observed[None,:,None]
            reset,update=torch.sigmoid(self.gates(torch.cat((current,hidden),dim=-1))).chunk(2,dim=-1)
            proposal=self.candidate_layer(torch.cat((current,reset*hidden),dim=-1))
            hidden=(update*hidden+(1-update)*torch.tanh(proposal))*self.observed[None,:,None]
        logits=self.head(hidden)
        if adjacency is not None:
            # Learned neighbours also apply to geographical isolates.
            logits=logits+self.neighbour_head(adjacency@hidden-hidden)
        return (F.softplus(logits)*self.area_scale[None,:,None]).clamp_min(1e-6)*self.observed[None,:,None]


class B2WithoutBase(B2Network):
    def __init__(self,edges,observed,width,scale):
        super().__init__(edges,observed,width,scale,True)
        self.gates=nn.Linear(5+width,2*width)
        self.candidate_layer=nn.Linear(5+width,width)


def make_model(panel,condition,seed,scale):
    from models.b_validation import graph_edges
    if condition in ('learned','identity'):return AdaptiveB2(panel.edges,panel.observed,64,scale,condition)
    if condition=='without_base':return B2WithoutBase(panel.edges,panel.observed,64,scale)
    return B2Network(graph_edges(panel,condition,seed),panel.observed,64,scale,condition!='no_graph')


def parameter_counts(nodes=2641):
    observed=np.ones(nodes,dtype=bool); edges=np.empty((0,2),dtype=int); scale=np.ones(nodes)
    result={}
    for condition in ('learned','identity'):
        model=AdaptiveB2(edges,observed,64,scale,condition)
        result[condition]={'total':sum(p.numel() for p in model.parameters()),'embeddings':model.E1.numel()+model.E2.numel()}
    return result
