"""A small offline case model. Read README.md before running."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'risk-register'
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

from datetime import date
LIMIT = 'The scores are a teaching scale, not measured probabilities. Proposed controls do not prove a lower real risk.'

def calendar_date(value):
    text(value)
    require(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value) is not None, 'expected YYYY-MM-DD')
    return date.fromisoformat(value)

def analyse(case):
    d=case['data']; fields(d,'as_of risks')
    today=calendar_date(d['as_of'])
    decisions, observations={},[]
    for r in rows(d,'risks'):
        fields(r,'id scenario likelihood impact treatment owner review likelihood_after impact_after control_verified acceptance controls assumption')
        for k in ('scenario','owner','review','assumption'): text(r[k])
        for k in ('likelihood','impact','likelihood_after','impact_after'): number(r[k],1,3)
        choice(r['treatment'],'reduce avoid transfer accept')
        flag(r['control_verified']); flag(r['acceptance']); words(r['controls'])
        require(r['likelihood_after'] <= r['likelihood'] and r['impact_after'] <= r['impact'], 'this model only supports unchanged or reduced projections')
        if r['treatment']=='accept':
            require(r['likelihood_after']==r['likelihood'] and r['impact_after']==r['impact'], 'accept does not itself reduce risk')
        score=r['likelihood']*r['impact']; after=r['likelihood_after']*r['impact_after']
        band='high' if score>=6 else 'medium' if score>=3 else 'low'
        status='review-due' if calendar_date(r['review'])<=today else 'review-planned'
        if r['treatment']=='accept' and not r['acceptance']: status='owner-acceptance-needed'
        residual='supported-in-case' if r['control_verified'] else 'projection-only'
        decisions[r['id']]=f'{band};{r["treatment"]};{status};{residual}'
        observations.append(f"{r['id']}: {r['likelihood']} x {r['impact']} = {score}; proposed residual {r['likelihood_after']} x {r['impact_after']} = {after}; owner {r['owner']}.")
    return output(decisions,observations)

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
