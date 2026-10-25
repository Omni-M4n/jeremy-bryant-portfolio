"""A small offline case model. Read README.md before running."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'incident-communications'
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

LIMIT = 'These are drafts about fictional facts. No message is sent and no real incident, breach or person is assessed.'
def analyse(case):
    d=case['data']; fields(d,'now_minute next_update_minute reporting_route statements')
    number(d['now_minute'],0,1439); number(d['next_update_minute'],0,1439)
    require(d['next_update_minute']>d['now_minute'],'next update must be later on this fictional day')
    require(d['reporting_route']=='service-desk.test','use the supplied trusted fictional route')
    decisions, observations={},[]
    for r in rows(d,'statements'):
        fields(r,'id text status source audience owner')
        text(r['text']); text(r['source']); text(r['owner'])
        choice(r['status'],'confirmed hypothesis unknown action')
        choice(r['audience'],'staff technical manager')
        if r['status']=='action': verdict='assign-action-and-owner'
        elif r['status']=='unknown': verdict='state-unknown-and-next-check'
        elif r['status']=='hypothesis': verdict='label-hypothesis-do-not-present-as-fact'
        else: verdict='use-confirmed-fact-for-'+r['audience']
        decisions[r['id']]=verdict
        observations.append(f"{r['id']}: {r['status']}; source {r['source']}; owner {r['owner']}; next update minute {d['next_update_minute']}.")
    return output(decisions,observations)

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
