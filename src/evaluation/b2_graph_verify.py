"""CPU-only audit of the completed, saved protocol-v6 graph screen."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from threadpoolctl import threadpool_limits


def main():
    from models.b2_runtime import authority,SCREEN,sha,require_screen
    from models.b2_adaptive import make_model
    from features.panel import load_panel
    from features.b2 import area_scale
    from evaluation.b2_graph_screen_report import load_screen,summarise,paths
    cfg,info=authority()
    assert json.loads((SCREEN/'manifest.json').read_text())==info
    checkpoints=[]; hashes={}
    with threadpool_limits(limits=1):
        _,ctx,values,records,curves=load_screen()
        for condition in values:
            for anchor in ctx.origins:
                path=paths(condition,anchor); panel=load_panel(through=anchor)
                scale=area_scale(panel,anchor)
                saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
                assert saved['completed_epochs']==saved['total_epochs']==100
                assert [r['epoch'] for r in saved['epoch_records']]==list(range(1,101))
                model=make_model(panel,condition,11,scale)
                model.load_state_dict(saved['model'],strict=True)
                np.testing.assert_array_equal(model.area_scale.numpy(),scale.astype(np.float32))
                for tensor in model.state_dict().values():
                    tensor=tensor.coalesce().values() if tensor.is_sparse else tensor
                    assert torch.isfinite(tensor).all()
                record=records.loc[records.condition.eq(condition)&records.anchor.eq(anchor)].iloc[0]
                assert sum(p.numel() for p in model.parameters())==record.parameter_count
                curve=curves.loc[curves.condition.eq(condition)&curves.anchor.eq(anchor)]
                assert curve.epoch.tolist()==list(range(1,101))
                assert np.isfinite(curve.training_poisson_loss).all()
                np.testing.assert_allclose(curve.training_poisson_loss.iloc[-1],record.training_loss,rtol=1e-12)
                checkpoints.append({'condition':condition,'anchor':anchor,'epochs':100,'parameters':int(record.parameter_count)})
                for name in ('checkpoint.pt','complete.json','prediction.npz'):hashes[str(path/name)]=sha(path/name)
                del model,saved
        bundle,decision=summarise(values,ctx)
        assert decision==require_screen()
        out=Path('data/explore/t03/b2_graph_screen')
        for name in ('origin','scores','seed','areas'):
            path=out/(name+'.csv.gz' if name=='areas' else name+'.csv')
            saved=pd.read_csv(path,dtype={'outcome':str,'postcode':str})
            current=bundle[name].copy()
            pd.testing.assert_frame_equal(saved,current,check_dtype=False,rtol=1e-10,atol=1e-11)
    real=decision['scores']['real']; learned=decision['scores']['learned']; identity=decision['scores']['identity']
    projection=pd.read_csv(out/'campaign_projection.csv')
    assert projection.condition.tolist()==['real','shuffled','no_graph','without_base']
    assert int(projection.new_fits.sum())==140 and int(projection.reused_fits.sum())==4
    result={'scope':'saved validation screen only','checkpoint_checks':checkpoints,'artifact_sha256':hashes,
        'decision':decision,'identity_improvement_percent':100*(real-identity)/real,
        'learned_worse_than_real_percent':100*(learned-real)/real,
        'new_screen_fit_hours':float(records.loc[records.condition.isin(['learned','identity']),'fit_seconds'].sum()/3600),
        'peak_new_screen_allocated_GiB':float(records.loc[records.condition.isin(['learned','identity']),'peak_gpu_memory_bytes'].max()/1024**3),
        'campaign_estimated_new_fit_hours':float(projection.estimated_new_fit_hours.sum()),
        'pooled_score_rows_verified':len(bundle['scores']),'origin_score_rows_verified':len(bundle['origin']),
        'gpu_use':False,'new_fits':0,'test_forecasts_or_losses':0}
    dest=Path('reports/experiments/t03_b2_graph_completion_verification.json')
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('artifact_sha256','checkpoint_checks')},indent=2))


if __name__=='__main__':main()
