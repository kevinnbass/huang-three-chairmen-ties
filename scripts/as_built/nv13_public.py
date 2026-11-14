"""Shared by the audit lane and the public release of the three-chairmen figure (nv13): the figure's rows with their wording,
the gift table without anything that identifies a donor, and one evidence line per cited source.
Nothing here names a donor or a lobbyist: a gift line carries its FEC identifiers and a running donor number."""
import csv, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'research'; PRIMARY = R / 'primary'
PACK = Path('EVIDENCE_SETS')
sys.path.insert(0, str(ROOT / 'scripts'))
import rows_ties as T
import rows_chairmen as C
csv.field_size_limit(10**9)

GIFT_COLS = ['side', 'member', 'bioguide', 'date', 'usd', 'committee_id', 'committee', 'committee_kind', 'employer_as_filed', 'donor_id', 'source', 'note',
             'sub_id', 'tran_id', 'file_num', 'image_num', 'amended_sub_id', 'amended_file_num', 'amended_image_num']
SOURCE_PUBLIC = lambda s: 'earlier-capture' if s.startswith('pack:') else s


def public_gifts():
    """Every counted gift line, both companies. `donor_id` numbers the donors of one company (A001.., N001..) in an arbitrary fixed
    order, so people can be counted; it is not derived from anything a reader could reverse. Occupation is left out."""
    g = T.gifts(); ids = {}
    for side, pre in (('anthropic', 'A'), ('nvidia', 'N')):
        for i, dn in enumerate(sorted({r['dn'] for r in g if r['side'] == side}), 1):
            ids[(side, dn)] = f'{pre}{i:03d}'
    out = []
    for r in g:
        o = {k: r.get(k, '') for k in GIFT_COLS}; o['donor_id'] = ids[(r['side'], r['dn'])]; o['source'] = SOURCE_PUBLIC(r['source']); out.append(o)
    return out


def figure_rows():
    """The rows behind the third version of nv13, each with the words the figure draws, its sources and its passages."""
    out = []
    for t in C.ties():
        out.append({'row_id': t['row_id'], 'table': 'record in a chairman\'s panel', 'member': t['member'], 'section': t['section'], 'type': t['type'],
                    'drawn_text': (t['head'] + '. ' if t['head'] else '') + t['words'], 'usd': t['usd'], 'first': t['first'], 'last': t['last'], 'src': t['src'], 'q': t['q']})
    for k in C.key():
        out.append({'row_id': k['row_id'], 'table': 'key: who is who', 'link': k['id'], 'card': k['card'], 'drawn_text': (k['label'] + '. ' if k['label'] else '') + k['words'], 'src': k['src'], 'q': k['q']})
    for k in C.stake():
        out.append({'row_id': k['row_id'], 'table': 'what is at stake between the two companies', 'link': k['id'], 'card': k['card'], 'drawn_text': (k['label'] + '. ' if k['label'] else '') + k['words'], 'src': k['src'], 'q': k['q']})
    for e in C.events():
        out.append({'row_id': e['row_id'], 'table': 'event on the timeline', 'member': e['lane'], 'date': e['date'], 'end': e['end'], 'drawn_text': e['words'], 'src': e['src'], 'q': e['q']})
    for n in C.numbers().values():
        out.append({'row_id': n['row_id'], 'table': 'number computed for the figure', 'key': n['key'], 'value': n['value'], 'drawn_text': f"{n['value']}: {n['words']}", 'src': n['src'], 'q': n['q']})
    return out


def public_lobbyist_gifts():
    """Every counted gift by a lobbyist or a firm's PAC to one of the three, three sides. No lobbyist is named: each has a number."""
    return C.lobbyist_gifts()


def _pack(path):
    f = open(PACK / path, newline='', errors='replace'); pos = f.tell(); first = f.readline()
    if not first.startswith('#'):
        f.seek(pos)
    return list(csv.DictReader(f))


_PACKS = {}


def pack_row(path, key):
    if path not in _PACKS:
        rows = _pack(path); _PACKS[path] = {(r.get('row_id') or next(iter(r.values()))): r for r in rows}
    return _PACKS[path].get(key)


WHAT = {  # what each kind of evidence-set table is, in a reader's words
    'congress/research/hard_money.csv': 'FEC receipt or disbursement line', 'congress/research/lobbyist_contributions.csv': 'Lobbyist\'s contribution report (form LD-203), U.S. Senate lobbying records',
    'congress/research/lobbying.csv': 'Lobbying registration or quarterly report (forms LD-1, LD-2), U.S. Senate lobbying records', 'congress/research/revolving_door.csv': 'Programme or organisation page listing a placement or a past post',
    'congress/research/travel.csv': 'Congressional hearing record (witness list)', 'congress/research/grants.csv': 'Grant record published by the funder',
    'congress/research/member_statements.csv': 'Search of the member\'s official X account (a bounded search; see the row\'s words)', 'congress/research/timeline.csv': 'FEC filing',
    'congress/research/entities.csv': 'FEC line giving the person\'s employer and title as filed', 'congress/research/interlocks.csv': 'IRS Form 990 (officers and directors; related organisations), as published by ProPublica',
    'lineage/research/flows_annual.csv': 'Grant awards by year, summed from the funder\'s published grant records or a foundation\'s tax filing', 'lineage/research/tenures.csv': 'Published statement of a post held (the organisation\'s page, the person\'s own post, or a news report)',
    'lineage/research/people.csv': 'An organisation\'s published team page naming a person and post',
    'lineage/research/equity.csv': 'Anthropic\'s own announcement of its funding round', 'toner/research/people_graph.csv': 'Organisation page describing a person\'s posts',
    'evaluators-deep/research/people_edges.csv': 'Organisation release naming a person\'s former post',
    'lineage/research/flows_named.csv': 'One grant award, or one grant line of a foundation\'s tax filing',
    'congress/research/super_pac_c4.csv': 'Money into a political group: the giver\'s own announcement, a press report, or a bounded search that found none',
    'congress/research/lb_network_windows.csv': 'A firm\'s lobbying registration for a client (dates), from the U.S. Senate lobbying records',
    'toner/research/cset_people.csv': 'A person\'s post at a research centre, from the centre\'s or the person\'s own page', 'toner/research/cset_money.csv': 'A grant to a research centre, from the funder\'s published grant record'}
TABLE_WHAT = {'employee_gift_rates.csv': 'This repository\'s count of employees\' gifts across the 535 sitting members (research/employee_gift_rates.csv, from research/employee_gifts.csv)',
              'pacs_by_member.csv': 'This repository\'s table of company PAC money by member, from FEC filings', 'lobbying_bill_reports.csv': 'This repository\'s count of lobbying reports naming each bill, from the Senate\'s lobbying records',
              'chip_bills.csv': 'This repository\'s table of chip-export bills, from the bills\' records at govinfo', 'chip_bill_backers.csv': 'This repository\'s table of sponsors and cosponsors, from the bills\' records at govinfo',
              'nv13_numbers.csv': 'This repository\'s table of the numbers computed for the figure (research/nv13_numbers.csv; scripts/verify_nv13.py recomputes them)',
              'lobbyist_gifts.csv': 'This repository\'s table of lobbyists\' and firm PACs\' gifts naming the three chairmen, from the contribution reports (form LD-203) filed with the U.S. Senate',
              'pac_base_rates.csv': 'This repository\'s count of each company PAC\'s gifts across the 535 sitting members, from FEC filings',
              'trade_pac_gifts.csv': 'This repository\'s table of gifts to the three chairmen from the PACs of three trade groups, from the FEC\'s committee-to-candidate file',
              'anthropac_by_recipient.csv': 'This repository\'s table of AnthroPAC\'s contributions by recipient committee, from the committee\'s FEC filings'}


DESCR = {'anthropic-ltbt': 'Anthropic: its page on the Long-Term Benefit Trust', 'anthropic-pfa-1': 'Anthropic: announcement of its first $20 million gift to Public First Action (Feb 12, 2026)',
         'anthropic-pfa-2': 'Anthropic: announcement of a further $20 million to Public First Action (Jul 21, 2026)',
         'art-anthropic-fontaine': 'Anthropic: announcement that Richard Fontaine joins the Long-Term Benefit Trust',
         'art-pfa-conservative': 'Public First Action: release announcing its Conservative AI Consensus Project and the advertisements (Jul 17, 2026)',
         'billstatus-119-hr5885': 'Bill status record of H.R. 5885, 119th Congress', 'billstatus-119-hr6875': 'Bill status record of H.R. 6875, 119th Congress',
         'house-hfac-letter-pr': 'House Foreign Affairs Committee: release on the three chairmen\'s Nov 5 letter to Jensen Huang',
         'x-chinaselect-letter': 'Post on X by the House Select Committee on the CCP with the chairmen\'s second letter (Nov 12, 2026)',
         'x-dream1984-article': 'Article on X, "Who Is Really Behind the Hunt for Jensen Huang?" (Nov 12, 2026)',
         'fec-bulk-indiv26-employers-20261113': 'FEC bulk file of itemised individual contributions, 2026 cycle (indiv26.zip): the lines whose employer begins with ANTHROPIC or NVIDIA',
         'fec-sched_a-employer-anthropic-2026': 'FEC API, Schedule A receipts, employer ANTHROPIC, 2026 cycle', 'fec-sched_a-employer-nvidia-2026': 'FEC API, Schedule A receipts, employer NVIDIA, 2026 cycle'}


def evidence(rows=None):
    """One line per (row, cited source): where a reader can check it. Never a donor's or a lobbyist's name.
    rows: another figure's rows (row_id, src, q); by default this figure's."""
    out = []
    for r in (figure_rows() if rows is None else rows):
        for n, (s, q) in enumerate(zip(r['src'], r['q']), 1):
            e = {'row_id': r['row_id'], 'n': n, 'source_ref': s, 'passage': q, 'kind': '', 'what': '', 'url': '', 'retrieved_utc': '', 'copy_in_repo': ''}
            if s.startswith('pack:'):
                path, key = s[5:].split('#', 1); pr = pack_row(path, key); assert pr is not None, s
                e['kind'] = 'evidence-set row'; e['what'] = WHAT[path]; e['url'] = pr.get('url') or pr.get('source_url') or ''; e['retrieved_utc'] = pr.get('checked_utc', '')
                e['source_ref'] = 'evidence-set:' + path.split('/')[0] + '/' + Path(path).stem + '#' + key
                if path.endswith('lb_network_windows.csv'):                 # the registrant's record in the Senate's lobbying data
                    e['url'] = f'https://lda.gov/api/v1/registrants/{key}/'
            elif s.startswith('table:'):
                name, key = s[6:].split('#', 1); e['kind'] = 'table in this repository'; e['what'] = TABLE_WHAT[name]; e['copy_in_repo'] = 'research/' + name; e['source_ref'] = f'research/{name}#{key}'
            else:
                d = PRIMARY / s; m = json.loads((d / 'meta.json').read_text()) if (d / 'meta.json').exists() else {}
                e['kind'] = 'saved original'; e['url'] = m.get('url') or m.get('zip_url') or ''; e['what'] = DESCR.get(s) or m.get('what') or m.get('title') or m.get('kind') or ''
                if not e['what'] and (d / 'text.txt').exists():           # a fetched page: its own title
                    tt = re.search(r'^TITLE:\s*(.+)$', (d / 'text.txt').read_text(errors='replace')[:1500], re.M); e['what'] = tt.group(1).strip() if tt else ''
                e['retrieved_utc'] = m.get('fetched_utc') or m.get('zip_saved_utc') or m.get('saved_utc') or m.get('fetched') or m.get('copied_utc') or ''
                if not e['url'] or not e['retrieved_utc']:
                    head = (d / 'text.txt').read_text(errors='replace')[:600] if (d / 'text.txt').exists() else ''
                    u = re.search(r'^URL:\s*(\S+)', head, re.M); f_ = re.search(r'^FETCHED:\s*(\S+)', head, re.M)
                    e['url'] = e['url'] or (u.group(1) if u else ''); e['retrieved_utc'] = e['retrieved_utc'] or (f_.group(1) if f_ else '')
            out.append(e)
    return out


if __name__ == '__main__':
    rows = figure_rows(); ev = evidence(); g = public_gifts()
    print('rows', len(rows), {t: sum(1 for r in rows if r['table'] == t) for t in sorted({r['table'] for r in rows})})
    print('evidence lines', len(ev), '| without a url (not a repository table):', sum(1 for e in ev if not e['url'] and e['kind'] != 'table in this repository'))
    print('gift lines', len(g), '| donors', len({x['donor_id'] for x in g}))
    for e in ev:
        if not e['url'] and e['kind'] != 'table in this repository':
            print('  no url:', e['row_id'], e['source_ref'])
