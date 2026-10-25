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

def read_database(path):
    read_bytes(path)  # enforce local ordinary-file size/link rules before SQLite opens it
    connection=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        connection.execute('PRAGMA query_only = ON')
        rows=[]
        for table,kind in (('history','history'),('downloads','download'),('cache','cache')):
            for values in connection.execute('SELECT id,time,url,session,state,received,expected FROM '+table+' ORDER BY id'):
                row=dict(zip(('id','time','url','session','state','received','expected'),values)); row['kind']=kind
                rows.append(row)
        return sorted(rows,key=lambda row:(row['time'],row['id']))
    finally: connection.close()

def perform(target, case):
    source=target/'source'/'item-01.db'
    connection=sqlite3.connect(source)
    try:
        for table in ('history','downloads','cache'):
            connection.execute('CREATE TABLE '+table+' (id TEXT PRIMARY KEY, time TEXT NOT NULL, url TEXT NOT NULL, session TEXT NOT NULL, state TEXT NOT NULL, received INTEGER NOT NULL, expected INTEGER NOT NULL)')
        for row in case['data']['events']:
            table={'history':'history','download':'downloads','cache':'cache'}[row['kind']]
            connection.execute('INSERT INTO '+table+' VALUES (?,?,?,?,?,?,?)',tuple(row[key] for key in ('id','time','url','session','state','received','expected')))
        connection.commit()
    finally: connection.close()
    original=freeze(source)
    copy=target/'output'/'item-01.db'; shutil.copyfile(source,copy); copy.chmod(stat.S_IREAD)
    copy_before=sha_bytes(read_bytes(copy)); rows=read_database(copy)
    save(target/'output'/'timeline.json',rows)
    return {'operation':'read-only queries of a copied fictional browser-artifact database','events':rows,
            'copy_unchanged':copy_before==sha_bytes(read_bytes(copy)), 'source_integrity':custody(target,{source:original}),
            'schema':'custom training tables, UTC strings; not a real browser schema',
            'comparison':analyse({'data':{'events':rows}})}

if __name__ == '__main__':
    raise SystemExit(main())
