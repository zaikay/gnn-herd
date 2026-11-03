"""Tag-locked authority shared by final-test commands; no data values loaded here."""
from dataclasses import dataclass
from datetime import datetime,timezone
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import pandas as pd

TAG='protocol-v7-test'
SPEC=Path('configs/protocol_v7_test.json')
NOTE=Path('reports/protocol/protocol_v7_final_test.md')
INVENTORY=Path('reports/protocol/protocol_v7_inventory.json')
PANEL=Path('data/processed/t02_panel.npz')
ROOT=Path('data/processed/t03_final_test')
CODE=(
 'src/models/final_test_runtime.py','src/models/final_test.py','src/features/sealed_panel.py',
 'src/evaluation/final_test.py','src/evaluation/final_test_metrics.py','src/evaluation/final_test_report.py',
 'src/models/b2_adaptive.py','src/models/b2.py','src/models/b_validation.py','src/models/screen_architectures.py',
 'src/models/gnn_checkpoint.py','src/models/gnn_fit.py','src/models/core_gnn.py',
 'src/features/panel.py','src/features/b2.py','src/features/gnn.py','src/features/builder.py',
 'src/evaluation/protocol.py','src/evaluation/baselines.py','src/evaluation/gate_c_metrics.py',
 'src/evaluation/dm.py','src/evaluation/v7_chain_evidence.py','src/evaluation/graph_diagnostics_report.py',
 'src/models/screen_cpu.py','src/evaluation/frozen.py',
 'configs/experiments.yaml','requirements.lock','requirements-baselines.lock','requirements-gnn.lock','pyproject.toml')


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8');temporary.replace(path)


def utc():return datetime.now(timezone.utc).isoformat()


def calendar(first,last,interval=3):
    dates=pd.period_range(first,last,freq='M').astype(str).tolist()
    return pd.DataFrame({'origin':dates,'fit_origin':[dates[(i//interval)*interval] for i in range(len(dates))],
        'last_target':[str(pd.Period(o,freq='M')+12) for o in dates]})


def validate_spec(spec):
    expected={'version':TAG,'status':'final','seeds':[11,29,47],'first_origin':'2022-10','last_origin':'2024-09','last_target':'2025-09',
      'epochs':100,'width':64,'rate':.003,'decay':.0001,'batch_size':2,'checkpoint_interval':5,'cpu_threads':8,
      'alpha_each':.025,'superiority':'one_sided_lower_loss','noninferiority_multiplier':1.01,'interval_confidence':.95,
      'seed_split':False,'refit_interval_months':3,'training_first_target':'2011-01',
      'conditions':['real','shuffled','no_graph','without_base'],
      'chains':{'Accuracy':['A7','A2','A1','A4','A3','A6','A5'],'Behavioural':['B3','B1','B2']}}
    for key,value in expected.items():
        if spec.get(key)!=value:raise RuntimeError(f'V7 decision mismatch: {key}')
    weights={'low':[.100818,.486487,.780161],'medium':[.687581,.784779,.831918],'high':[.492785,.659162,.682345]}
    for group,values in weights.items():
        if [spec['weights'][group][b] for b in ('1-3','4-6','7-12')]!=values:raise RuntimeError('Frozen six-decimal weights changed')
    for name,leaves in (('gradient_boosting_own',15),('gradient_boosting_neighbours',31)):
        if spec['boosting'][name]!={'learning_rate':.03,'max_leaf_nodes':leaves,'l2_regularization':1.,'max_iter':300,'early_stopping':False}:
            raise RuntimeError('Frozen boosting selection changed')
    if spec['battery_target_first']!='2025-07' or spec['battery_target_last']!='2025-09' or spec['machine']!='original_Windows_RTX4070_laptop':
        raise RuntimeError('Final timing/hardware decision changed')


@dataclass(frozen=True)
class Permit:
    spec:dict
    cfg:dict
    signature:str
    manifest:dict
    max_month:str='2024-09'


def authorize(check_host=True):
    # Tag checks happen before panel, hardware/GPU initialisation or test dates' values.
    tagged_hashes={}
    for path in (str(SPEC),str(NOTE),str(INVENTORY),*CODE):
        result=subprocess.run(['git','show',f'{TAG}:{Path(path).as_posix()}'],capture_output=True)
        if result.returncode:raise RuntimeError(f'Missing {TAG} or tagged file {path}; commit and tag the FINAL protocol first')
        local=Path(path).read_bytes().replace(b'\r\n',b'\n')
        tagged=result.stdout.replace(b'\r\n',b'\n')
        if local!=tagged:raise RuntimeError(f'Working file differs from {TAG}: {path}')
        tagged_hashes[path]=hashlib.sha256(tagged).hexdigest()
    spec=json.loads(SPEC.read_text());validate_spec(spec)
    if 'Status: FINAL' not in NOTE.read_text(encoding='utf-8'):raise RuntimeError('The tagged protocol is not marked FINAL')
    inventory=json.loads(INVENTORY.read_text())
    for path,digest in inventory['private_visual_sha256'].items():
        if sha(path)!=digest:raise RuntimeError('Private figure source differs from frozen inventory')
    if check_host:
        if platform.system()!='Windows' or platform.node()!=inventory['hardware']['computer'] or platform.platform()!=inventory['hardware']['os']:
            raise RuntimeError('Final fits/evaluation require the approved original Windows laptop')
        for name,pinned in inventory['packages'].items():
            if version(name)!=pinned:raise RuntimeError(f'Software inventory differs: {name}')
        if platform.python_version()!=inventory['python']:raise RuntimeError('Python inventory differs')
    import yaml
    cfg=yaml.safe_load(Path('configs/experiments.yaml').read_text())
    panel_manifest=json.loads(Path('data/processed/t02_panel_manifest.json').read_text())
    panel_hash=sha(PANEL)
    if panel_hash!=panel_manifest['panel_sha256'] or panel_hash!=inventory['panel_sha256']:raise RuntimeError('Frozen panel bytes changed')
    graphs={str(p):sha(p) for p in sorted(Path('data/processed/t03_graphs').glob('shuffled_seed*.npz'))}
    if graphs!=inventory['shuffled_graph_sha256']:raise RuntimeError('Frozen shuffled graph bytes changed')
    manifest={'tag':TAG,'tagged_file_sha256':tagged_hashes,'panel_sha256':panel_hash,'graphs':graphs,'inventory':inventory,'spec':spec}
    signature=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    return Permit(spec,cfg,signature,manifest)


def bind(permit):
    path=ROOT/'manifest.json'
    expected={'signature':permit.signature,**permit.manifest}
    if path.exists() and json.loads(path.read_text())!=expected:raise RuntimeError('Existing final-test manifest differs; no overwrite')
    write_json(path,expected)


def all_models(spec):return list(spec['boosting'])+['B2_'+c for c in spec['conditions']]


def require_complete(permit):
    rows=calendar(permit.spec['first_origin'],permit.spec['last_origin'])
    expected={(s,o) for s in permit.spec['seeds'] for o in rows.fit_origin.unique()}
    for name in all_models(permit.spec):
        root=ROOT/name;path=root/'complete.json'
        if not path.exists():raise RuntimeError(f'Locked evaluation withheld: {name} incomplete')
        marker=json.loads(path.read_text())
        if marker['signature']!=permit.signature or marker['fits']!=24 or marker['origins']!=24:raise RuntimeError('Invalid final completion marker')
        records=pd.read_csv(root/'fit_records.csv',dtype={'fit_origin':str})
        if len(records)!=24 or set(zip(records.seed,records.fit_origin))!=expected:raise RuntimeError('Missing/duplicate final fits')
        required={str(root/'fit_records.csv'),*(str(root/f'predictions_seed{s}.npz') for s in permit.spec['seeds'])}
        required.update(str(Path(p)) for p in records.checkpoint)
        required.update(str(root/f'seed{s}_{o}'/'fit.json') for s,o in expected)
        if set(marker['artifact_sha256'])!=required:raise RuntimeError('Incomplete final checkpoint/forecast hash inventory')
        if not records.signature.eq(permit.signature).all():raise RuntimeError('Fit signatures differ')
        for path,expected_sha in marker['artifact_sha256'].items():
            if sha(path)!=expected_sha:raise RuntimeError(f'Final artifact changed: {path}')
