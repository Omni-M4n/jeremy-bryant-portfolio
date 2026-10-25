"""A small offline case model. Read README.md before running."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'data-classification'
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

LIMIT = 'These are invented handling rules, not legal advice or proof of real deletion.'
def analyse(case):
    d = case['data']; fields(d, 'records')
    decisions, observations = {}, []
    for r in rows(d, 'records'):
        fields(r, 'id purpose personal secret public fields needed age_days retain_days hold recipient allowed_receivers disposal')
        text(r['purpose']); text(r['recipient'])
        for k in ('personal', 'secret', 'public', 'hold'): flag(r[k])
        require(not (r['public'] and (r['personal'] or r['secret'])), 'public approval conflicts with sensitive content')
        words(r['fields']); words(r['needed']); words(r['allowed_receivers'])
        require(set(r['needed']) <= set(r['fields']), 'needed field missing')
        number(r['age_days']); number(r['retain_days'], 1)
        choice(r['disposal'], 'none primary-only all-listed-copies')
        require(r['disposal'] == 'none' or (not r['hold'] and r['age_days'] >= r['retain_days']), 'disposal conflicts with retention or hold')
        level = 'restricted' if r['secret'] else 'confidential' if r['personal'] else 'public' if r['public'] else 'internal'
        lifecycle = 'retain-on-hold' if r['hold'] else 'disposal-due' if r['age_days'] >= r['retain_days'] else 'retain-until-review'
        share = 'share-as-approved' if r['recipient'] in r['allowed_receivers'] else 'do-not-share'
        extra = sorted(set(r['fields']) - set(r['needed']))
        receipt = 'no-receipt' if r['disposal'] == 'none' else 'receipt-incomplete' if r['disposal'] == 'primary-only' else 'receipt-covers-listed-copies'
        decisions[r['id']] = f'{level};{lifecycle};{share};{receipt}'
        observations.append(f"{r['id']}: age {r['age_days']} / retain {r['retain_days']} days; unnecessary fields: {', '.join(extra) if extra else 'none'}.")
    return output(decisions, observations)

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
