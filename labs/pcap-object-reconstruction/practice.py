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

BODY=b'alpha\n'
HTTP=b'HTTP/1.1 200 OK\r\nContent-Length: 6\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n'
SOURCE=b'\xc0\x00\x02\x0a'
DESTINATION=b'\xc0\x00\x02\x14'

def checksum(raw):
    raw+=b'\x00' if len(raw)%2 else b''
    total=sum(struct.unpack('>'+str(len(raw)//2)+'H',raw))
    while total>>16: total=(total&0xffff)+(total>>16)
    return (~total)&0xffff

def frame(sequence,payload):
    tcp=struct.pack('>HHIIBBHHH',80,40000,sequence,1,0x50,0x18,8192,0,0)
    pseudo=SOURCE+DESTINATION+struct.pack('>BBH',0,6,len(tcp)+len(payload))
    tcp=tcp[:16]+struct.pack('>H',checksum(pseudo+tcp+payload))+tcp[18:]
    ip=struct.pack('>BBHHHBBH4s4s',0x45,0,40+len(payload),1,0,64,6,0,SOURCE,DESTINATION)
    ip=ip[:10]+struct.pack('>H',checksum(ip))+ip[12:]
    ethernet=b'\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x01\x08\x00'
    return (ethernet+ip+tcp+payload).ljust(60,b'\x00')

def make_pcap(data):
    payloads=[(1000,HTTP)] + [(1000+len(HTTP)+row['offset'],bytes.fromhex(row['bytes_hex'])) for row in data['segments']]
    content=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1)
    for index,(sequence,payload) in enumerate(payloads):
        packet=frame(sequence,payload)
        content+=struct.pack('<IIII',1735689600,index*1000,len(packet),len(packet))+packet
    return content

def extract(pcap):
    require(len(pcap)>=24,'short PCAP header')
    require(struct.unpack_from('<IHHIIII',pcap)==(0xa1b2c3d4,2,4,0,0,65535,1),'unsupported PCAP format')
    offset=24; packets=[]
    while offset<len(pcap):
        require(len(pcap)-offset>=16,'short packet record')
        sec,usec,included,original=struct.unpack_from('<IIII',pcap,offset); offset+=16
        require(usec<1000000 and included==original and 54<=included<=4096 and offset+included<=len(pcap),'truncated or unsupported packet length')
        packet=pcap[offset:offset+included]; offset+=included
        require(packet[12:14]==b'\x08\x00' and packet[14]==0x45,'only fixed IPv4 header is supported')
        ip=packet[14:34]
        ip_length=struct.unpack_from('>H',ip,2)[0]
        require(checksum(ip)==0 and 40<=ip_length<=len(packet)-14,'invalid IP checksum or length')
        require(len(packet)==max(60,14+ip_length) and not any(packet[14+ip_length:]),'invalid Ethernet padding')
        require(ip[9]==6 and ip[6:8]==b'\x00\x00' and ip[12:16]==SOURCE and ip[16:20]==DESTINATION,'unsupported IP flow or fragment')
        tcp=packet[34:54]; payload=packet[54:14+ip_length]
        require(tcp[:4]==struct.pack('>HH',80,40000) and tcp[12]==0x50 and tcp[13]==0x18,'unsupported TCP flow or options')
        pseudo=SOURCE+DESTINATION+struct.pack('>BBH',0,6,len(tcp)+len(payload))
        require(checksum(pseudo+tcp+payload)==0,'invalid TCP checksum')
        packets.append((struct.unpack_from('>I',tcp,4)[0],payload))
        require(len(packets)<=21,'too many training packets')
    require(packets and packets[0]==(1000,HTTP),'first packet must hold the exact training response header')
    rows=[]
    for index,(sequence,payload) in enumerate(packets[1:],1):
        rows.append({'id':f'item-{index:02d}','offset':sequence-1000-len(HTTP),'bytes_hex':payload.hex()})
    data={'content_length':6,'known_sha256':sha_bytes(BODY),'encrypted':False,'segments':rows}
    analyse({'data':data})
    return data

def contiguous_prefix(data):
    positions,conflicts={},set()
    for row in data['segments']:
        for index,byte in enumerate(bytes.fromhex(row['bytes_hex']),row['offset']):
            if index in positions and positions[index]!=byte: conflicts.add(index)
            positions[index]=byte
    output=bytearray()
    for index in range(data['content_length']):
        if index not in positions or index in conflicts: break
        output.append(positions[index])
    return bytes(output)

def perform(target, case):
    source=target/'source'/'item-01.pcap'
    write_new(source,make_pcap(case['data'])); original=freeze(source)
    copy=target/'output'/'item-01.pcap'; shutil.copyfile(source,copy); copy.chmod(stat.S_IREAD)
    data=extract(read_bytes(copy)); prefix=contiguous_prefix(data)
    write_new(target/'output'/'item-01.bin',prefix)
    report=analyse({'data':data})
    # Keep this first evidence view separate from the reference interpretation.
    save(target/'output'/'packet-log.json',{'parsed_body_segments':data,'exported_bytes':len(prefix),'exported_sha256':sha_bytes(prefix)})
    save(target/'output'/'feedback.json',report)
    return {'operation':'synthetic HTTP PCAP reconstruction','data':data,'result':report,
            'exported_bytes':len(prefix),'exported_sha256':sha_bytes(prefix),'source_integrity':custody(target,{source:original}),
            'live_capture_performed':False,'network_used':False,'wireshark_export_run':False}

if __name__ == '__main__':
    raise SystemExit(main())
