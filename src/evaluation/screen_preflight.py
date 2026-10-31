"""Read-only preflight evidence for the prepared v3 screen."""
import hashlib
import json
from pathlib import Path
from models.screen_cpu import ROOT,base_jobs,extra_jobs,folder,write_json


def main():
    original=json.loads(Path('logs/t03_graph_diagnostics_frozen_before.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in original.items())
    raw=Path('logs/t03_v3_full_tests.log').read_bytes()
    log=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
    assert '114 passed' in log and 'FAILED' not in log and 'ERROR ' not in log
    records=[]
    for job in extra_jobs()+base_jobs():
        marker=folder(job)/'complete.json'
        if marker.exists():
            r=json.loads(marker.read_text()); records.append({'job':job['name'],'fit_seconds':r['fit_seconds'],'new_fit':r['new_fit']})
    assert not (ROOT/'gpu_manifest.json').exists()
    assert not Path('reports/experiments/t03_architecture_screen.md').exists()
    result={'full_tests_passed':114,'frozen_files_unchanged':len(original),'completed_cpu_jobs':records,
            'new_cpu_fit_seconds':sum(r['fit_seconds'] for r in records),'gpu_fits_by_agent':0,
            'screen_results_pending':True,'sealed_test_access':False}
    write_json('reports/experiments/t03_v3_screen_preflight.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
