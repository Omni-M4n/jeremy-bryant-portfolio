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

LIMITS = ['File timestamps can be copied or set explicitly; they do not identify a person or prove an action occurred at that exact time.', 'Creation/access behavior and timestamp precision vary by operating system and filesystem. ctime is not treated as a portable creation time.']

def analyse(case):
    data = case['data']; exact(data, 'snapshots')
    decisions, observations = {}, []
    for row in rows(data['snapshots']):
        exact(row, 'id operation before_sha256 after_sha256 before_mtime_ns after_mtime_ns')
        option(row['operation'], {'copyfile', 'copy2', 'write-and-reset-time'})
        sha(row['before_sha256']); sha(row['after_sha256'])
        integer(row['before_mtime_ns']); integer(row['after_mtime_ns'])
        equal_bytes = row['before_sha256'] == row['after_sha256']
        equal_time = row['before_mtime_ns'] == row['after_mtime_ns']
        answer = ('content-equal-time-equal' if equal_time else 'content-equal-time-differs') if equal_bytes else ('content-differs-time-equal' if equal_time else 'content-and-time-differ')
        decisions[row['id']] = answer
        observations.append(f"{row['id']}: hash equal={equal_bytes}; modified-time difference={row['after_mtime_ns'] - row['before_mtime_ns']} ns.")
    return result(decisions, observations)

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
