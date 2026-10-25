from pathlib import Path
import argparse
import json
import sys
import lab
from foundation_runtime import safe_path, read_json, encoded, require

def fresh_folder(value):
    relative = Path(value)
    require(not relative.is_absolute() and ".." not in relative.parts, "use a relative path below run/")
    target = safe_path(lab.ROOT / relative)
    require(safe_path(lab.ROOT / "run") in target.parents and not target.exists(), "use a fresh folder below run/")
    target.mkdir(parents=True, exist_ok=False)
    return target

def run_input(value):
    path = safe_path(value)
    require(safe_path(lab.ROOT / "run") in path.parents and path.is_file(), "use a regular input below this lab run/")
    require(path.stat().st_size <= 1000000, "input exceeds 1 MB")
    return path

def process(source,start,end,output):
    path=run_input(source)
    raw=path.read_text(encoding="utf-8")
    states,counts,rejected=lab.count_lines(raw,start,end)
    target=fresh_folder(output)
    result=dict(start=start,end=end,decisions=states,counts=counts,rejected=rejected)
    (target/"report.json").write_bytes(encoded(result))
    (target/"source.jsonl").write_bytes(path.read_bytes())
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Count the prepared synthetic JSON-lines file.")
    for key in ("source","start","end","out"): p.add_argument("--"+key,required=True)
    a=p.parse_args()
    try: print(json.dumps(process(a.source,a.start,a.end,a.out),indent=2))
    except (ValueError,OSError) as error:
        print(f"Input error: {error}",file=sys.stderr); raise SystemExit(2)
