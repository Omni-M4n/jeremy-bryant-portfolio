"""Local synthetic exercise. No external input paths, network or device access."""
import argparse
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import struct
import sys
import time
import zlib
from lab import ROOT, LAB_ID, analyse
from foundation_runtime import read_json, safe_path, encoded, require, analyse_checked

def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()

def read_bytes(path):
    path = safe_path(path)
    require(path.is_file() and path.stat().st_nlink == 1 and path.stat().st_size <= 2_000_000, 'use a small ordinary unlinked training file')
    return path.read_bytes()

def write_new(path, content):
    safe_path(path)
    with path.open('xb') as stream:
        stream.write(content)

def save(path, value):
    write_new(path, encoded(value))

def freeze(path):
    before = sha_bytes(read_bytes(path))
    path.chmod(stat.S_IREAD)
    return before

def custody(target, originals):
    return [{'path':path.relative_to(target).as_posix(), 'before_sha256':before,
             'after_sha256':sha_bytes(read_bytes(path)),
             'unchanged':before == sha_bytes(read_bytes(path))}
            for path,before in originals.items()]

def fresh_target(output):
    require(isinstance(output, str) and re.fullmatch(r'run/[a-z0-9][a-z0-9-]{0,47}', output), 'use run/a-new-short-name')
    reserved={'con','prn','aux','nul'} | {f'{prefix}{number}' for prefix in ('com','lpt') for number in range(1,10)}
    require(output.split('/')[1] not in reserved, 'reserved output name')
    target = safe_path(ROOT / output)
    require(safe_path(ROOT / 'run') in target.parents and not target.exists(), 'output must be fresh below run/')
    target.parent.mkdir(exist_ok=True)
    target.mkdir()
    (target/'source').mkdir(); (target/'output').mkdir()
    return target

def run(scenario, output):
    require(scenario in {'guided','changed','challenge'}, 'unsupported scenario')
    case = read_json(ROOT/'fixtures'/f'{scenario}.json')
    analyse_checked(case, LAB_ID, analyse)
    target = fresh_target(output)
    started = datetime.now(timezone.utc).isoformat()
    receipt = perform(target, case)
    receipt.update({'lab_id':LAB_ID, 'scenario':scenario, 'started_utc':started,
                    'ended_utc':datetime.now(timezone.utc).isoformat(),
                    'synthetic':True, 'learner_mastery':'not assessed'})
    save(target/'receipt.json', receipt)
    return {'saved':output+'/receipt.json', 'source_bytes_unchanged':all(row['unchanged'] for row in receipt['source_integrity']), 'operation':receipt['operation']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('run')
    p.add_argument('--scenario',choices=('guided','changed','challenge'),default='guided')
    p.add_argument('--out',default='run/practical-01')
    args=parser.parse_args()
    try:
        print(encoded(run(args.scenario,args.out)).decode(),end='')
        return 0
    except (ValueError,OSError,sqlite3.Error,struct.error) as error:
        print('Practice input error: '+str(error),file=sys.stderr)
        return 2

def inventory(folder):
    values=[]
    for path in sorted(folder.iterdir()):
        raw=read_bytes(path)
        values.append({'name':path.name,'size':len(raw),'sha256':sha_bytes(raw)})
    return values

def perform(target, case):
    current=target/'output'/'current'; backup=target/'source'/'backup'; restored=target/'output'/'restored'
    current.mkdir(); backup.mkdir(); restored.mkdir()
    for number,raw in enumerate((b'alpha\n',b'bravo\n'),1): write_new(current/f'item-{number:02d}.txt',raw)
    baseline=inventory(current); originals={}
    for path in sorted(current.iterdir()):
        if case['case_id']=='changed' and path.name=='item-02.txt': continue
        destination=backup/path.name; shutil.copyfile(path,destination); originals[destination]=freeze(destination)
    # change only the disposable current folder after taking the backup
    (current/'item-01.txt').write_bytes(b'newer school notes\n')
    current_after=inventory(current)
    start=time.perf_counter_ns()
    for path in sorted(backup.iterdir()): shutil.copyfile(path,restored/path.name)
    copy_elapsed_ns=time.perf_counter_ns()-start
    if case['case_id']=='challenge': write_new(restored/'item-03.txt',b'alpha\n')
    verify_start=time.perf_counter_ns()
    found=inventory(restored); backup_inventory=inventory(backup)
    verification_elapsed_ns=time.perf_counter_ns()-verify_start
    expected={row['name']:row for row in baseline}; actual={row['name']:row for row in found}
    file_checks={name:('missing' if name not in actual else 'matches-baseline' if actual[name]==row else 'differs') for name,row in expected.items()}
    summary={'baseline':baseline,'current_after_change':current_after,'backup':backup_inventory,'restored':found,
             'file_checks':file_checks,'extra_files':sorted(actual.keys()-expected.keys()),
             'copy_elapsed_ns':copy_elapsed_ns,'verification_elapsed_ns':verification_elapsed_ns,
             'measurement':'copy loop only; validation measured separately; excludes planning and application recovery',
             'backup_age':'simulated in worksheet, not measured by waiting in this practical'}
    save(target/'output'/'restore-log.json',summary)
    return {'operation':'real dummy-data backup, controlled change and separate restore',**summary,'source_integrity':custody(target,originals)}

if __name__ == '__main__':
    raise SystemExit(main())
