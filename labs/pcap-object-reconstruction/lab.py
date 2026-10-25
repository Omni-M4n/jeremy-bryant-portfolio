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

LIMITS = ['The generated PCAP was not collected from a network. The parser handles one small plain HTTP/1.1 response with Content-Length, fixed IPv4/TCP headers and no TLS.', 'A complete matching object does not identify a user. Missing packets, encryption, conflicting overlaps, chunked bodies and compression need separate treatment.']

def analyse(case):
    data = case['data']; exact(data, 'content_length known_sha256 encrypted segments')
    integer(data['content_length'], 1, 4096); sha(data['known_sha256'])
    require(type(data['encrypted']) is bool, 'encrypted must be boolean')
    segments = rows(data['segments'], 0); positions, conflicts = {}, set()
    require(not data['encrypted'] or not segments, 'encrypted model cannot supply plaintext segments')
    for row in segments:
        exact(row, 'id offset bytes_hex'); integer(row['offset'], maximum=4095)
        content = rawhex(row['bytes_hex']); require(content, 'empty segments are unsupported')
        require(row['offset'] + len(content) <= data['content_length'], 'segment exceeds declared body')
        for index, byte in enumerate(content, row['offset']):
            if index in positions and positions[index] != byte: conflicts.add(index)
            positions[index] = byte
    missing = data['content_length'] - len(positions)
    if data['encrypted']: answer = 'encrypted-no-plaintext'
    elif conflicts: answer = 'conflicting-overlap'
    elif missing: answer = 'stream-incomplete'
    else:
        body = bytes(positions[index] for index in range(data['content_length']))
        answer = 'complete-matches-known-object' if hashlib.sha256(body).hexdigest() == data['known_sha256'] else 'complete-object-differs'
    return result({'stream': answer}, [f"Body positions present={len(positions)}/{data['content_length']}; missing={missing}; conflicting positions={len(conflicts)}; encrypted={data['encrypted']}."])

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
