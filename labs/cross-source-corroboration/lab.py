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

def corrected_timestamp(value, error):
    observed = timestamp(value)
    if error is None:
        return None
    integer(error, -86400, 86400)
    try:
        return observed - timedelta(seconds=error)
    except OverflowError as exc:
        raise ValueError('corrected UTC timestamp must remain within years 0001-9999') from exc

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

LIMITS = ['A shared ID and compatible time interval support a link within this fictional model; IDs and logs can be reused, copied or wrong.', 'Clock correction is supplied evidence, not a fitted value chosen to force agreement. Timing alone does not identify a person or establish causation.']

def analyse(case):
    data = case['data']; exact(data, 'sources records pairs')
    sources, records = {}, {}
    for row in rows(data['sources']):
        exact(row, 'id kind clock_error_seconds uncertainty_seconds collection_note')
        option(row['kind'], {'host', 'web', 'packet'})
        if row['clock_error_seconds'] is not None: integer(row['clock_error_seconds'], -86400, 86400)
        integer(row['uncertainty_seconds'], maximum=3600)
        option(row['collection_note'], {'closed-copy', 'partial-export', 'generated-packets'})
        sources[row['id']] = row
    for row in rows(data['records']):
        exact(row, 'id source time request_id object_sha256'); timestamp(row['time']); sha(row['object_sha256'])
        label(row['source']); require(row['source'] in sources, 'unknown source')
        if row['request_id'] is not None: label(row['request_id'])
        # Validate every corrected date, including records not named in a pair.
        corrected_timestamp(row['time'], sources[row['source']]['clock_error_seconds'])
        records[row['id']] = row
    decisions, observations = {}, []
    for pair in rows(data['pairs']):
        exact(pair, 'id left right')
        label(pair['left']); label(pair['right'])
        require(pair['left'] in records and pair['right'] in records and pair['left'] != pair['right'], 'invalid comparison records')
        left, right = records[pair['left']], records[pair['right']]
        require(left['source'] != right['source'], 'comparison needs different sources')
        a, b = sources[left['source']], sources[right['source']]
        corrected, spread = None, a['uncertainty_seconds'] + b['uncertainty_seconds']
        if a['clock_error_seconds'] is not None and b['clock_error_seconds'] is not None:
            corrected = abs(int((corrected_timestamp(left['time'], a['clock_error_seconds']) - corrected_timestamp(right['time'], b['clock_error_seconds'])).total_seconds()))
        if left['request_id'] and right['request_id'] and left['request_id'] != right['request_id']: answer = 'identifiers-conflict'
        elif left['object_sha256'] != right['object_sha256']: answer = 'content-conflict'
        elif not left['request_id'] or not right['request_id']: answer = 'insufficient-link'
        elif corrected is None: answer = 'clock-unresolved'
        elif corrected > spread: answer = 'time-conflict'
        else: answer = 'link-supported-within-clock-bounds'
        decisions[pair['id']] = answer
        observations.append(f"{pair['id']}: corrected separation={corrected if corrected is not None else 'unknown'} seconds; combined uncertainty={spread} seconds; sources={left['source']},{right['source']}.")
    return result(decisions, observations)

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
