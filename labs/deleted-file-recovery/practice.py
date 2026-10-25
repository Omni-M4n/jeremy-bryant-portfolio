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

PAYLOAD=b'Library practice: blue notebook, shelf 4.\n'
SECTOR=512
TOTAL_SECTORS=64
ROOT_OFFSET=3*SECTOR
DATA_OFFSET=4*SECTOR

def build_image(scenario):
    require(scenario in {'guided','changed','challenge'},'unsupported image scenario')
    image=bytearray(SECTOR*TOTAL_SECTORS)
    image[:3]=b'\xeb\x3c\x90'; image[3:11]=b'LABFAT12'
    struct.pack_into('<HBHBHHBHHHII',image,11,512,1,1,2,16,64,0xf8,1,1,1,0,0)
    image[36:39]=b'\x80\x00\x29'; struct.pack_into('<I',image,39,0x12345678)
    image[43:54]=b'TRAINING   '; image[54:62]=b'FAT12   '; image[510:512]=b'\x55\xaa'
    # construct an allocated file, then model deletion only in this bytearray
    for offset in (SECTOR,2*SECTOR):
        image[offset:offset+3]=b'\xf8\xff\xff'
        image[offset+3:offset+5]=b'\xff\x0f'  # cluster 2 end-of-chain
    image[ROOT_OFFSET:ROOT_OFFSET+11]=b'ITEM01  TXT'
    image[ROOT_OFFSET+11]=0x20
    struct.pack_into('<H',image,ROOT_OFFSET+26,2)
    struct.pack_into('<I',image,ROOT_OFFSET+28,len(PAYLOAD))
    image[DATA_OFFSET:DATA_OFFSET+len(PAYLOAD)]=PAYLOAD
    image[ROOT_OFFSET]=0xe5
    for offset in (SECTOR,2*SECTOR): image[offset+3:offset+5]=b'\x00\x00'
    if scenario=='changed': image[DATA_OFFSET:DATA_OFFSET+len(PAYLOAD)]=b'X'*len(PAYLOAD)
    if scenario=='challenge': image[ROOT_OFFSET:ROOT_OFFSET+32]=bytes(32)
    return bytes(image)

def read_deleted(image):
    require(len(image)==SECTOR*TOTAL_SECTORS,'only the 32 KiB training image is supported')
    require(image[3:11]==b'LABFAT12' and image[510:512]==b'\x55\xaa','unrecognized training boot record')
    require(struct.unpack_from('<HBHBHHBHHHII',image,11)==(512,1,1,2,16,64,0xf8,1,1,1,0,0),'unsupported FAT12 geometry')
    require(image[SECTOR:2*SECTOR]==image[2*SECTOR:3*SECTOR],'FAT copies disagree')
    row={'id':'item-01','directory_present':False,'cluster_allocated':False,'declared_size':0,'candidate_hex':'','known_sha256':sha_bytes(PAYLOAD)}
    entry=image[ROOT_OFFSET:ROOT_OFFSET+32]
    if entry[0]==0: return row
    require(entry[0]==0xe5 and entry[11]==0x20,'only a deleted ordinary training entry is supported')
    cluster=struct.unpack_from('<H',entry,26)[0]
    length=struct.unpack_from('<I',entry,28)[0]
    require(cluster==2 and 1<=length<=4096,'entry lies outside training allocation bounds')
    fat_value=struct.unpack_from('<H',image,SECTOR+3)[0]&0xfff
    row.update(directory_present=True,cluster_allocated=fat_value!=0,declared_size=length)
    if not fat_value and length<=SECTOR:
        row['candidate_hex']=image[DATA_OFFSET:DATA_OFFSET+length].hex()
    return row

def perform(target, case):
    source=target/'source'/'item-01.img'
    write_new(source,build_image(case['case_id'])); original=freeze(source)
    working=target/'output'/'item-01.img'; shutil.copyfile(source,working); working.chmod(stat.S_IREAD)
    row=read_deleted(read_bytes(working))
    if row['candidate_hex']:
        write_new(target/'output'/'item-01.bin',bytes.fromhex(row['candidate_hex']))
    save(target/'output'/'recovery-log.json',row)
    return {'operation':'read-only FAT12 image parsing and separate candidate extraction', 'image_sha256':original,
            'entry':row,'source_integrity':custody(target,{source:original}),
            'comparison':analyse({'data':{'entries':[row]}}),
            'generated_layout':{'sector_bytes':512,'sectors':64,'root_offset':ROOT_OFFSET,'data_offset':DATA_OFFSET},
            'mounted_or_device_accessed':False}

if __name__ == '__main__':
    raise SystemExit(main())
