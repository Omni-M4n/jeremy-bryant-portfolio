"""Measure embedded fictional backup bytes without revealing analysis decisions.

Contract: python inspect_payloads.py --case run/attempt-01/case.json
Reads one bounded case through the shared reader; prints JSON to stdout only.
Exit 0 means measurements produced; 2 means invalid input or filesystem error.
No payload is executed or written to disk, and no comparison verdict is emitted.
"""
import argparse
from pathlib import Path
import sys

from lab import ROOT, measure_payloads
from foundation_runtime import encoded, read_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, default=ROOT / "fixtures" / "guided.json")
    args = parser.parse_args(argv)
    try:
        case = read_json(args.case)
        result = {"case_id": case["case_id"], "measurements": measure_payloads(case),
                  "scope": "Embedded fictional bytes decoded in memory only. Compare these measurements with the case manifest and recovery requirements yourself."}
        print(encoded(result).decode("utf-8"), end="")
        return 0
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
