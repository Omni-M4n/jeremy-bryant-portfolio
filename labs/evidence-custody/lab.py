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

LIMITS = ['Matching hashes support byte identity at the recorded checks; they do not prove who created the file or that its contents are true.', 'This is a dummy logical-file copy, not disk imaging, a write blocker, or a legal chain-of-custody process.']

def analyse(case):
    data = case['data']; exact(data, 'files')
    decisions, observations = {}, []
    for row in rows(data['files']):
        exact(row, 'id source acquired_utc handler source_before copy source_after handling')
        label(row['source'])
        acquired = timestamp(row['acquired_utc'])
        require(isinstance(row['handler'], str) and (not row['handler'] or re.fullmatch(r'handler-[0-9]{2}', row['handler'])), 'use a fictional handler alias')
        for key in ('source_before', 'copy', 'source_after'): sha(row[key])
        require(isinstance(row['handling'], list) and len(row['handling']) <= 8, 'invalid handling log')
        previous = acquired
        for event in row['handling']:
            exact(event, 'time action')
            current = timestamp(event['time'])
            require(current >= previous, 'handling times must be ordered after acquisition')
            option(event['action'], {'copy', 'hash', 'store'})
            previous = current
        if row['source_before'] != row['source_after']: answer = 'source-changed'
        elif row['copy'] != row['source_before']: answer = 'copy-differs'
        elif not row['handler'] or not row['handling']: answer = 'handling-record-incomplete'
        else: answer = 'copy-matches-recorded-source'
        decisions[row['id']] = answer
        observations.append(f"{row['id']}: source stable={row['source_before'] == row['source_after']}; copy matches initial hash={row['copy'] == row['source_before']}; handling entries={len(row['handling'])}; handler recorded={bool(row['handler'])}.")
    return result(decisions, observations)

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
