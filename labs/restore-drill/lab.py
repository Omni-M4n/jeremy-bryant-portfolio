"""Bounded fictional evidence reasoning. Read README.md before use."""
from datetime import datetime, timezone, timedelta
import hashlib
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
ROOT = Path(__file__).resolve().parent
LAB_ID = ROOT.name

def exact(value, keys):
    require(isinstance(value, dict) and set(value) == set(keys.split()), 'missing or unsupported fields')

def integer(value, minimum=0, maximum=10**20):
    require(type(value) is int and minimum <= value <= maximum, 'integer outside supported range')

def option(value, choices):
    require(isinstance(value, str) and value in choices, 'unsupported option')

def label(value):
    require(isinstance(value, str) and re.fullmatch(r'[a-z0-9][a-z0-9-]{0,39}', value), 'invalid record ID')

def sha(value):
    require(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value), 'expected lowercase SHA-256')

def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value), 'use whole UTC seconds ending Z')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def rows(value, minimum=1):
    require(isinstance(value, list) and minimum <= len(value) <= 20, 'unsupported record count')
    seen = set()
    for row in value:
        require(isinstance(row, dict) and 'id' in row, 'record object required')
        label(row['id'])
        require(row['id'] not in seen, 'duplicate record ID')
        seen.add(row['id'])
    return value

def rawhex(value, maximum=4096):
    require(isinstance(value, str) and len(value) <= maximum * 2 and re.fullmatch(r'(?:[0-9a-f]{2})*', value) is not None, 'invalid bounded hexadecimal bytes')
    return bytes.fromhex(value)

def result(decisions, observations):
    return {'decisions': decisions, 'observations': observations, 'limitations': LIMITS}

LIMITS = ['A local byte-copy drill does not establish application startup, permissions, cloud availability, full-machine recovery or a disaster recovery time.', 'The supplied worksheet times and ages are fictional. The practical receipt separately records actual copy and validation durations.']

def inventory(value):
    output = {}
    for row in rows(value, 0):
        exact(row, 'id name size sha256'); sha(row['sha256']); integer(row['size'], maximum=100000)
        require(row['id'] not in {'inventory','recovery-time','recovery-point'}, 'record ID collides with summary decision')
        require(isinstance(row['name'], str) and re.fullmatch(r'item-[0-9]{2}\.txt', row['name']), 'unsupported inventory name')
        require(row['name'] not in output, 'duplicate inventory name')
        output[row['name']] = row
    return output

def analyse(case):
    data = case['data']; exact(data, 'expected restored measured_ms target_ms backup_age_minutes maximum_age_minutes')
    expected, restored = inventory(data['expected']), inventory(data['restored'])
    require(expected, 'expected inventory must not be empty')
    for name in expected.keys() & restored.keys(): require(expected[name]['id'] == restored[name]['id'], 'same filename has conflicting ID')
    for key in ('measured_ms','target_ms','backup_age_minutes','maximum_age_minutes'): integer(data[key], maximum=10**9)
    decisions, observations = {}, []
    for name, row in expected.items():
        found = restored.get(name)
        answer = 'file-missing' if found is None else ('file-matches' if row['size'] == found['size'] and row['sha256'] == found['sha256'] else 'file-differs')
        decisions[row['id']] = answer
        observations.append(f"{row['id']}: expected {name}, {row['size']} bytes; restored entry present={found is not None}.")
    extras = sorted(restored.keys() - expected.keys())
    decisions['inventory'] = 'inventory-has-extra' if extras else 'inventory-no-extras'
    decisions['recovery-time'] = 'within-time-target' if data['measured_ms'] <= data['target_ms'] else 'over-time-target'
    decisions['recovery-point'] = 'within-data-age-target' if data['backup_age_minutes'] <= data['maximum_age_minutes'] else 'older-than-data-age-target'
    observations.append(f"Unexpected names={','.join(extras) or 'none'}; restore={data['measured_ms']}/{data['target_ms']} ms; backup age={data['backup_age_minutes']}/{data['maximum_age_minutes']} minutes.")
    return result(decisions, observations)

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
