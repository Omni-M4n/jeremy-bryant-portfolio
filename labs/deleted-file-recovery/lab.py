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

LIMITS = ['This parser accepts only the generated 32 KiB FAT12 layout and one-cluster deleted entries. It is not a general recovery tool.', 'A known-file hash match checks this training file. Missing entries or different bytes do not establish that all old data is gone or why it changed.']

def analyse(case):
    data = case['data']; exact(data, 'entries')
    decisions, observations = {}, []
    for row in rows(data['entries']):
        exact(row, 'id directory_present cluster_allocated declared_size candidate_hex known_sha256')
        require(type(row['directory_present']) is bool and type(row['cluster_allocated']) is bool, 'flags must be booleans')
        integer(row['declared_size'], maximum=4096); sha(row['known_sha256'])
        candidate = rawhex(row['candidate_hex'])
        if not row['directory_present']:
            require(not candidate and row['declared_size'] == 0 and not row['cluster_allocated'], 'absent entry has contradictory fields')
            answer = 'no-directory-candidate'
        elif row['cluster_allocated'] or row['declared_size'] > 512: answer = 'outside-recovery-model'
        else:
            require(row['declared_size'] > 0, 'this model requires a nonempty deleted file')
            if len(candidate) != row['declared_size']: answer = 'candidate-size-differs'
            elif hashlib.sha256(candidate).hexdigest() != row['known_sha256']: answer = 'candidate-content-differs'
            else: answer = 'matches-known-training-file'
        decisions[row['id']] = answer
        observations.append(f"{row['id']}: directory present={row['directory_present']}; declared bytes={row['declared_size']}; candidate bytes={len(candidate)}; cluster allocated={row['cluster_allocated']}.")
    return result(decisions, observations)

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
