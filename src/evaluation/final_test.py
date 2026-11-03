"""One locked v7 final evaluation. All six model sets must be complete first."""
import argparse
from dataclasses import replace
import json
import numpy as np
import pandas as pd
from models.final_test_runtime import authorize,bind,require_complete,ROOT,PANEL,calendar,all_models,write_json,sha,utc


def context(panel,rows,cfg):
    from evaluation.gate_c_metrics import Context
    from evaluation.baselines import mase_scales
    from evaluation.protocol import maturity_groups
    codes=panel.codes[panel.observed]
    truth=np.stack([panel.targets[panel.observed,panel.index(o)+1:panel.index(o)+13].astype(float) for o in rows.origin])
    scales=np.stack([mase_scales(panel,fit,cfg) for fit in rows.fit_origin])
    base=np.cumsum(panel.inputs,axis=1,dtype=np.float64)
    groups=np.stack([maturity_groups(base[panel.observed,panel.index(o)],codes) for o in rows.origin])
    reindex={old:i for i,old in enumerate(np.flatnonzero(panel.observed))}
    edges=np.array([(reindex[a],reindex[b]) for a,b in panel.edges if a in reindex and b in reindex],dtype=int).reshape(-1,2)
    return Context(rows.origin.to_numpy(dtype='U7'),codes,truth,scales,groups,edges,rows.fit_origin.to_numpy(dtype='U7'))


def receipt(root,signature,hashes):
    """An interrupted evaluation can resume only with identical frozen inputs."""
    path=root/'evaluation_started.json';identity={'signature':signature,'forecast_sha256':hashes}
    if path.exists():
        saved=json.loads(path.read_text())
        if any(saved[k]!=v for k,v in identity.items()):raise RuntimeError('Locked evaluation inputs changed; refusing repeat')
    else:write_json(path,{**identity,'started_at':utc()})


def run(permit):
    from filelock import FileLock
    from threadpoolctl import threadpool_limits
    from features.sealed_panel import load_prefix
    from evaluation.final_test_metrics import analyse
    from evaluation.final_test_report import write_outputs
    # This lock is shared with BOTH fitting commands. No target access before release.
    ROOT.mkdir(parents=True,exist_ok=True)
    with FileLock(str(ROOT/'workflow.lock'),timeout=0):
        bind(permit);require_complete(permit)
        result_root=ROOT/'evaluation';result_root.mkdir(exist_ok=True)
        if (result_root/'complete.json').exists():
            saved=json.loads((result_root/'complete.json').read_text())
            if saved['signature']!=permit.signature:raise RuntimeError('Evaluation signature changed')
            for path,digest in saved['artifact_sha256'].items():
                if sha(path)!=digest:raise RuntimeError('Completed evaluation artifact changed; no silent re-evaluation')
            print(json.dumps({'event':'final_evaluation_already_complete','report':saved['report']}));return
        rows=calendar(permit.spec['first_origin'],permit.spec['last_origin']);values={};hashes={}
        with np.load(PANEL,allow_pickle=False) as metadata:
            expected_codes=metadata['codes'][metadata['observed']]
        # Forecasts can be opened before targets; calendars/codes are checked afterward.
        identifiers=[]
        for model in all_models(permit.spec):
            values[model]={}
            for seed in permit.spec['seeds']:
                path=ROOT/model/f'predictions_seed{seed}.npz'
                with np.load(path,allow_pickle=False) as data:
                    np.testing.assert_array_equal(data['origins'],rows.origin.to_numpy())
                    np.testing.assert_array_equal(data['codes'],expected_codes)
                    if data['prediction'].shape!=(len(rows),len(expected_codes),12) or not np.isfinite(data['prediction']).all() or (data['prediction']<0).any():
                        raise RuntimeError('Final forecasts incomplete or invalid; targets remain sealed')
                    identifiers.append(data['codes'].copy());values[model][seed]=data['prediction'].copy()
                hashes[str(path)]=sha(path)
        receipt(result_root,permit.signature,hashes)
        # Only this locked production branch extends the permitted target prefix to Sep 2025.
        evaluation_permit=replace(permit,max_month=permit.spec['last_target'])
        panel=load_prefix(PANEL,permit.spec['last_target'],evaluation_permit)
        for codes in identifiers:np.testing.assert_array_equal(codes,panel.codes[panel.observed])
        with threadpool_limits(limits=1):
            ctx=context(panel,rows,permit.cfg);bundle,point=analyse(values,ctx,permit.spec)
            paths,report=write_outputs(bundle,ctx,permit.spec,result_root,scope='final_test')
        metadata={'signature':permit.signature,'report':str(report),'completed_at':utc(),
            'forecast_sha256':hashes,'artifact_sha256':{str(p):sha(p) for p in paths},'test_origins':24,
            'chain_orders':permit.spec['chains'],'alpha_each':.025,'weights':permit.spec['weights'],'model_refits_in_evaluation':0}
        write_json(result_root/'complete.json',metadata)
        print(json.dumps({'event':'final_test_evaluation_complete','report':str(report),'chains':bundle['chains'][['chain','candidate_id','status']].to_dict('records')}),flush=True)


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--run',action='store_true',required=True);parser.parse_args()
    permit=authorize();run(permit)


if __name__=='__main__':main()
