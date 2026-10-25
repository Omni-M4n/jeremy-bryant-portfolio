"""A small offline case model. Read README.md before running."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require
LAB_ID = 'portfolio-mastery-capstone'
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

LIMIT = 'The helper checks bounded supplied facts only. A fresh case, human review and later recall are needed; mastery is not assessed.'
def analyse(case):
    d=case['data']; fields(d,'observations')
    decisions, evidence={},[]
    for r in rows(d,'observations'):
        fields(r,'id track claim facts')
        choice(r['track'],'dns identity access retest')
        text(r['claim'])
        f=r['facts']; state='incomplete'
        if r['track']=='dns':
            fields(f,'answer http_status'); flag(f['answer'])
            if f['http_status'] is not None: number(f['http_status'],100,599)
            choice(r['claim'],'name-resolved page-works')
            if r['claim']=='name-resolved': state='supported' if f['answer'] else 'contradicted'
            elif f['http_status'] is not None: state='supported' if f['http_status']==200 else 'contradicted'
        elif r['track']=='identity':
            fields(f,'failed_count later_success user_reports_typo')
            number(f['failed_count'],0,100); flag(f['later_success']); flag(f['user_reports_typo'])
            require(r['claim']=='intrusion-confirmed','unsupported identity claim')
            # A failure count and a later success cannot establish who typed.
            state='incomplete'
        elif r['track']=='access':
            fields(f,'current_roles checked_accounts total_accounts')
            words(f['current_roles'],empty=True); number(f['checked_accounts'],0,20); number(f['total_accounts'],1,20)
            require(f['checked_accounts']<=f['total_accounts'],'checked exceeds total')
            choice(r['claim'],'editor-role-absent all-permissions-correct')
            if r['claim']=='editor-role-absent': state='contradicted' if 'editor' in f['current_roles'] else 'supported'
            # A row count alone cannot prove that every permission is correct.
        else:
            fields(f,'nonowner_code owner_code same_route'); flag(f['same_route'])
            require(r['claim']=='correction-demonstrated','unsupported retest claim')
            for k in ('nonowner_code','owner_code'):
                if f[k] is not None: number(f[k],100,599)
            if f['same_route'] and f['nonowner_code'] is not None and f['owner_code'] is not None:
                state='supported' if f['nonowner_code']==403 and f['owner_code']==200 else 'contradicted'
        decisions[r['id']]={'supported':'supported-within-case','contradicted':'revise-claim','incomplete':'collect-bounded-evidence'}[state]
        evidence.append(f"{r['id']}: {r['track']}; evidence {state}.")
    require(2<=len({r['track'] for r in d['observations']})<=3,'combine two or three tracks')
    return output(decisions,evidence)

if __name__ == '__main__':
    sys.exit(main(ROOT, LAB_ID, analyse))
