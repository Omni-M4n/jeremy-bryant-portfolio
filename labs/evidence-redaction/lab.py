"""A small offline case model. Read README.md before running."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'evidence-redaction'
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

LIMIT = 'Exact seeded text replacement is not a general redaction detector. A person must review context, hidden data and the final copy.'
def redact(case):
    d=case['data']; fields(d,'remove keep')
    words(d['remove']); words(d['keep'])
    require('record.txt' in case['artifacts'],'record.txt is required')
    original=case['artifacts']['record.txt']
    require(original.startswith('SYNTHETIC TRAINING RECORD\n'),'only supplied synthetic text is supported')
    require(len(original.encode('utf-8'))<=100000,'text too large')
    require('[REMOVED-' not in original,'reserved replacement marker in input')
    for value in d['remove']+d['keep']:
        require(value in original,'listed text is absent')
    for sensitive in d['remove']:
        require(not any(sensitive in keep or keep in sensitive for keep in d['keep']),'keep and remove overlap')
        require(not any(sensitive in other for other in d['remove'] if other!=sensitive),'overlapping remove terms')
    excerpt=original
    for index,value in enumerate(d['remove'],1):
        excerpt=excerpt.replace(value,f'[REMOVED-{index}]')
    require(all(v not in excerpt for v in d['remove']),'a seeded value remains')
    require(all(v in excerpt for v in d['keep']),'a required claim was changed')
    return excerpt

def analyse(case):
    excerpt=redact(case); d=case['data']; original=case['artifacts']['record.txt']
    return output({'item-1':'seeded-values-removed','item-2':'listed-claims-preserved'},[
        f"Replacements: {sum(original.count(v) for v in d['remove'])}; distinct seeded values: {len(d['remove'])}.",
        f"Preserved claim fragments: {len(d['keep'])}; source and output differ: {excerpt != original}."])

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
