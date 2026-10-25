"""A small offline case model. Read README.md before running."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'rules-of-engagement'
ROOT = Path(__file__).resolve().parent

def fields(obj, names):
    require(isinstance(obj, dict) and set(obj) == set(names.split()), 'missing or unsupported fields')

def text(value):
    require(isinstance(value, str) and 0 < len(value.strip()) <= 500, 'expected short nonempty text')

def flag(value):
    require(type(value) is bool, 'expected true or false')

def number(value, low=0, high=3650):
    require(type(value) is int and low <= value <= high, 'number outside supported range')

def choice(value, choices):
    require(isinstance(value, str) and value in choices.split(), 'unsupported value')

def words(values, empty=False):
    require(isinstance(values, list) and (0 if empty else 1) <= len(values) <= 20, 'expected bounded list')
    for value in values:
        text(value)
    require(len(values) == len(set(values)), 'duplicate list item')

def rows(data, key):
    values = data[key]
    require(isinstance(values, list) and 1 <= len(values) <= 20, 'expected 1-20 rows')
    ids = []
    for row in values:
        require(isinstance(row, dict) and 'id' in row, 'row needs an id')
        text(row['id'])
        ids.append(row['id'])
    require(len(ids) == len(set(ids)), 'duplicate row id')
    return values

def output(decisions, observations):
    return {'decisions': decisions, 'observations': observations, 'limitations': [LIMIT]}

LIMIT = 'This reviews a fictional written plan. It grants no permission and launches no test.'

def hostname(value):
    text(value)
    require(len(value) <= 253 and value.endswith('.test'), 'expected a lowercase .test hostname')
    # A target is a name, not a URL; compare valid names without rewriting them.
    labels = value.split('.')
    require(all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in labels), 'invalid hostname label')

def analyse(case):
    d = case['data']
    fields(d, 'owned isolated approved stop_active start_minute end_minute targets allowed requests')
    for key in ('owned', 'isolated', 'approved', 'stop_active'):
        flag(d[key])
    number(d['start_minute'], 0, 1439)
    number(d['end_minute'], 1, 1440)
    require(d['start_minute'] < d['end_minute'], 'empty or reversed window')
    words(d['targets']); words(d['allowed'])
    for target in d['targets']:
        hostname(target)
    require(set(d['allowed']) <= {'read-config', 'read-log'}, 'unsupported training activity')
    decisions, observations = {}, []
    for row in rows(d, 'requests'):
        fields(row, 'id target activity minute')
        hostname(row['target']); text(row['activity']); number(row['minute'], 0, 1439)
        if d['stop_active']:
            verdict = 'stop-and-contact-owner'
        elif not all(d[k] for k in ('owned', 'isolated', 'approved')):
            verdict = 'do-not-start-plan-incomplete'
        elif row['target'] not in d['targets']:
            verdict = 'outside-target-scope'
        elif row['activity'] not in d['allowed']:
            verdict = 'outside-activity-scope'
        elif not d['start_minute'] <= row['minute'] < d['end_minute']:
            verdict = 'outside-time-window'
        else:
            verdict = 'within-written-plan-only'
        decisions[row['id']] = verdict
        observations.append(f"{row['id']}: {row['target']}, {row['activity']}, minute {row['minute']}; window [{d['start_minute']}, {d['end_minute']}).")
    return output(decisions, observations)

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
