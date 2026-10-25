"""A small offline case model. Read README.md before running."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'small-threat-model'
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

LIMIT = 'Configuration is a claim. Supplied observations cover one fictional path only; no radio or network test is run.'
def analyse(case):
    d=case['data']; fields(d, 'wifi_access paths')
    choice(d['wifi_access'], 'shared-password named-users')
    decisions, observations={}, []
    for r in rows(d,'paths'):
        fields(r,'id source destination configured observed identity resource_check transport')
        choice(r['source'],'staff-wifi guest-wifi device-segment')
        require(r['destination']=='records-service.test','unsupported destination')
        choice(r['configured'],'allow block'); choice(r['observed'],'unrun reachable blocked')
        choice(r['identity'],'named shared none'); flag(r['resource_check']); choice(r['transport'],'tls plain')
        if r['configured']=='block':
            network='configured-only' if r['observed']=='unrun' else 'path-block-observed' if r['observed']=='blocked' else 'configuration-observation-conflict'
        else:
            network='path-needs-check' if r['observed']=='unrun' else 'path-reachable' if r['observed']=='reachable' else 'unexpected-block'
        layers=[]
        if r['identity']!='named': layers.append('named-identity')
        if not r['resource_check']: layers.append('resource-permission')
        if r['transport']!='tls': layers.append('transport-protection')
        decisions[r['id']]=network+';'+('review-'+','.join(layers) if layers else 'listed-service-checks-present')
        observations.append(f"{r['id']}: {r['source']} -> {r['destination']}; network {r['configured']}/{r['observed']}; Wi-Fi access {d['wifi_access']}.")
    return output(decisions,observations)

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
