"""Rows behind the third version of the three-chairmen figure (nv13): the tables build_chairmen.py writes.
Each row cites the records it rests on and a passage the checker must find in each. Ids: CT (a record in a chairman's panel),
CK (a line of the who-is-who key), CS (a line on what is at stake), CE (a dated event on the timeline), CN (a computed number).
A tie is a dated record. It is not a statement of why anyone acted. Donors and lobbyists are counted, never named."""
import csv
from pathlib import Path
R = Path(__file__).resolve().parents[1] / 'research'
csv.field_size_limit(10**9)
TABLES = ('nv13_ties.csv', 'nv13_key.csv', 'nv13_stake.csv', 'nv13_events.csv', 'nv13_numbers.csv')


def table(name):
    p = R / name
    out = []
    for r in (csv.DictReader(open(p, newline='')) if p.exists() else []):
        r = dict(r)
        if 'src' in r:
            r['src'] = r['src'].split(' || '); r['q'] = r['q'].split(' || ')
        out.append(r)
    return out


def ties():
    return table('nv13_ties.csv')


def key():
    return table('nv13_key.csv')


def stake():
    return table('nv13_stake.csv')


def events():
    return table('nv13_events.csv')


def numbers():
    return {r['key']: r for r in table('nv13_numbers.csv')}


def glance():
    return table('nv13_glance.csv')


def quiet(cell):
    """A cell of the at-a-glance table that holds no record: a dash, $0, or "none found"."""
    return cell.startswith('–') or cell in ('$0', 'none found')


def lobbyist_gifts():
    return table('lobbyist_gifts.csv')


def rows():
    out = []
    for name in TABLES:
        for r in table(name):
            out.append({'row_id': r['row_id'], 'table': name, 'src': r['src'], 'q': r['q']})
    return out
