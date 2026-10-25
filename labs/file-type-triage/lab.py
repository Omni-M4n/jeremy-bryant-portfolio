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

LIMITS = ['A matching signature is a format clue, not proof that the whole file is valid or safe.', 'An extension mismatch alone does not establish malware. Only PNG and SQLite signatures are recognized here.']

def analyse(case):
    data = case['data']; exact(data, 'files')
    decisions, observations = {}, []
    for row in rows(data['files']):
        exact(row, 'id name prefix_hex size reported_mime')
        require(isinstance(row['name'], str) and re.fullmatch(r'item-[0-9]{2}\.(?:png|dat|db|sqlite|sqlite3|txt)', row['name']), 'unsupported sample name')
        integer(row['size'], maximum=100000)
        prefix = rawhex(row['prefix_hex'], 16)
        require(len(prefix) == min(row['size'], 16), 'prefix length disagrees with size')
        option(row['reported_mime'], {'image/png', 'application/octet-stream', 'application/vnd.sqlite3', 'text/plain'})
        if not row['size']: answer = 'empty-file'
        elif prefix.startswith(b'\x89PNG\r\n\x1a\n'):
            answer = 'png-signature-extension-' + ('agrees' if row['name'].endswith('.png') else 'differs')
        elif prefix.startswith(b'SQLite format 3\x00'):
            answer = 'sqlite-signature-extension-' + ('agrees' if Path(row['name']).suffix in {'.db', '.sqlite', '.sqlite3'} else 'differs')
        else: answer = 'type-undetermined'
        decisions[row['id']] = answer
        observations.append(f"{row['id']}: {len(prefix)} prefix bytes inspected from {row['size']} bytes; reported label={row['reported_mime']}.")
    return result(decisions, observations)

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
