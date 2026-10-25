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

LIMITS = ['This is a fictional SQLite schema with explicit UTC times, not a Chrome/Firefox profile parser. No real browser history is read.', 'Records do not identify the person at the keyboard or prove page attention. Missing history can reflect deletion, private browsing, collection gaps or no visit.']

def analyse(case):
    data = case['data']; exact(data, 'events')
    events = rows(data['events']); decisions, observations = {}, []
    for row in events:
        exact(row, 'id kind time url session state received expected')
        option(row['kind'], {'history', 'download', 'cache'})
        timestamp(row['time']); label(row['session'])
        require(isinstance(row['url'], str) and re.fullmatch(r'https?://[a-z0-9-]+\.test/[a-z0-9/._-]*', row['url']), 'use reserved training URL')
        integer(row['received'], maximum=100000); integer(row['expected'], maximum=100000)
        require(row['received'] <= row['expected'], 'received exceeds expected bytes')
        if row['kind'] == 'download':
            option(row['state'], {'complete', 'interrupted', 'in-progress'})
            require(row['state'] != 'complete' or row['received'] == row['expected'], 'complete record contradicts byte counts')
        else: require(row['state'] == 'recorded' and row['received'] == row['expected'] == 0, 'non-download fields contradict kind')
    for row in events:
        linked = [other['id'] for other in events if other['kind'] == 'history' and other['session'] == row['session'] and other['url'] == row['url'] and 0 <= (timestamp(row['time']) - timestamp(other['time'])).total_seconds() <= 60 and other['id'] != row['id']]
        if row['kind'] == 'history': answer = 'history-record'
        elif row['kind'] == 'cache': answer = 'cache-linked' if linked else 'cache-without-linked-history'
        elif row['state'] != 'complete': answer = 'download-incomplete'
        else: answer = 'download-complete-linked' if linked else 'download-complete-unlinked'
        decisions[row['id']] = answer
        observations.append(f"{row['id']}: kind={row['kind']}; earlier same-session URL records={','.join(linked) or 'none'}; bytes={row['received']}/{row['expected']}.")
    return result(decisions, observations)

if __name__ == '__main__':
    raise SystemExit(main(ROOT, LAB_ID, analyse))
