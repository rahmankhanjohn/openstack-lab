#!/usr/bin/env python3
"""lab-status: check what is actually running in an OpenStack lab.

Runs the openstack CLI and prints what is up, what is missing and what to
fix next. Reads only, changes nothing.

Usage:
  lab-status.py
  lab-status.py --json
"""

import argparse
import json
import shutil
import subprocess
import sys

CHECKS = [
    ('identity', 'openstack token issue', 'auth as admin'),
    ('services', 'openstack service list', 'keystone and the rest are registered'),
    ('images', 'openstack image list', 'at least one image to boot'),
    ('flavors', 'openstack flavor list', 'flavors to launch with'),
    ('networks', 'openstack network list', 'a network for the port'),
    ('volumes', 'openstack volume service list', 'block storage is alive'),
    ('instances', 'openstack server list', 'any running instance'),
]


def run(command):
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None, 'command not available'
    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or '').strip().splitlines()
        return None, message[-1] if message else 'command failed'
    return proc.stdout.strip(), None


def count_rows(text):
    return len([line for line in text.splitlines() if line.strip()])


def check_all():
    results = []
    for key, command, purpose in CHECKS:
        output, error = run(command.split())
        if error:
            results.append({'key': key, 'command': command, 'state': 'FAIL',
                            'detail': error, 'purpose': purpose})
            continue
        rows = count_rows(output)
        state = 'OK' if rows > 0 else 'EMPTY'
        results.append({'key': key, 'command': command, 'state': state,
                        'detail': '%d rows' % rows, 'purpose': purpose})
    return results


def render(results):
    lines = []
    lines.append('OpenStack lab status')
    lines.append('=' * 68)
    for result in results:
        mark = {'OK': 'ok  ', 'EMPTY': 'thin', 'FAIL': 'fail'}[result['state']]
        lines.append('  %s %-11s %-28s %s' % (mark, result['key'], result['detail'], result['purpose']))
    lines.append('')
    fails = [r for r in results if r['state'] == 'FAIL']
    empties = [r for r in results if r['state'] == 'EMPTY']
    if fails:
        lines.append('  Fix first: %s' % ', '.join(r['key'] for r in fails))
        lines.append('  Common cause: keystone not reached, or the service account env vars are not set.')
    elif empties:
        lines.append('  Running but thin: %s' % ', '.join(r['key'] for r in empties))
        lines.append('  That is normal on day one. Create the missing object and check again.')
    else:
        lines.append('  Lab looks healthy. Try breaking it on purpose, that is the point of a lab.')
    return '\n'.join(lines)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Check what is running in an OpenStack lab.')
    parser.add_argument('--json', action='store_true', help='machine-readable output')
    args = parser.parse_args(argv)

    if shutil.which('openstack') is None:
        message = ('the openstack CLI is not on PATH. Install the python3-openstackclient '
                   'package, or source the devstack openrc file first.')
        if args.json:
            print(json.dumps({'error': message}, indent=2))
        else:
            print('OpenStack lab status')
            print('=' * 68)
            print('  fail  cli          %s' % message)
        return 2

    results = check_all()
    if args.json:
        print(json.dumps({'results': results}, indent=2))
    else:
        print(render(results))
    return 1 if any(r['state'] == 'FAIL' for r in results) else 0


if __name__ == '__main__':
    sys.exit(main())
