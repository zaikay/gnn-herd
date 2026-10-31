"""Small synthetic end-to-end check. Never reads any study GNN prediction."""
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from evaluation.gate_c import write_tables,write_report
from evaluation.gate_c_metrics import evaluate,compare,spatial_diagnostics
from evaluation.gate_c_fixtures import synthetic_fixture


def main():
    with threadpool_limits(limits=1):
        ctx,predictions=synthetic_fixture()
        bundle=evaluate(predictions,ctx)
        bundle['dm']=compare(bundle['origin'],True)
        without=compare(bundle['origin'].loc[lambda f:f.model.ne('gnn_no_base')],False)
        assert len(bundle['dm'])==20 and len(without)==16
        bundle['moran'],bundle['difference']=spatial_diagnostics(bundle['areas'],ctx)
        root=Path('data/explore/t03/gate_c_preflight/synthetic')
        roots={'explore':root/'exploration','visual':Path('visuals/t03/gate_c_preflight/synthetic'),
               'paper':Path('reports/figures/gate_c_preflight/synthetic')}
        write_tables(bundle,root)
        without.to_csv(root/'dm_tests_without_optional.csv',index=False)
        from visuals.gate_c import render,synthetic_geometry
        files=render(bundle,ctx,'synthetic',geometry=synthetic_geometry(ctx),roots=roots)
        report=root/'SYNTHETIC_report_fixture.md'
        write_report(bundle,{'source_kind':'synthetic'},output=report,data_root=root,figure_roots=roots)
        broken=[target for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')) if not (report.parent/target).exists()]
        assert not broken,broken
        for name in ('gnn_scaled_error_map','gnn_real_minus_shuffled_map'):
            plotted=pd.read_csv(roots['explore']/f'{name}.csv',dtype={'postcode':str})
            assert len(plotted)==7 and int((~plotted.evaluated).sum())==1
        assert set(bundle['scores'].outcome)==set(map(str,range(1,13)))|{'total_12'}
        info={'scope':'synthetic_fixture_only','models':len(predictions),'origins':len(ctx.origins),'areas':len(ctx.codes),
              'dm_family_sizes_tested':[16,20],'figure_csv_files_checked':len(files),
              'map_unknown_area_checked':True,'fixture_report_links':'passed',
              'gnn_study_prediction_files_opened':0,'study_gnn_comparisons_computed':0,
              'full_test_suite_run':False,'gpu_use':False,'threadpool_limit':1}
        Path('reports/experiments/t03_gate_c_synthetic_check.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
        print(json.dumps(info,indent=2))


if __name__=='__main__':
    main()
