"""Load the authoritative tagged protocol without modifying Git."""
import hashlib
from pathlib import Path
import subprocess

import yaml


def frozen_protocol(tag='protocol-v1', require_working=True):
    if tag not in {'protocol-v1','protocol-v1.1'}:
        raise ValueError('Unknown approved protocol tag')
    result = subprocess.run(['git', 'show', f'{tag}:configs/experiments.yaml'],
                            capture_output=True, check=True)
    working = Path('configs/experiments.yaml').read_bytes()
    # Permit Windows line ending differences, never semantic protocol changes.
    tagged_text = result.stdout.decode('utf-8').replace('\r\n', '\n')
    if require_working and working.decode('utf-8').replace('\r\n', '\n') != tagged_text:
        raise RuntimeError(f'Working protocol differs from {tag}; approved version change required')
    return yaml.safe_load(tagged_text), hashlib.sha256(tagged_text.encode()).hexdigest()
