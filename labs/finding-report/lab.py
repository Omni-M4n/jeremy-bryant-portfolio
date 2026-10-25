"""A small offline case model. Read README.md before running."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'finding-report'
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

LIMIT = 'The transcript is authored training data. No live test ran, and one retest does not establish security for every route.'
def analyse(case):
    d=case['data']; fields(d,'expected_unauthorised expected_owner attempts')
    number(d['expected_unauthorised'],100,599); number(d['expected_owner'],100,599)
    require(d['expected_unauthorised']==403 and d['expected_owner']==200,'this lesson uses 403 and 200 only')
    decisions, observations={},[]
    for r in rows(d,'attempts'):
        fields(r,'id original_code original_other_record fix_claimed retest_code retest_other_record owner_code same_route evidence_ref')
        for k in ('original_code','retest_code','owner_code'):
            if r[k] is not None: number(r[k],100,599)
        for k in ('original_other_record','fix_claimed','retest_other_record','same_route'): flag(r[k])
        text(r['evidence_ref'])
        require(not r['original_other_record'] or r['original_code']==200,'record body contradicts original status in this model')
        require(not r['retest_other_record'] or r['retest_code']==200,'record body contradicts retest status in this model')
        original=r['original_other_record']
        if not original: verdict='original-claim-not-supported'
        elif not r['same_route']: verdict='retest-not-comparable'
        elif r['retest_code'] is None: verdict='retest-missing'
        elif r['retest_code']!=403 or r['retest_other_record']: verdict='correction-not-demonstrated'
        elif r['owner_code'] is None: verdict='legitimate-use-retest-missing'
        elif r['owner_code']!=200: verdict='access-blocked-but-owner-regressed'
        else: verdict='bounded-correction-supported'
        decisions[r['id']]=verdict
        observations.append(f"{r['id']}: original {r['original_code']}, retest {r['retest_code']}, owner {r['owner_code']}; evidence {r['evidence_ref']}.")
    return output(decisions,observations)

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
