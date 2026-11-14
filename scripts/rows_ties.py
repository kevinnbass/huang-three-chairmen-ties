"""Rows behind the member-tie figures: nv13 (three chairmen, one panel each) and the map's third version.
The ties are built by build_member_ties.py into research/member_ties.csv; each tie cites the records it rests on (rows of the builder's evidence sets; FEC lines; the bill and lobbying tables in research/)
and a passage the checker must find in each. A tie is a dated record. It is not a statement of why anyone acted.
Employees who gave their own money are counted, never named."""
import csv, re
from pathlib import Path
R = Path(__file__).resolve().parents[1] / 'research'
csv.field_size_limit(10**9)
THREE = ['mast', 'moolenaar', 'crawford']
# dated public events drawn on the panels' time strips: member ('all' = each panel), date, words, source, passage
EVENTS = [
 ('moolenaar', '2025-06-25', 'Jack Clark testifies to his committee', 'pack:congress/research/travel.csv#TV2012', 'Algorithms and Authoritarians: Why U.S. AI Must Lead'),
 ('moolenaar', '2025-10-31', 'Introduces H.R. 5885', 'table:chip_bills.csv#hr5885', '2025-10-31'),
 ('crawford', '2025-11-18', 'Cosponsors H.R. 5885', 'table:chip_bill_backers.csv#hr5885:C001087', '2025-11-18'),
 ('mast', '2025-12-18', 'Introduces H.R. 6875', 'table:chip_bills.csv#hr6875', '2025-12-18'),
 ('moolenaar', '2025-12-18', 'Original cosponsor of H.R. 6875', 'table:chip_bill_backers.csv#hr6875:M001194', '2025-12-18'),
 ('crawford', '2025-12-18', 'Original cosponsor of H.R. 6875', 'table:chip_bill_backers.csv#hr6875:C001087', '2025-12-18'),
 ('mast', '2026-01-21', 'His committee approves it, 42–2', 'table:chip_bills.csv#hr6875', 'Ordered to be Reported in the Nature of a Substitute by the Yeas and Nays: 42 - 2.'),
 ('mast', '2026-07-17', 'Ads praising his record announced', 'art-pfa-conservative', 'Rep. Brian Mast'),
 ('moolenaar', '2026-07-17', 'Ads praising his record announced', 'art-pfa-conservative', 'Rep. John Moolenaar'),
 ('moolenaar', '2026-08-05', 'Public First Action ad naming him starts', 'google-political-ads-pfa-20260916', 'Ad_ID=CR04292619503667249153'),
 ('mast', '2026-08-19', 'Public First Action ad naming him starts', 'google-political-ads-pfa-20260916', 'Ad_ID=CR08230337604738875393'),
 ('all', '2026-10-29', 'First Times report', 'man-nyt-1029-01', 'American officials had concluded that she was a Chinese intelligence asset'),
 ('all', '2026-11-05', 'Three chairmen ask Huang to brief them', 'house-hfac-letter-pr', 'the Chairmen have requested that Mr. Huang brief the committees on November 18, 2026'),
 ('all', '2026-11-12', 'Second letter: interview or subpoena', 'x-chinaselect-letter', 'accept the request of our three committees or he will be subpoenaed'),
]
# what was looked for and not found, each a bounded search recorded in the congress pack (member, words, row, passage)
NOT_FOUND = [
 ('mast', 'A post from his official X account since Jan 2025 using any of eleven search terms, among them Anthropic, Open Philanthropy, Public First, Horizon Institute and Amodei (searched Sep 16, 2026)', 'pack:congress/research/member_statements.csv#MS1338', 'none found in from:RepBrianMast'),
 ('moolenaar', 'A post from his official X account since Jan 2025 using any of eleven search terms, among them Anthropic, Open Philanthropy, Public First, Horizon Institute and Amodei (searched Sep 16, 2026)', 'pack:congress/research/member_statements.csv#MS1432', 'none found in from:RepMoolenaar'),
 ('crawford', 'A post from his official X account since Jan 2025 using any of eleven search terms, among them Anthropic, Open Philanthropy, Public First, Horizon Institute and Amodei (searched Sep 16, 2026)', 'pack:congress/research/member_statements.csv#MS1264', 'none found in from:RepRickCrawford'),
]


def table(name):
    p = R / name
    return list(csv.DictReader(open(p, newline=''))) if p.exists() else []


def ties():
    out = []
    for t in table('member_ties.csv'):
        t = dict(t); t['src'] = t['src'].split(' || '); t['q'] = t['q'].split(' || '); out.append(t)
    return out


def gifts():
    return table('employee_gifts.csv')


def links():
    """The key of the three-chairmen figure: how each group named in the panels connects to Anthropic (one record per line)."""
    out = []
    for r in table('nv13_links.csv'):
        r = dict(r); r['src'] = r['src'].split(' || '); r['q'] = r['q'].split(' || '); out.append(r)
    return out


def members():
    """The three chairmen's header facts (name, role line, pages naming each), written by build_member_ties.py."""
    return {r['key']: r for r in table('nv13_members.csv')}


def rates():
    return {r['side']: r for r in table('employee_gift_rates.csv')}


def basis_words():
    """Where the employees' gift lines come from, counted from the gift table itself (one wording for both figures)."""
    g = gifts()
    api = {s: sum(1 for r in g if r['side'] == s and r['source'].startswith('fec-sched_a') and not r['note']) for s in ('anthropic', 'nvidia')}
    late = sum(1 for r in g if r['note'].startswith('a later filing'))
    early = [r for r in g if r['note'].startswith('employer given on an earlier capture')]
    assert all(r['side'] == 'anthropic' for r in early)
    out = ('Both companies\' lines come from the FEC\'s bulk file of itemised individual contributions for the 2026 cycle, downloaded Nov 13, 2026 (it carries whole dollars), '
           f'plus the lines its API holds and the file does not yet (nearly all dated Jul to Sep 2026): {api["anthropic"]} for Anthropic, {api["nvidia"]} for Nvidia.'
           + (f' For {late} more line{"s" if late != 1 else ""} the API\'s later filing replaces the file\'s copy.' if late else ''))
    if early:
        cm = sorted({re.sub(r'(?<=\w )(For|Of|The|And)\b', lambda m: m.group(1).lower(), r['committee'].title()) for r in early}); n = len(early)
        nw = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten'}.get(n, str(n))
        out += (f' {nw} Anthropic line{"s" if n != 1 else ""} to {cm[0] if len(cm) == 1 else str(len(cm)) + " committees"} {"are" if n != 1 else "is"} counted from a copy of the committee\'s report saved in Sep 2026: '
                'its amended report leaves the employer blank. No earlier copy exists for Nvidia, so a Nvidia line blanked that way is missed.')
    return out


def rows():
    out = []
    for i, t in enumerate(ties(), 1):
        out.append({'row_id': t.get('row_id') or f'TY{i:03d}', 'member': t['member'], 'type': t['type'], 'side': t['side'], 'src': t['src'], 'q': t['q']})
    for i, (m, d, w, s, q) in enumerate(EVENTS, 1):
        out.append({'row_id': f'TE{i:02d}', 'member': m, 'date': d, 'src': s, 'q': q})
    for i, (m, w, s, q) in enumerate(NOT_FOUND, 1):
        out.append({'row_id': f'TX{i:02d}', 'member': m, 'src': s, 'q': q})
    for i, k in enumerate(links(), 1):
        out.append({'row_id': f'TL{i:02d}', 'link': k['id'], 'src': k['src'], 'q': k['q']})
    for i, side in enumerate(sorted(rates()), 1):
        out.append({'row_id': f'TR{i:02d}', 'side': side, 'src': f'table:employee_gift_rates.csv#{side}', 'q': rates()[side]['members_with_a_gift']})
    return out
