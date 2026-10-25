"""Create a fresh redacted copy of a prepared synthetic record only."""
import argparse
import hashlib
from pathlib import Path
import sys
from lab import ROOT, LAB_ID, redact
from foundation_runtime import read_json, validate_case, safe_path, require, encoded

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def make_copy(relative):
    path=Path(relative)
    require(not path.is_absolute() and '..' not in path.parts,'use a relative run folder')
    folder=safe_path(ROOT/path); run=safe_path(ROOT/'run')
    require(run in folder.parents and folder.is_dir(),'use a prepared folder below run/')
    case=validate_case(read_json(folder/'case.json'),LAB_ID)
    excerpt=redact(case).encode('utf-8')
    source=safe_path(folder/'record.txt'); target=safe_path(folder/'excerpt.txt')
    receipt_path=safe_path(folder/'redaction-receipt.json')
    require(source.is_file() and source.stat().st_size<=100000,'bounded original is required')
    original=source.read_bytes()
    require(original==case['artifacts']['record.txt'].encode('utf-8'),'original differs from supplied synthetic artifact')
    require(not target.exists() and not receipt_path.exists(),'outputs already exist; use a fresh attempt')
    before=digest(original)
    with target.open('xb') as stream:
        stream.write(excerpt)
    after=digest(source.read_bytes())
    require(before==after,'original changed; stop and preserve both files')
    require(target.read_bytes()==excerpt,'copy readback differs')
    receipt={'original':'record.txt','copy':'excerpt.txt','case_id':case['case_id'],
             'original_before_sha256':before,'original_after_sha256':after,
             'copy_sha256':digest(excerpt),'seeded_values_absent':True,
             'listed_claims_present':True,'human_privacy_review':'not performed',
             'mapping':'case.json remove list indexes map to [REMOVED-N]'}
    with receipt_path.open('xb') as stream:
        stream.write(encoded(receipt))
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',required=True)
    args=parser.parse_args()
    try:
        print(encoded(make_copy(args.run)).decode(),end='')
    except (ValueError,OSError,TypeError,KeyError) as error:
        print(f'Input error: {error}',file=sys.stderr)
        sys.exit(2)
