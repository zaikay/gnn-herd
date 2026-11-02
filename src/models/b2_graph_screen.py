"""Four researcher-run learned/identity fits; no study fitting without --run."""
import argparse
import json
import os
import numpy as np
from models.b2_runtime import SCREEN,ANCHORS,authority,bind_manifest,configure_gpu,screen_path,fit


def run():
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
    import torch
    from filelock import FileLock
    from features.panel import load_panel
    from features.b2 import B2Windows
    cfg,info=authority()
    with FileLock('data/processed/t03_gnn/gpu_fit.lock',timeout=0):
        configure_gpu(info); bind_manifest(SCREEN,info)
        for condition in ('learned','identity'):
            for anchor in ANCHORS:
                path=screen_path(condition,anchor)
                model,scale,record=fit(cfg,path,condition,11,anchor,info)
                panel=load_panel(through=anchor); windows=B2Windows(panel,cfg,scale)
                with torch.no_grad():prediction=model(torch.from_numpy(windows.at(anchor)[None]).cuda())[0,panel.observed].cpu().numpy()
                if not np.isfinite(prediction).all() or (prediction<0).any():raise RuntimeError('Invalid screen forecast')
                np.savez_compressed(path/'prediction.npz',prediction=prediction,codes=panel.codes[panel.observed],origin=anchor,scale=scale)
                print(json.dumps({'event':'graph_screen_fit_complete',**record}),flush=True)
                del model; torch.cuda.empty_cache()
    from evaluation.b2_graph_screen_report import report
    report()


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--run',action='store_true'); parser.add_argument('--report',action='store_true'); args=parser.parse_args()
    if args.run:run()
    elif args.report:
        from evaluation.b2_graph_screen_report import report
        report()
    else:
        from models.b2_adaptive import parameter_counts
        print(json.dumps({'fits':4,'epochs':100,'seed':11,'anchors':ANCHORS,'parameters':parameter_counts(),'gpu_use':False}))


if __name__=='__main__':main()
