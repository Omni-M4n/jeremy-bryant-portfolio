"""View tune rows first, save a choice, then reveal the held-aside rows."""
import argparse
import hashlib
import json
import sys
import lab
from foundation_runtime import encoded, read_json, require, safe_path


def case_input(value):
    path = safe_path(value)
    require(safe_path(lab.ROOT / 'run') in path.parents,
            'use a prepared case below this lab run/')
    case = read_json(path)
    lab.analyse(case)  # Validate all input without printing its results.
    return path, case, hashlib.sha256(path.read_bytes()).hexdigest()


def choice_path(path):
    return safe_path(path.parent / 'choice.json')


def choose(value, threshold, reason):
    path, case, digest = case_input(value)
    require(type(threshold) is int and threshold in case['data']['thresholds'],
            'choose one of the two supplied thresholds')
    require(isinstance(reason, str) and 1 <= len(reason.strip()) <= 500,
            'give a short reason based only on the tune rows')
    choice = dict(case_sha256=digest, threshold=threshold, reason=reason.strip())
    # Exclusive creation keeps the first choice. Corrections belong in notes.
    with choice_path(path).open('xb') as output:
        output.write(encoded(choice))
    return {'saved': 'choice.json', 'threshold': threshold,
            'next': 'View holdout rows and keep this threshold fixed.'}


def view(value, partition):
    require(partition in ('tune', 'holdout'), 'choose tune or holdout')
    path, case, digest = case_input(value)
    output = {'partition': partition}
    if partition == 'holdout':
        choice = read_json(choice_path(path))
        lab.exact(choice, ['case_sha256', 'threshold', 'reason'])
        require(choice['case_sha256'] == digest, 'case changed after the choice')
        require(type(choice['threshold']) is int and
                choice['threshold'] in case['data']['thresholds'], 'invalid saved threshold')
        require(isinstance(choice['reason'], str) and
                1 <= len(choice['reason'].strip()) <= 500, 'saved choice needs a reason')
        output['chosen_threshold'] = choice['threshold']
    else:
        output['thresholds'] = case['data']['thresholds']
    output['events'] = [row for row in case['data']['events']
                        if row['partition'] == partition]
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('tune', 'holdout', 'choose'):
        command = sub.add_parser(name)
        command.add_argument('--case', required=True)
        if name == 'choose':
            command.add_argument('--threshold', type=int, required=True)
            command.add_argument('--reason', required=True)
    args = parser.parse_args()
    try:
        result = (choose(args.case, args.threshold, args.reason)
                  if args.command == 'choose' else view(args.case, args.command))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError) as error:
        print(f'Input error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
