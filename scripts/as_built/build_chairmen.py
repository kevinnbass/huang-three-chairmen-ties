"""Tables behind the third version of the three-chairmen figure (nv13).

Run: python3 -I scripts/build_chairmen.py        (after build_member_ties.py and build_lobbyist_gifts.py)

Reads the tables of the second version (research/member_ties.csv, nv13_links.csv, employee_gifts.csv, pacs_by_member.csv,
pac_base_rates.csv, employee_gift_rates.csv, nv13_members.csv), research/lobbyist_gifts.csv and the saved sources, and writes
  research/nv13_ties.csv     every record drawn in a chairman's panel (ids CT...)
  research/nv13_key.csv      who is who: how each group connects to Anthropic (CK...)
  research/nv13_stake.csv    what is at stake between the two companies (CS...)
  research/nv13_events.csv   dated public events on the timeline (CE...)
  research/nv13_numbers.csv  every number the figure states that is computed here (CN...)
  research/nv13_glance.csv   the at-a-glance table (its cells repeat facts cited in the tables above)
It does not change the second version's tables, so the map figure (nv8), which shares them, is untouched.
Wording changed after the audit of the second version carries the finding it answers in the column `audit`.
No donor and no lobbyist is named: they are counted."""
import csv, json, re, sys, zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'research'; P = R / 'primary'; PACK = Path('EVIDENCE_SETS')
csv.field_size_limit(10**9)
THREE = ['mast', 'moolenaar', 'crawford']
CAND = {'mast': 'H6FL18097', 'moolenaar': 'H4MI04126', 'crawford': 'H0AR01083'}
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
NUM = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
LD = 'Senate lobbying records'


def money(v):
    v = float(v)
    return (f'${v / 1e6:,.1f}M' if v < 100e6 else f'${v / 1e6:,.0f}M') if v >= 1e6 else f'${v:,.0f}'


def day(d, year=True):
    p = d.split('-')
    if len(p) == 2:
        return f'{MON[int(p[1]) - 1]} {p[0]}'
    return f'{MON[int(p[1]) - 1]} {int(p[2])}' + (f', {p[0]}' if year else '')


def span(ds):
    a, b = min(ds), max(ds)
    if a == b:
        return day(a)
    if a[:7] == b[:7]:
        return f'{MON[int(a[5:7]) - 1]} {int(a[8:])}–{int(b[8:])}, {a[:4]}'
    return f'{day(a, a[:4] != b[:4])} to {day(b)}'


def table(name):
    return list(csv.DictReader(open(R / name, newline='')))


def pack(path):
    return {r['row_id']: r for r in csv.DictReader([l for l in (PACK / path).open(newline='') if not l.startswith('#')])}


def text(sid):
    d = P / sid
    return re.sub(r'\s+', ' ', '\n'.join(p.read_text(errors='replace') for p in sorted(d.glob('text*.txt'))))


def has(sid, passage):
    """The passage must be in the saved copy now: a builder that quotes checks its own quotation."""
    n = lambda s: re.sub(r'\s+', ' ', s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–', '-').replace('—', '-'))
    t = n(text(sid))
    if n(passage) not in t:
        b = [p for p in (P / sid).glob('body.*')]
        t += ' ' + n(re.sub(r'<[^>]+>', ' ', b[0].read_text(errors='replace'))) if b and b[0].suffix in ('.html', '.json') else ''
    assert n(passage) in t, (sid, passage[:80])
    return passage


TIES, KEY, STAKE, EVENTS, NUMS = [], [], [], [], []


def tie(member, section, typ, mark, head, words, src, q, usd='', first='', last='', audit=''):
    src = [src] if isinstance(src, str) else list(src); q = [q] if isinstance(q, str) else list(q)
    assert len(src) == len(q), (member, typ)
    TIES.append({'member': member, 'section': section, 'type': typ, 'mark': mark, 'head': head, 'words': words, 'usd': usd, 'first': first, 'last': last,
                 'audit': audit, 'src': ' || '.join(src), 'q': ' || '.join(q)})


def num(key, value, words, src=None, q=None):
    src = [] if src is None else ([src] if isinstance(src, str) else list(src)); q = [] if q is None else ([q] if isinstance(q, str) else list(q))
    NUMS.append({'key': key, 'value': str(value), 'words': words, 'src': ' || '.join([f'table:nv13_numbers.csv#{key}'] + src), 'q': ' || '.join([str(value)] + q)})


FIRM = {'BROWNSTEIN HYATT FARBER SCHRECK, LLP': 'Brownstein Hyatt Farber Schreck', 'BGR GOVERNMENT AFFAIRS': 'BGR Government Affairs', 'THE VOGEL GROUP': 'the Vogel Group',
        'TIBER CREEK GROUP': 'Tiber Creek Group', 'NAVIGATORS GLOBAL LLC (FORMERLY DC NAVIGATORS, LLC)': 'Navigators Global', 'BALLARD PARTNERS': 'Ballard Partners',
        'KYLE HOUSE GROUP': 'Kyle House Group', 'DENTONS US LLP': 'Dentons'}
CLIENT = {'NVIDIA CORPORATION': 'Nvidia', 'NVIDIA': 'Nvidia', 'ANTHROPIC PBC': 'Anthropic', 'ANTHROPIC, PBC': 'Anthropic', 'ANTHROPIC': 'Anthropic',
          'OPEN PHILANTHROPY ACTION FUND': 'Open Philanthropy Action Fund', 'AMERICANS FOR RESPONSIBLE INNOVATION': 'Americans for Responsible Innovation (ARI)',
          'FUTURE OF LIFE INSTITUTE': 'the Future of Life Institute'}
FILINGS = {'nvidia': ('lda-gov-nvidia-2024', 'lda-gov-nvidia-2025', 'lda-gov-nvidia-2026'), 'anthropic': ('lda-gov-anthropic-2024', 'lda-gov-anthropic-2025', 'lda-gov-anthropic-2026')}


def lobby_words(rows):
    """Plain words for one member's lobbyist gifts on one side, firm by firm. Lobbyists are counted, never named."""
    firms = defaultdict(list)
    for r in rows:
        firms[r['registrant']].append(r)
    out = []
    for reg, rs in sorted(firms.items(), key=lambda kv: min(r['date'] for r in kv[1])):
        cl = CLIENT[rs[0]['client']]; f = FIRM[reg]; since = rs[0]['registered_from'][:7]; end = rs[0]['registration_ended'][:7]
        when = f'from {MON[int(since[5:7]) - 1] if since[:4] == end[:4] else day(since)} to {day(end)}' if end else f'since {day(since)}'
        parts = []
        for measure, how in (('named', 'listed there for ' + cl), ('firm_only', 'not listed for ' + cl), ('firm_only_not_classified', 'there (whether listed for that client was not checked)'), ('firm_pac', '')):
            # a committee's contribution that a lobbyist's report lists is said as that, not as the lobbyist's own gift (corrected Nov 16, 2026)
            com = [r for r in rs if r['measure'] == measure and measure != 'firm_pac' and r['own_money'] == 'no']
            if com:
                assert all(r['contributor'].startswith('a campaign committee') for r in com), [r['item'] for r in com]
                cds = [r['date'] for r in com]; assert len(com) == 1
                parts.append(f'{money(sum(float(r["amount_usd"]) for r in com))} from a campaign committee that a lobbyist there lists in a contribution report and that carries that lobbyist\'s name '
                             f'(the committee\'s money, not the lobbyist\'s own), on {span(cds)}')
            ms = [r for r in rs if r['measure'] == measure and r not in com]
            if not ms:
                continue
            usd = sum(float(r['amount_usd']) for r in ms); n = len({r['lobbyist_no'] for r in ms}); ds = [r['date'] for r in ms]
            on = ('on ' if min(ds) == max(ds) else '') + span(ds)
            oth = [r['payee'].title().replace('Pac', 'PAC') for r in ms if not re.search(r'FOR CONGRESS|WINRED', r['payee']) and r['member'].upper() not in r['payee'].upper()]   # a payee that is another committee
            to = f', to {oth[0]} with him named as honoree' if oth else ''
            if measure == 'firm_pac':
                parts.append(f'{money(usd)} from the firm\'s own PAC ({span(ds)})')
            else:
                k = f'{NUM[n]} lobbyist{"s" if n != 1 else ""}' if n > 1 else 'a lobbyist'
                gifts = f' in {NUM[len(ms)]} gifts' if len(ms) > n else ''
                parts.append(f'{money(usd)} from {k} {how}{gifts}, {on}{to}')
        out.append(f'{f[0].upper() + f[1:]} (registered for {cl} {when}): ' + '; '.join(parts) + '.')
    return ' '.join(out)


def committee_lines(rows):
    """The lines that are a committee's contribution listed in a lobbyist's report (not the lobbyist's own money, and not the firm's PAC)."""
    return [r for r in rows if r['measure'] not in ('firm_pac', 'own_pac') and r['own_money'] == 'no']


def givers(rows):
    if any(r['measure'] == 'firm_pac' for r in rows):
        return 'lobbyists, or the PAC, of firms'
    return 'lobbyists at firms' if len(rows) > 1 else 'a lobbyist at a firm'


def main():
    TY = [r for r in table('member_ties.csv') if r['member'] in THREE]
    ty = lambda m, typ: next(r for r in TY if r['member'] == m and r['type'].startswith(typ))
    sq = lambda r: (r['src'].split(' || '), r['q'].split(' || '))
    gifts = [g for g in table('employee_gifts.csv') if g['member'] in THREE]
    LG = table('lobbyist_gifts.csv')
    who = {r['key']: r for r in table('nv13_members.csv')}
    rates = {r['side']: r for r in table('employee_gift_rates.csv')}
    base = {r['pac']: r for r in table('pac_base_rates.csv')}
    pacs = defaultdict(list)
    for r in table('pacs_by_member.csv'):
        pacs[r['member_bioguide']].append(r)

    # ---- campaign totals, for scale (FEC "all candidates" file, coverage through Oct 14, 2026)
    wt = (P / 'fec-bulk-weball26-20261113' / 'text.txt').read_text()
    tot = {}
    for m, cid in CAND.items():
        mm = re.search(rf'CAND_ID={cid}; CAND_NAME=([^;]+); TTL_RECEIPTS=([\d.]+); TTL_INDIV_CONTRIB=([\d.]+);.*?CVG_END_DT=(\S+)', wt)
        assert mm, cid
        tot[m] = {'receipts': float(mm.group(2)), 'q': f'CAND_ID={cid}; CAND_NAME={mm.group(1)}; TTL_RECEIPTS={mm.group(2)}', 'end': mm.group(4)}
        assert mm.group(4) == '10/14/2026'

    # ---- lobbyists' own gifts, three sides, one rule (build_lobbyist_gifts.py)
    def lob(side, m):
        return [r for r in LG if r['side'] == side and r['member'] == m and r['measure'] != 'own_pac']

    def lob_src(rows, side):
        src, q = [], []
        for r in rows:
            src += [f'table:lobbyist_gifts.csv#{r["item"]}', r['source'].split('/')[0]]; q += [r['amount_usd'], r['report_url']]
        for reg in sorted({r['registrant'] for r in rows}):
            if side in FILINGS:
                hit = [s for s in FILINGS[side] if reg in json.dumps(json.loads((P / s / 'body.json').read_text()))]
                src.append(hit[0]); q.append(reg)
            else:
                w = [x for x in csv.DictReader([l for l in (PACK / 'congress/research/lb_network_windows.csv').open(newline='') if not l.startswith('#')]) if x['registrant_name'] == reg]
                src.append('pack:congress/research/lb_network_windows.csv#' + w[0]['registrant_id']); q.append(w[0]['client_name'])
        return src, q
    NOTE = ' Each is reported as the giver\'s own contribution; the reports do not show whether a client asked for it.'

    # ---- PACs of trade groups: which company each group lists as a member (its own page), and what its PAC gave the three (FEC)
    TRADE = [('sia', 'Semiconductor Industry Association', 'C00613521', 'art-sia-members'), ('iti', 'Information Technology Industry Council', 'C00419036', 'art-iti-members'),
             ('technet', 'TechNet', 'C00328369', 'art-technet-members-all')]
    PA_ = P / 'fec-bulk-pas226-20261112'
    pas = [l.split('|') for l in zipfile.ZipFile(PA_ / 'pas226.zip').read('itpas2.txt').decode('latin-1').splitlines() if l.split('|')[0] in {t[2] for t in TRADE} and l.split('|')[5] in ('24K', '24Z')]
    cmr = [l.split('|') for l in zipfile.ZipFile(PA_ / 'cm26.zip').read('cm.txt').decode('latin-1').splitlines()]
    cmn = {l[0]: l[1] for l in cmr}; cm_cand = {l[0]: l[14] for l in cmr}
    # The third audit found twelve of TechNet's lines with no candidate id; counting the blank as one candidate gave 26, not 36.
    # A blank id is now resolved through the recipient committee (OTHER_ID) in the committee master, and a line that still has none stops the build.
    for l in pas:
        if not l[16]:
            l[16] = cm_cand.get(l[15], '')
        assert l[16], ('a PAC line names no candidate and its recipient committee has none', l[0], l[15])
    lists = {}; TG = []
    for g, gname, cid, pid in TRADE:
        t_ = text(pid); n_members = int(re.search(r'\((\d+) names;', t_).group(1))
        lists[g] = {'name': gname, 'nvidia': 'Nvidia is listed.' in t_, 'anthropic': 'Anthropic is listed.' in t_, 'members': n_members, 'pid': pid,
                    'candidates': len({l[16] for l in pas if l[0] == cid}), 'usd_all': sum(float(l[14]) for l in pas if l[0] == cid)}
        assert lists[g]['candidates'] == {'sia': 11, 'iti': 35, 'technet': 36}[g], (g, lists[g]['candidates'])       # the third audit's recount
        assert ('Nvidia is listed.' in t_) != ('Nvidia is not listed.' in t_) and ('Anthropic is listed.' in t_) != ('Anthropic is not listed.' in t_), pid
        for l in pas:
            m_ = {v: k for k, v in CAND.items()}.get(l[16])
            if l[0] == cid and m_:
                d_ = f'{l[13][4:]}-{l[13][:2]}-{l[13][2:4]}'
                TG.append({'key': f'{g}:{m_}:{d_}', 'group': g, 'group_name': gname, 'committee_id': cid, 'committee': cmn[cid], 'member': m_, 'cand_id': l[16], 'date': d_, 'usd': l[14],
                           'lists_nvidia': 'yes' if lists[g]['nvidia'] else 'no', 'lists_anthropic': 'yes' if lists[g]['anthropic'] else 'no', 'tran_id': l[17], 'image_num': l[4], 'sub_id': l[21],
                           'fec_page_url': 'https://docquery.fec.gov/cgi-bin/fecimg/?' + l[4]})
    assert lists['sia']['nvidia'] and not lists['sia']['anthropic'] and lists['iti']['nvidia'] and not lists['iti']['anthropic'] and lists['technet']['nvidia'] and lists['technet']['anthropic']
    assert not [x for x in TG if x['group'] == 'technet'], 'TechNet\'s PAC gave to one of the three: the wording below must change'
    with open(R / 'trade_pac_gifts.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(TG[0]), lineterminator='\n'); w.writeheader(); w.writerows(sorted(TG, key=lambda x: (x['member'], x['date'])))
    LISTED = 'The lists were read on Nov 13, 2026 and do not say who was a member when a gift was made.'
    bills = {r['key']: r for r in table('chip_bills.csv')}

    for m in THREE:
        name = who[m]['name'].replace('Rep. ', ''); last = name.split()[-1]
        # ===== Anthropic itself
        gs = sorted((g for g in gifts if g['member'] == m and g['side'] == 'anthropic'), key=lambda g: g['date'])
        usd = sum(float(g['usd']) for g in gs); people = len({g['dn'] for g in gs})
        cl, cur = [], []
        for g in gs:                                   # gifts within a week of each other read as one date range
            if cur and (date.fromisoformat(g['date']) - date.fromisoformat(cur[-1]['date'])).days > 7:
                cl.append(cur); cur = []
            cur.append(g)
        cl.append(cur)
        bits = [f'{money(sum(float(g["usd"]) for g in c))} on {span([g["date"] for g in c])}' for c in cl]
        when = bits[0] if len(bits) == 1 else ', '.join(bits[:-1]) + ' and ' + bits[-1]
        jf = [g for g in gs if g['committee_kind'] != 'campaign committee' and 'VICTORY' in g['committee']]
        assert len({g['committee_id'] for g in jf}) <= 1, (m, 'more than one joint committee: word each')
        joint = f' ({money(sum(float(g["usd"]) for g in jf))} of it to {jf[0]["committee"].title()}, a joint fundraising committee)' if jf else ''
        share = usd / tot[m]['receipts']
        o = ty(m, 'employee_gifts'); s0, q0 = [], []
        for r in TY:
            if r['member'] == m and r['type'] == 'employee_gifts' and r['side'] == 'anthropic':
                s0, q0 = sq(r)
        assert abs(usd - float(next(r['usd'] for r in TY if r['member'] == m and r['type'] == 'employee_gifts' and r['side'] == 'anthropic'))) < 0.5
        s0 += ['fec-bulk-weball26-20261113']; q0 += [tot[m]['q']]
        if jf:                                         # the joint committee's own FEC record, saved for this figure
            jsrc = sorted(x.name for x in P.glob(f"fec-committee-{jf[0]['committee_id'].lower()}-*"))[0]
            s0 += [jsrc]; q0 += [has(jsrc, 'designation_full: Joint fundraising committee')]
        tie(m, 'anthropic', 'employee_gifts', 'A', 'Employees\' own gifts',
            f'{money(usd)} from {NUM[people] if people > 1 else "one"} {"people" if people > 1 else "person"} who gave Anthropic as employer, in {NUM[len(gs)]} contributions to committees tied to him: {when}{joint}. '
            f'Their own money, not the company\'s. For scale, it equals {share * 100:.1f}% of the {money(tot[m]["receipts"])} his campaign reported raising from Jan 2025 to Oct 14, 2026'
            + ('; the records do not show how much of the joint committee\'s money reached the campaign.' if jf else '.'),
            s0, q0, usd=f'{usd:.2f}', first=gs[0]['date'], last=gs[-1]['date'], audit='B-01' + (' V3-CT01 B3-21' if jf else ''))
        num(f'emp:anthropic:{m}', f'{usd:.0f}', f'Anthropic employees\' gifts to committees tied to {last}')
        num(f'emp_people:anthropic:{m}', people, f'people who gave them')
        num(f'emp:nvidia:{m}', f'{sum(float(g["usd"]) for g in gifts if g["member"] == m and g["side"] == "nvidia"):.0f}', f'Nvidia employees\' gifts to committees tied to {last}')
        num(f'receipts:{m}', f'{tot[m]["receipts"]:.2f}', f'{last}\'s campaign receipts, 2026 cycle through Oct 14, 2026', 'fec-bulk-weball26-20261113', tot[m]['q'])
        num(f'share:{m}', f'{share * 100:.1f}', 'the Anthropic employees\' gifts as a percentage of those receipts')
        pa = [r for r in TY if r['member'] == m and r['type'] == 'company_pac' and r['side'] == 'anthropic']
        if pa:
            assert pa[0]['panel'].startswith('AnthroPAC, Anthropic\'s own political committee, gave ')
            tie(m, 'anthropic', 'company_pac', 'A', 'AnthroPAC', pa[0]['panel'].replace('AnthroPAC, Anthropic\'s own political committee, gave ', 'Anthropic\'s own political committee gave '),
                *sq(pa[0]), usd=pa[0]['usd'], first=pa[0]['first'], last=pa[0]['last'])
        else:
            tie(m, 'anthropic', 'company_pac', 'G', 'AnthroPAC', 'No gift on file from AnthroPAC, Anthropic\'s own political committee (its filings through Sep 30, 2026).',
                'table:pac_base_rates.csv#anthropic', base['anthropic']['latest_line'])
        if m == 'moolenaar':
            o = ty(m, 'witness'); s, q = sq(o)
            s += ['house-hrg-zs00-20250625-transcript', 'house-hrg-zs00-20250625-transcript', 'house-hrg-zs00-20250625-clark-statement', 'house-hrg-zs00-20250625-clark-statement', 'house-hrg-zs00-20250625-clark-statement']
            q += [has('house-hrg-zs00-20250625-transcript', 'Moolenaar [chairman of the select committee] presiding'), has('house-hrg-zs00-20250625-transcript', 'STATEMENT OF MR. JACK CLARK'),
                  has('house-hrg-zs00-20250625-clark-statement', 'Co-Founder and Head of Policy, Anthropic'),
                  has('house-hrg-zs00-20250625-clark-statement', 'maintaining and strengthening export controls of advanced semiconductors to China'),
                  has('house-hrg-zs00-20250625-clark-statement', 'ongoing work to prevent China from obtaining advanced semiconductor chips')]
            tie(m, 'anthropic', 'witness', 'A', 'Its co-founder before his committee',
                'Jack Clark, then Anthropic\'s co-founder and head of policy, testified to the House Select Committee on the CCP on Jun 25, 2025; the transcript shows Moolenaar presiding. '
                'Clark\'s written statement says the government should control powerful AI "by maintaining and strengthening export controls of advanced semiconductors to China" '
                'and thanks the committee for its "ongoing work to prevent China from obtaining advanced semiconductor chips".',
                s, q, first='2025-06-25', audit='B-17 A-TY090')
        lb = [r for r in TY if r['member'] == m and r['type'].startswith('lobbying')]
        for o in lb:
            tie(m, 'anthropic', o['type'], 'A', 'Lobbying on his bill', o['panel'], *sq(o))
        if m == 'crawford':
            tie(m, 'anthropic', 'cosponsor', 'G', 'The bills the lobbying reports name',
                'He sponsors neither of the two chip bills the lobbying reports were searched for, H.R. 5885 and H.R. 6875. He cosponsored Moolenaar\'s H.R. 5885 on Nov 18, 2025 and was an original cosponsor of Mast\'s H.R. 6875 on Dec 18, 2025. '
                'Reports naming other bills of his were not counted.',
                ['table:chip_bill_backers.csv#hr5885:C001087', 'table:chip_bill_backers.csv#hr6875:C001087'], ['2025-11-18', '2025-12-18'], audit='V3-CT47 B3-19')
        la = lob('anthropic', m)
        if la:
            u = sum(float(r['amount_usd']) for r in la)
            tie(m, 'anthropic', 'lobbyists', 'A', 'Lobbyists at Anthropic\'s firms',
                f'{money(u)} in {NUM[len(la)]} gift{"s" if len(la) != 1 else ""} from {givers(la)} then registered to lobby for Anthropic. ' + lobby_words(la) + NOTE,
                *lob_src(la, 'anthropic'), usd=f'{u:.2f}', first=min(r['date'] for r in la), last=max(r['date'] for r in la))
        else:
            tie(m, 'anthropic', 'lobbyists', 'G', 'Lobbyists at Anthropic\'s firms',
                'None found: no gift naming him is reported, for Jan 2024 to Jun 2026, by a lobbyist at a firm then registered to lobby for Anthropic.',
                f'table:nv13_numbers.csv#lob:anthropic:{m}:total', '0')
        tie(m, 'anthropic', 'trade_pacs', 'G', 'Trade groups\' PACs',
            f'Of three trade groups whose member lists were read, none lists Anthropic and not Nvidia. TechNet lists both ({lists["technet"]["members"]} members); its PAC gave none of the three anything (FEC records through Sep 2026).',
            ['art-technet-members-all', 'art-technet-members-all', f'table:nv13_numbers.csv#trade:technet:three'], [has('art-technet-members-all', 'Nvidia is listed. Anthropic is listed.'), has('art-technet-members-all', 'NVIDIA'), '0'])
        # ===== Public First Action
        if m in ('mast', 'moolenaar'):
            tie(m, 'pfa', 'ads', 'A', 'Ads announced',
                'On Jul 17, 2026 Public First Action announced advertisements "highlighting the strong records of 12 Republican members of Congress"; its page lists 11, all in the House, him among them.',
                ['art-pfa-conservative', 'art-pfa-conservative'], [has('art-pfa-conservative', 'highlighting the strong records of 12 Republican members of Congress'), has('art-pfa-conservative', f'Rep. {name}')],
                first='2026-07-17')
            o = ty(m, 'ad_run'); s, q = sq(o)
            pid2 = 'google-ads-creative-fl21-v2-20261113' if m == 'mast' else 'google-ads-creative-mi2-v2-20261113'
            s += [pid2, pid2]; q += [has(pid2, f'CONGRESSMAN {name.upper()} BACKING LEGISLATION TO PUT EXPORT CONTROLS ON ADVANCED CHIPS'), has(pid2, '2 of 2 variations')]
            old_ = o['panel']
            mm = re.search(r'ran from (\w+ \d+, \d+) to (\w+ \d+, \d+), aimed at (.+?)\. Google\'s political-ads report gives ([\d,]+ to [\d,]+) showings and (\$[\d,]+ to \$[\d,]+) spent\. On screen: (.+)$', old_)
            assert mm, old_
            if m == 'mast':
                cz = [l.split('|') for l in (P / 'census-cd119-zcta-20261113' / 'tab20_cd11920_zcta520_natl.txt').read_text(encoding='utf-8-sig').splitlines()[1:]]
                z = {l[8] for l in cz if l[1] == '1221' and l[8]}; also = {l[8] for l in cz if l[1] != '1221' and l[8] in z}
                assert (len(z), len(also)) == (38, 11)
                where = f'{len(z)} Florida zip codes, which are the {len(z)} zip-code areas the Census Bureau maps wholly or partly to his district (FL-21); {NUM[len(also)]} of them also reach into another district'
                num('fl21_zip_areas', len(z), 'zip-code areas wholly or partly in FL-21 (Census Bureau)', 'census-cd119-zcta-20261113', 'Congressional District 21')
                num('fl21_zip_areas_shared', len(also), 'of those, areas that also lie in another district')
            else:
                where = 'his district (MI-2)'
            tie(m, 'pfa', 'ad_run', 'A', 'The ad as it ran',
                f'Google\'s political-ads report lists a 30-second video by Public First Action shown from {mm.group(1)} to {mm.group(2)}, aimed at {where}. '
                f'For that entry, which has two versions, Google gives {mm.group(4)} showings and {mm.group(5)} spent. Both versions show the same words: {mm.group(6)} The voice-over was not captured.',
                s, q, first=o['first'], last=o['last'], audit='B-18 A-TY048' if m == 'mast' else 'B-19 A-TY081')
        # ===== groups Open Philanthropy, or its related foundation, has funded
        ar = [r for r in TY if r['member'] == m and r['type'] == 'ari_pac']
        if ar:
            tie(m, 'network', 'ari_pac', 'W', 'ARI\'s PAC', ar[0]['panel'], *sq(ar[0]), usd=ar[0]['usd'], first=ar[0]['first'], last=ar[0]['last'])
        own = [r for r in LG if r['side'] == 'network' and r['member'] == m and r['measure'] == 'own_pac']
        if own and not ar:                              # ARI's own report to the Senate lists a gift the FEC table keyed to him does not hold
            r = own[0]; assert len(own) == 1 and 'RESPONSIBLE INNOVATION' in r['registrant']
            tie(m, 'network', 'ari_pac', 'W', 'ARI\'s PAC',
                f'ARI\'s report to the Senate lists {money(float(r["amount_usd"]))} from its PAC on {day(r["date"])} to {r["payee"].title()}, a joint fundraising committee, with him named as honoree.',
                [f'table:lobbyist_gifts.csv#{r["item"]}', r['source'].split('/')[0]], [r['amount_usd'], r['report_url']], usd=r['amount_usd'], first=r['date'], last=r['date'])
        elif own:
            assert all(abs(float(a['usd']) - sum(float(r['amount_usd']) for r in own)) < 0.5 for a in ar), 'ARI PAC lines in the two records differ'
        for typ, head in (('fellow', None), ('advisor', 'An Institute for Progress fellow advising his committee'), ('left:RD056', 'Former committee staff, now at ARI'),
                          ('left:WPE3178', 'Former committee staff, now at the Center for AI Safety')):
            for o in [r for r in TY if r['member'] == m and r['type'].startswith(typ)]:
                tie(m, 'network', o['type'], 'W', head or 'A Horizon fellow with his committee', o['panel'], *sq(o), first=o['first'])
        nw = [r for r in TY if r['member'] == m and r['type'] == 'net_witness']
        if nw:
            o = nw[0]; old_ = 'Six witnesses from three groups Open Philanthropy has funded (Center for a New American Security 3, Carnegie Endowment 2, Foundation for American Innovation 1) testified to House Foreign Affairs subcommittees, Feb 2025 to Feb 2026.'
            assert o['panel'].startswith(old_), o['panel']
            tie(m, 'network', 'net_witness', 'W', 'Witnesses from groups it has funded',
                'Six people from three groups Open Philanthropy has funded (Center for a New American Security 3, Carnegie Endowment 2, Foundation for American Innovation 1) were listed as witnesses for hearings of '
                'House Foreign Affairs subcommittees dated Feb 2025 to Feb 2026. One hearing, dated Nov 20, 2025, was titled "Export Control Loopholes: Chipmaking Tools and their Subcomponents". '
                'None was listed with Anthropic. A witness list does not show who appeared.', *sq(o), first=o['first'], last=o['last'], audit='B-13 A-TY057')
        if m == 'mast':
            tie(m, 'network', 'endorse', 'W', 'ARI named among his bill\'s backers',
                'His committee\'s release of Jan 21, 2026 says the bill "has received broad support from industry groups including the Foundation for Defense of Democracies Action, American Compass, '
                'Americans for Responsible Innovation, the American Security Fund and Exiger."',
                'art-hfac-overwatch-advances', has('art-hfac-overwatch-advances', 'has received broad support from industry groups including the Foundation for Defense of Democracies Action, American Compass, '
                                                                                   'Americans for Responsible Innovation, the American Security Fund and Exiger.'), first='2026-01-21', audit='B3-16')
        if m == 'moolenaar':
            assert bills['s3150']['title'] == bills['hr5885']['title'] == 'GAIN AI Act of 2025' and bills['hr5885']['introduced'] == '2025-10-31'
            tie(m, 'network', 'endorse', 'W', 'ARI on the Senate\'s version of his bill',
                'TechSpot reported on Sep 4, 2025: "Americans for Responsible Innovation calls the GAIN AI Act a "major win" for US economic competitiveness and national security." '
                'That was the proposal then in the Senate\'s defence bill; he introduced the House bill of the same name on Oct 31, 2025.',
                ['art-techspot-gain', 'art-techspot-gain', 'table:chip_bills.csv#hr5885'],
                [has('art-techspot-gain', 'Americans for Responsible Innovation calls the GAIN AI Act a "major win" for US economic competitiveness and national security.'), has('art-techspot-gain', '2025-09-04'), '2025-10-31'],
                first='2025-09-04', audit='B3-16')
        ai = [r for r in TY if r['member'] == m and r['type'] == 'aide']
        if ai:
            assert ai[0]['panel'].startswith('A lobbyist registered in early 2025 for Open Philanthropy Action Fund')
            kw = [x for x in csv.DictReader([l for l in (PACK / 'congress/research/lb_network_windows.csv').open(newline='') if not l.startswith('#')])
                  if x['registrant_name'] == 'KYLE HOUSE GROUP' and x['client_name'] == 'OPEN PHILANTHROPY ACTION FUND']
            lbrow = pack('congress/research/lobbying.csv')['LB323']
            assert len(kw) == 1 and kw[0]['window_start'] == '2023-03-01' and lbrow['registrant'] == 'KYLE HOUSE GROUP' and lbrow['client'] == 'OPEN PHILANTHROPY ACTION FUND'
            s_, q_ = sq(ai[0])
            tie(m, 'network', 'aide', 'W', 'Former aide, later a lobbyist for Open Philanthropy Action Fund',
                'A lobbyist listed for Open Philanthropy Action Fund in a report for the first quarter of 2025, on foreign assistance, gives "Legislative Assistant, Rep. Brian Mast" among past posts. '
                'The firm has been registered for that client since Mar 1, 2023. The report does not date that person\'s time in Mast\'s office, or when that person began work for the client.',
                s_ + ['pack:congress/research/lb_network_windows.csv#' + kw[0]['registrant_id']], q_ + ['2023-03-01'], first='2025', audit='B-12 A-TY049 V3-CT10 B3-25')
        ln = lob('network', m)
        if ln:
            u = sum(float(r['amount_usd']) for r in ln)
            tie(m, 'network', 'lobbyists', 'G', 'Lobbyists and a PAC at these groups\' firms' if any(r['measure'] == 'firm_pac' for r in ln) else 'Lobbyists at these groups\' firms',
                f'{money(u)} in {NUM[len(ln)]} gift{"s" if len(ln) != 1 else ""} {"reported by" if committee_lines(ln) else "from"} {givers(ln)} then registered to lobby for one of these groups. ' + lobby_words(ln) + NOTE,
                *lob_src(ln, 'network'), usd=f'{u:.2f}', first=min(r['date'] for r in ln), last=max(r['date'] for r in ln), audit='B-14 B-15 B-16 A-TY056 A-TY089')
        # ===== said in public at the time (Mast's bill)
        if m == 'mast':
            tie(m, 'said', 'release', 'G', 'His committee\'s release, Jan 21, 2026',
                'On the day his committee approved the bill, its release quoted him: "Companies like Nvidia are requesting to sell millions of advanced AI chips, which are the cutting edge of warfare, to Chinese military companies like Alibaba and Tencent."',
                'art-hfac-overwatch-advances', has('art-hfac-overwatch-advances', 'Companies like Nvidia are requesting to sell millions of advanced AI chips, which are the cutting edge of warfare, to Chinese military companies like Alibaba and Tencent.'),
                first='2026-01-21')
            tie(m, 'said', 'sacks', 'G', 'A claim about the bill\'s backers',
                'The Register reported that day that the White House\'s AI adviser, David Sacks, "endorsed a post that speculated that the bill had been orchestrated by "never Trumpers" with financial support from Anthropic CEO Dario Amodei." '
                'No record here tests that claim.',
                ['art-register-overwatch', 'art-register-overwatch'], [has('art-register-overwatch', 'White House AI advisor David Sacks endorsed a post that speculated that the bill had been orchestrated by'),
                                                                     has('art-register-overwatch', 'with financial support from Anthropic CEO Dario Amodei')], first='2026-01-21')
        # ===== the same records for Nvidia
        assert not [g for g in gifts if g['member'] == m and g['side'] == 'nvidia']
        tie(m, 'nvidia', 'employee_gifts', 'G', 'Employees\' own gifts',
            'None found from anyone who gave Nvidia as employer to a committee tied to him, in FEC records for Jan 2025 to Sep 2026, counted by the same rule.',
            [f'table:nv13_numbers.csv#emp:nvidia:{m}', 'table:employee_gift_rates.csv#nvidia'], ['0', 'nvidia'], audit='B-22 A-TY053 A-TY061 A-TY084')
        lv = lob('nvidia', m); u = sum(float(r['amount_usd']) for r in lv)
        tie(m, 'nvidia', 'lobbyists', 'N', 'Lobbyists and a PAC at Nvidia\'s firms' if any(r['measure'] == 'firm_pac' for r in lv) else 'Lobbyists at Nvidia\'s firms',
            f'{money(u)} in {NUM[len(lv)] if len(lv) < len(NUM) else len(lv)} gift{"s" if len(lv) != 1 else ""}, {span([r["date"] for r in lv])}, from {givers(lv)} then registered to lobby for Nvidia. ' + lobby_words(lv) + NOTE,
            *lob_src(lv, 'nvidia'), usd=f'{u:.2f}', first=min(r['date'] for r in lv), last=max(r['date'] for r in lv))
        if m == 'mast':
            tie(m, 'nvidia', 'meeting', 'N', 'Huang before his committee',
                'Fortune reported on May 2, 2025 that Huang "addressed the upcoming rules in a recent meeting with the House Foreign Affairs Committee", which Mast chairs. '
                'The report gives no date for the meeting and does not say which members attended.',
                ['art-fortune-nvidia-tall-tales', 'art-fortune-nvidia-tall-tales'],
                [has('art-fortune-nvidia-tall-tales', 'addressed the upcoming rules in a recent meeting with the House Foreign Affairs Committee'), has('art-fortune-nvidia-tall-tales', 'PUBLISHED: 2025-05-02')],
                first='2025-05-02', audit='B3-17')
        tg = sorted((x for x in TG if x['member'] == m and x['lists_nvidia'] == 'yes' and x['lists_anthropic'] == 'no'), key=lambda x: x['date'])
        both = ' and '.join(f'the {lists[g]["name"]}' for g in ('sia', 'iti'))
        if tg:
            u = sum(float(x['usd']) for x in tg); parts = []
            for g in ('sia', 'iti'):
                xs = [x for x in tg if x['group'] == g]
                if xs:
                    amts = [f'{money(float(x["usd"]))} on {day(x["date"])}' for x in xs]
                    parts.append(f'the {lists[g]["name"]}\'s PAC gave ' + (' and '.join(amts)) + f' (it gave to {lists[g]["candidates"]} candidates in all; the group lists {lists[g]["members"]} members)')
            tie(m, 'nvidia', 'trade_pacs', 'N', 'PACs of trade groups that list Nvidia',
                f'{money(u)} in {NUM[len(tg)]} gifts from the PACs of two trade groups that list Nvidia as a member and do not list Anthropic: ' + '; '.join(parts) + '. ' + LISTED,
                [f'table:trade_pac_gifts.csv#{x["key"]}' for x in tg] + ['art-sia-members', 'art-iti-members'], [x['usd'] for x in tg] + [has('art-sia-members', 'Nvidia is listed. Anthropic is not listed.'), has('art-iti-members', 'Nvidia is listed. Anthropic is not listed.')],
                usd=f'{u:.2f}', first=tg[0]['date'], last=tg[-1]['date'])
        else:
            tie(m, 'nvidia', 'trade_pacs', 'G', 'PACs of trade groups that list Nvidia',
                f'None found from the PACs of {both}, two trade groups that list Nvidia as a member and do not list Anthropic (FEC records through Sep 2026).',
                ['art-sia-members', 'art-iti-members', f'table:nv13_numbers.csv#trade:nvidia:{m}'], [has('art-sia-members', 'Nvidia is listed. Anthropic is not listed.'), has('art-iti-members', 'Nvidia is listed. Anthropic is not listed.'), '0'])
        num(f'trade:nvidia:{m}', f'{sum(float(x["usd"]) for x in tg):.0f}', f'gifts to {last} from PACs of trade groups that list Nvidia and not Anthropic (SIA, ITI)')
        nb = [o for o in lb if int(o['n'].split('/')[1])]
        tie(m, 'nvidia', 'lobbying', 'N' if nb else 'G', 'Lobbying on his bill',
            ' '.join(f'{o["n"].split("/")[1]} lobbying report{"s" if o["n"].split("/")[1] != "1" else ""} filed for Nvidia name{"" if o["n"].split("/")[1] != "1" else "s"} his {re.match(r"(H\.R\. \d+)", o["panel"]).group(1)} (Anthropic\'s: {o["n"].split("/")[0]}).' for o in nb)
            if nb else 'He sponsors neither H.R. 5885 nor H.R. 6875, the two chip bills counted here, so no report is counted for him. Reports naming other bills of his were not searched.',
            [s for o in nb for s in sq(o)[0]] or ['table:chip_bill_backers.csv#hr5885:C001087', 'table:chip_bill_backers.csv#hr6875:C001087'], [x for o in nb for x in sq(o)[1]] or ['2025-11-18', '2025-12-18'],
            audit='' if nb else 'V3-CT47 B3-19')
        tie(m, 'nvidia', 'company_pac', 'G', 'Nvidia\'s PAC',
            f'Nvidia\'s employee PAC has reported no contribution to any sitting member (filings through {day(base["nvidia"]["latest_efiled_report_ends"])}).',
            'table:pac_base_rates.csv#nvidia', base['nvidia']['sitting_members_with_net_above_zero'])
        tie(m, 'nvidia', 'ads', 'G', 'Political ads',
            'Google\'s political-ads search offers no advertiser named Nvidia (searched Nov 13, 2026; the same search finds Public First Action). Other platforms and television were not searched.',
            ['google-ads-political-search-nvidia-20261113', 'google-ads-political-search-nvidia-20261113'],
            [has('google-ads-political-search-nvidia-20261113', 'typed "Nvidia": [nothing offered]'), has('google-ads-political-search-nvidia-20261113', 'typed "Public First Action": Public First Action Inc ~20 ads')])
        oth = [r for r in pacs[who[m]['bioguide']] if r['pac'] not in ('anthropic', 'nvidia')]
        if oth:
            tie(m, 'nvidia', 'other_pacs', 'G', 'Other companies\' own PACs',
                '; '.join(f'{r["pac"].upper() if len(r["pac"]) == 3 else r["pac"].title()} {money(float(r["net_usd"]))} ({day(r["first_date"])})' for r in oth)
                + f'. These are those companies\' own committees, from this project\'s table of {NUM[len(base) - 1]} technology companies\' PACs other than AnthroPAC, which is counted above; they are not ties to Nvidia.',
                [f'table:pacs_by_member.csv#{r["key"]}' for r in oth], [r['net_usd'] for r in oth], audit='B-23 V3-CT19 B3-20')
        # ===== looked for, none found
        x = {'mast': 'MS1338', 'moolenaar': 'MS1432', 'crawford': 'MS1264'}[m]; acct = {'mast': 'RepBrianMast', 'moolenaar': 'RepMoolenaar', 'crawford': 'RepRickCrawford'}[m]
        tie(m, 'searched', 'x_posts', 'O', '',
            'A post from his official X account since Jan 2025 using any of eleven search terms, among them Anthropic, Open Philanthropy, Public First, Horizon Institute and Amodei: '
            'the evidence set records none found on Sep 16, 2026. The search responses themselves were not saved.',
            f'pack:congress/research/member_statements.csv#{x}', f'none found in from:{acct}', audit='gap TX')
        if m == 'crawford':
            tie(m, 'searched', 'pfa_ad', 'O', '',
                'An ad by Public First Action naming him: Google\'s report lists two entries by the group aimed at Arkansas (Jul 2026); frames of both name Sen. Tom Cotton, not him.',
                ['google-ads-creative-ar-20261113', 'google-ads-creative-ar2-20261113'], [has('google-ads-creative-ar-20261113', 'CALL TOM COTTON'), has('google-ads-creative-ar2-20261113', 'CALL TOM COTTON')])
        for side in ('anthropic', 'network', 'nvidia'):
            rs = lob(side, m)
            num(f'lob:{side}:{m}:total', f'{sum(float(r["amount_usd"]) for r in rs):.0f}', f'gifts naming {last} from lobbyists or PACs of firms registered for {side}'
                + (f' (of it {sum(float(r["amount_usd"]) for r in committee_lines(rs)):.0f} a campaign committee\'s contribution that a lobbyist\'s report lists)' if committee_lines(rs) else ''))
            assert not committee_lines(rs) or (side, m) == ('network', 'mast'), ('a committee\'s line on a side whose panel does not say so', side, m)
            num(f'lob:{side}:{m}:named', f'{sum(float(r["amount_usd"]) for r in rs if r["measure"] == "named"):.0f}', 'of which from lobbyists listed for the client')
            num(f'lob:{side}:{m}:items', len(rs), 'gifts')

    # ---- numbers across the three and across Congress
    num('trade:nvidia:three', f'{sum(float(x["usd"]) for x in TG if x["group"] in ("sia", "iti")):.0f}', 'gifts to the three from PACs of trade groups that list Nvidia and not Anthropic')
    num('trade:technet:three', f'{sum(float(x["usd"]) for x in TG if x["group"] == "technet"):.0f}', 'gifts to the three from the PAC of TechNet, which lists both companies')
    for g_ in lists:
        num(f'trade:{g_}:members', lists[g_]['members'], f'members on {lists[g_]["name"]}\'s list as saved', lists[g_]['pid'], f'({lists[g_]["members"]} names;')
        num(f'trade:{g_}:candidates', lists[g_]['candidates'], f'candidates the PAC of {lists[g_]["name"]} gave to, 2026 cycle')
    a_all = sum(float(g['usd']) for g in gifts if g['side'] == 'anthropic')
    win = sum(float(g['usd']) for g in gifts if g['side'] == 'anthropic' and '2026-04-29' <= g['date'] <= '2026-05-20')
    num('emp:anthropic:three', f'{a_all:.0f}', 'Anthropic employees\' gifts to committees tied to the three chairmen')
    num('emp:anthropic:three:window', f'{win:.0f}', 'of which dated Apr 29 to May 20, 2026')
    for side in ('anthropic', 'network', 'nvidia'):
        num(f'lob:{side}:three', f'{sum(float(r["amount_usd"]) for r in LG if r["side"] == side and r["measure"] != "own_pac"):.0f}', f'lobbyists\' and firm PACs\' gifts to the three, firms registered for {side}')
    # how common an Anthropic or Nvidia employee's gift is across all sitting members, with ties in rank shown as ties
    allg = table('employee_gifts.csv'); bg = {who[m]['bioguide']: m for m in THREE}
    for side in ('anthropic', 'nvidia'):
        by = Counter()
        for g_ in allg:
            if g_['side'] == side:
                by[g_['bioguide']] += float(g_['usd'])
        assert len(by) == int(rates[side]['members_with_a_gift']) and abs(sum(by.values()) - float(rates[side]['usd'])) < 1
        num(f'rate:{side}:members', len(by), f'sitting members with a gift from someone who gave {side.title()} as employer, since Jan 2025', f'table:employee_gift_rates.csv#{side}', rates[side]['members_with_a_gift'])
        num(f'rate:{side}:usd', f'{sum(by.values()):.0f}', 'dollars in those gifts')
        ind = len(by) - int(rates[side]['democrats']) - int(rates[side]['republicans'])
        num(f'rate:{side}:parties', f'{rates[side]["democrats"]} Democrats, {rates[side]["republicans"]} Republicans, {ind} independent{"s" if ind != 1 else ""}', 'by party')
        if side == 'anthropic':
            for b, m in bg.items():
                more = sum(1 for v in by.values() if v > by[b]); same = sum(1 for v in by.values() if v == by[b])
                num(f'rank:{m}', ('joint ' if same > 1 else '') + f'{more + 1}', f'rank by dollars among the {len(by)} (members with more: {more}; with the same: {same - 1})')
    pf = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', (P / 'art-pfa-conservative' / 'body.html').read_text(errors='replace')))    # the page's list, from its saved HTML
    i0 = pf.index('highlighting the strong records of 12 Republican members of Congress')
    listed = sorted(set(re.findall(r"(Rep\. [A-Z][A-Za-z.' -]+?) ?, ([A-Z]{2}-\d{2})", pf[i0:i0 + 1500])))
    assert len(listed) == 11 and ('Rep. Brian Mast', 'FL-21') in listed and ('Rep. John Moolenaar', 'MI-02') in listed and not [x for x in listed if 'Crawford' in x[0]], listed
    num('pfa_page_members', len(listed), 'House members listed on Public First Action\'s announcement of Jul 17, 2026 (it speaks of 12)', 'art-pfa-conservative', 'highlighting the strong records of 12 Republican members of Congress')
    # the two frames of each ad that the panels show, copied as saved (the figure crops them to the video)
    import shutil
    FR = R / 'nv13_frames'; FR.mkdir(exist_ok=True)
    for m, pid in (('mast', 'google-ads-creative-fl21-20261113'), ('moolenaar', 'google-ads-creative-mi2-20261113')):
        for n, tag in (('03', 'backing'), ('06', 'call')):
            shutil.copyfile(P / pid / f'frame-{n}.png', FR / f'{m}-{tag}.png')
    num('pac:anthropic:members', base['anthropic']['sitting_members_with_net_above_zero'], 'sitting members with money from AnthroPAC', 'table:pac_base_rates.csv#anthropic', base['anthropic']['sitting_members_with_net_above_zero'])
    num('pac:anthropic:usd', f'{float(base["anthropic"]["usd_to_sitting_members"]):.0f}', 'dollars from AnthroPAC to sitting members')
    num('pac:anthropic:through', base['anthropic']['latest_line'], 'date of the latest AnthroPAC line counted')
    num('pac:nvidia:members', base['nvidia']['sitting_members_with_net_above_zero'], 'sitting members with money from Nvidia\'s employee PAC', 'table:pac_base_rates.csv#nvidia', base['nvidia']['sitting_members_with_net_above_zero'])
    num('lob:nvidia:mast:window', f'{sum(float(r["amount_usd"]) for r in LG if r["side"] == "nvidia" and r["member"] == "mast" and "2025-11-17" <= r["date"] <= "2025-12-31"):.0f}',
        'gifts naming Mast from lobbyists and a PAC at Nvidia\'s firms dated Nov 17 to Dec 31, 2025')
    PA = P / 'fec-bulk-pas226-20261112'
    cm = {l.split('|')[0]: l.split('|')[1] for l in zipfile.ZipFile(PA / 'cm26.zip').read('cm.txt').decode('latin-1').splitlines()}
    ari = sorted(k for k, v in cm.items() if 'RESPONSIBLE INNOVATION' in v)
    assert ari == ['C00873356', 'C00893883'], ari
    lines = [l.split('|') for l in zipfile.ZipFile(PA / 'pas226.zip').read('itpas2.txt').decode('latin-1').splitlines() if l.split('|')[0] in ari and l.split('|')[5] in ('24K', '24Z')]
    cand = Counter()
    for l in lines:
        cand[l[16]] += float(l[14])
    assert cand[CAND['mast']] == 2500 and cand[CAND['crawford']] == 1000 and CAND['moolenaar'] not in cand
    num('ari_pac_candidates', sum(1 for v in cand.values() if v > 0), 'candidates whose campaign committees ARI\'s PACs gave to, Feb 2025 to Sep 2026 (FEC committee-to-candidate file)')
    num('ari_pac_usd', f'{sum(cand.values()):.0f}', 'dollars in those gifts')
    ga = [r for r in csv.DictReader(open(P / 'google-political-ads-pfa-20260916' / 'creative-stats.csv', newline='', errors='replace')) if r['Advertiser_Name'] == 'Public First Action Inc']
    num('pfa_google_entries', len(ga), 'ad entries by Public First Action in Google\'s political-ads report (saved Sep 16, 2026)', 'google-political-ads-pfa-20260916', 'Public First Action Inc')

    # ---- who is who (the second version's lines, corrected where the audit asked)
    L = {r['id']: r for r in table('nv13_links.csv')}
    FIX = {
        'article': ('An article on X on Nov 12, 2026 said "Anthropic\'s people overlap with the think tanks, ex-officials and forums behind this coverage."',
                    'An article on X on Nov 12, 2026 alleged that "Anthropic\'s people overlap with the think tanks, ex-officials and forums behind this coverage."', [], [], 'B-04 A-TL01'),
        'clark': ('A co-founder of Anthropic and its head of policy.', 'Listed as Anthropic\'s co-founder and head of policy on his testimony of Jun 2025.',
                  ['house-hrg-zs00-20250625-clark-statement'], ['Co-Founder and Head of Policy, Anthropic'], 'B-30 A-TL06'),
        'op_1': ('Dustin Moskovitz, one of its directors, invested in Anthropic\'s Series A funding round in 2021.',
                 'Dustin Moskovitz, listed as a director on its 2024 tax return, took part in Anthropic\'s Series A funding round in 2021. The records do not show what he holds now.', [], [], 'B-05 A-TL10'),
        'horizon': ('Places fellows in congressional offices and committees. $11.8M in 2023 from Good Ventures Foundation, which Open Philanthropy\'s tax return lists as a related organisation.',
                    'Places fellows in congressional offices and committees. Good Ventures Foundation, which Open Philanthropy\'s tax return lists as a related organisation, reported paying it $11.8M in its fiscal year ending Jun 2023.',
                    ['pack:lineage/research/flows_named.csv#FN1133'], ['FY 2022-07-01..2023-06-30'], 'B-06 B-07 A-TL14'),
        'cais': ('$12.5M in awards, 2022–23.', '$12.5M in awards, 2022–23, the last of them a $1.9M exit grant in Oct 2023.', ['pack:lineage/research/flows_named.csv#FN107'], ['General Support (Exit Grant)'], 'B-08 A-TL16'),
        'cnas': ('$14.6M in awards, 2017–25. Its chief executive, Richard Fontaine, was named in Jun 2025 to the trust that will elect most of Anthropic\'s board.',
                 '$14.6M in awards, 2017–25. Its chief executive, Richard Fontaine, was named in Jun 2025 to Anthropic\'s Long-Term Benefit Trust, which Anthropic describes as "an independent body of five financially disinterested members" '
                 '(its page lists four trustees as of Oct 2026). The trust is to elect most of Anthropic\'s board; Anthropic says that power will "phase in according to time- and funding-based milestones", '
                 'and that large enough majorities of stockholders can change the trust\'s powers without the trustees\' consent.',
                 ['anthropic-ltbt'] * 4,
                 ['The Trust is an independent body of five financially disinterested members', has('anthropic-ltbt', 'phase in according to time- and funding-based milestones'),
                  has('anthropic-ltbt', 'allow changes to the Trust and its powers without the consent of the Trustees if sufficiently large supermajorities of the stockholders agree'),
                  has('anthropic-ltbt', 'As of October 2026, the current Trustees are')], 'B-09 A-TL17 V3-CK18 B3-13'),
        'op': ('A grant-maker, now called Coefficient Giving. It is a separate organisation from Anthropic. Three records link the two:',
               'A grant-maker, renamed Coefficient Giving in Nov 2025. It is a separate organisation from Anthropic, with its own tax return. Three records link the two:',
               ['pack:congress/research/timeline.csv#TL068', 'pack:congress/research/timeline.csv#TL332'], ['Open Philanthropy renamed Coefficient Giving', 'Open Philanthropy EIN 81-0737472'], 'V3-CK10 B3-14'),
        'carnegie': ('$2.4M in awards, 2015–26.', '$2.4M in awards, 2015–26, for several subjects: three of the seven are for research on AI (2022 and 2025).', [], [], 'report part E'),
        'fai': ('$3.7M in awards, 2023–26.', '$3.7M in awards, 2023–26: $976,000 for AI policy (the 2024 award is an exit grant) and $2.7M in 2026 for energy permitting.', [], [], 'B-10 A-TL19'),
        'opaf': ('A related body with the same president as Open Philanthropy. It hires lobbying firms.',
                 'Listed as a related organisation on Open Philanthropy\'s 2024 tax return; both 2024 returns list the same president. It hires lobbying firms.', [], [], 'B-11 A-TL20'),
    }
    g = pack('congress/research/grants.csv')
    tlp = pack('congress/research/timeline.csv'); assert tlp['TL068']['date'] == '2025-11' and 'EIN 81-0737472' in tlp['TL332']['note']
    cg = [g[i] for i in ('GR026', 'GR027', 'GR028', 'GR029', 'GR030', 'GR031', 'GR032')]
    assert [r['purpose'] for r in cg if 'AI' in r['purpose']] == ['AI Governance Research', 'AI Governance Research', 'Frontier AI and Geopolitics Research'] and sorted({r['date'][:4] for r in cg if 'AI' in r['purpose']}) == ['2022', '2025']
    lt = text('anthropic-ltbt'); seg = lt[lt.index('As of October 2026, the current Trustees are'):][:700]; seg = seg[:seg.index('and Dr. Christopher Stubbs')]
    assert 'Richard Fontaine' in seg and seg.count(';') == 3, seg[:400]            # four names: three before the closing "and", separated by semicolons
    assert [g[i]['purpose'] for i in ('GR044', 'GR045', 'GR046')] == ['AI Safety Policy Advocacy', 'AI Safety Policy Research and Advocacy (Exit Grant)', 'Energy Permitting Reforms']
    assert float(g['GR044']['amount_usd']) + float(g['GR045']['amount_usd']) == 976000 and float(g['GR046']['amount_usd']) == 2714000
    fn = pack('lineage/research/flows_named.csv'); assert fn['FN107']['amount_usd'] == '1866559' and fn['FN107']['date'] == '2023-10-04'
    for i, r in L.items():
        src, q = r['src'].split(' || '), r['q'].split(' || '); words, audit = r['words'], ''
        if i in FIX:
            old, new, s2, q2, audit = FIX[i]
            assert words == old, (i, words)
            words = new; src += s2; q += q2
            if i == 'fai':
                q = ['AI Safety Policy Advocacy', 'AI Safety Policy Research and Advocacy (Exit Grant)', 'Energy Permitting Reforms'] if len(q) == 3 else q
        KEY.append({'id': i, 'card': r['card'], 'label': r['label'], 'words': words, 'audit': audit, 'src': ' || '.join(src), 'q': ' || '.join(q)})
        if i == 'pfa_carson':
            sp = pack('congress/research/super_pac_c4.csv')
            assert 'none_found' == sp['SP430']['source_type'] and sp['SP430']['date'] == '2026-09-16'
            # Who funds it. The group's own announcement of Jun 30, 2026 gives a total and names no donor (the saved copy was read whole;
            # the control is that the one donor known from elsewhere, Anthropic, is not named in it either). Its one FEC filing reports no donations.
            assert sp['SP053']['date'] == '2026-02-12' and sp['SP054']['date'] == '2026-07-21' and 'Anthropic' not in text('art-pfa-80m-release')
            fl = json.loads((P / 'fec-filings-c30003586-20261114' / 'page-001.json').read_text())
            assert fl['pagination']['count'] == 1 and fl['results'][0]['form_type'] == 'F9' and fl['results'][0]['total_receipts'] == 0.0 and fl['results'][0]['receipt_date'][:10] == '2026-03-10'
            KEY.append({'id': 'pfa_donors', 'card': 'pfa', 'label': '', 'audit': '',
                        'words': 'Anthropic is the only donor the saved records identify: a search on Sep 16, 2026 found no other organisation naming itself as one. '
                                 'On Jun 30, 2026 the group said it had raised more than $80 million, and its announcement named no donor; Anthropic had by then announced $20 million of its $40 million. '
                                 'The FEC lists one filing by the group, a notice of spending on an ad in Mar 2026: it names no donor, and it is not an account of the group\'s funding.',
                        'src': ' || '.join(['pack:congress/research/super_pac_c4.csv#SP053', 'pack:congress/research/super_pac_c4.csv#SP054', 'pack:congress/research/super_pac_c4.csv#SP430',
                                            'art-pfa-80m-release', 'art-pfa-80m-release', 'fec-filings-c30003586-20261114', 'fec-filings-c30003586-20261114']),
                        'q': ' || '.join(['Anthropic is contributing $20 million', 'bringing our total support to $40 million', 'Public First Action donor OR donated -site:anthropic.com',
                                          has('art-pfa-80m-release', 'has raised more than $80 million to date'), has('art-pfa-80m-release', 'PUBLISHED: 2026-06-30'),
                                          has('fec-filings-c30003586-20261114', 'document_description: 24 HOUR NOTIFICATION 2026'), has('fec-filings-c30003586-20261114', 'filings listed: 1 (pages: 1)')])})
            # The chief executive's own gift went to a super PAC with a similar name, which the FEC lists as a separate committee; the group itself gave that committee money.
            assert sp['SP062']['payer'] == 'PUBLIC FIRST ACTION INC.' and sp['SP062']['payee'] == 'PUBLIC FIRST' and sp['SP062']['date'] == '2026-02-24' and float(sp['SP062']['amount_usd']) == 1000000
            assert sp['SP104']['payee'] == 'PUBLIC FIRST' and sp['SP104']['date'] == '2026-05-04' and float(sp['SP104']['amount_usd']) == 1000000 and 'AMODEI, DARIO' in sp['SP104']['quote_300']
            oth = [sp[i] for i in ('SP409', 'SP410', 'SP411', 'SP412', 'SP413')]
            assert all(r['payee'] == 'PUBLIC FIRST' and r['payer_type'] == 'individual' and r['date'].startswith('2026-06') for r in oth) and len({r['payer'] for r in oth} | {sp['SP104']['payer']}) == 6
            assert sum(float(r['amount_usd']) for r in oth) == 2154900
            KEY.append({'id': 'pfa_ceo', 'card': 'pfa', 'label': '', 'audit': 'B4-07',
                        'words': 'Anthropic\'s chief executive, Dario Amodei, gave $1 million of his own on May 4, 2026 to Public First, a super PAC: a separate committee, to which the group itself gave $1 million on Feb 24, 2026. '
                                 'Five other people who gave Anthropic as employer gave that committee $2,154,900 in Jun 2026. None of this identifies a donor to the group, and the ads shown in the panels are the group\'s.',
                        'src': ' || '.join(['pack:congress/research/super_pac_c4.csv#SP104', 'pack:congress/research/super_pac_c4.csv#SP058', 'pack:congress/research/super_pac_c4.csv#SP062']
                                           + ['pack:congress/research/super_pac_c4.csv#' + r['row_id'] for r in oth]),
                        'q': ' || '.join(['AMODEI, DARIO', 'gave $1 million in May to Public First, a super PAC', 'PUBLIC FIRST ACTION INC.'] + [r['amount_usd'] for r in oth])})
    KEY.append({'id': 'times', 'card': 'context', 'label': '', 'audit': 'B3-18',
                'words': 'The letters followed a New York Times report of Oct 29, 2026, headlined "Nvidia Chief, Jensen Huang, Is Seen as Target of Chinese Spy Plot"; Nvidia told the Times his meetings with a customer\'s executive were "not unusual or unexpected".',
                'src': ' || '.join(['man-nyt-1029-01'] * 3),
                'q': ' || '.join([has('man-nyt-1029-01', 'Nvidia Chief, Jensen Huang, Is Seen as Target of Chinese Spy Plot'), has('man-nyt-1029-01', 'PUBLISHED: 2026-10-29'), has('man-nyt-1029-01', 'are not unusual or unexpected')])})
    KEY.append({'id': 'times_more', 'card': 'context', 'label': '', 'audit': 'B3-18',
                'words': 'The Times report also carries Nvidia\'s statement that such customers receive "zero information relevant to national security" and that it had "investigated and debunked" claims that the customer was smuggling chips, '
                         'and says that when the president was first briefed, "U.S. officials did not believe the Nvidia executive knew" of the intelligence gathering the report describes. '
                         'It adds: "It is unclear whether intelligence officials have since updated their assessment, but some senior officials inside the Trump administration doubt that Mr. Huang could have remained unaware".',
                'src': ' || '.join(['man-nyt-1029-01'] * 4),
                'q': ' || '.join([has('man-nyt-1029-01', 'zero information relevant to national security'), has('man-nyt-1029-01', 'previously investigated and debunked claims'),
                                  has('man-nyt-1029-01', 'U.S. officials did not believe the Nvidia executive knew'),
                                  has('man-nyt-1029-01', 'It is unclear whether intelligence officials have since updated their assessment, but some senior officials inside the Trump administration doubt that Mr. Huang could have remained unaware')])})
    fl = [g[i] for i in ('GR053', 'GR054', 'GR055', 'GR056', 'GR057', 'GR058')]
    assert all(r['payer'] == 'Coefficient Giving' and r['payee'] == 'Future of Life Institute' for r in fl) and sum(float(r['amount_usd']) for r in fl) == 1912000
    KEY.append({'id': 'fli', 'card': 'op_group', 'label': 'Future of Life Institute', 'words': '$1.9M in awards, 2015–20.', 'audit': '',
                'src': ' || '.join('pack:congress/research/grants.csv#' + r['row_id'] for r in fl), 'q': ' || '.join('Future of Life Institute' for r in fl)})

    # ---- the stake: what each company makes, where each is heading, where they have clashed
    def stake(i, card, label, words, src, q):
        src = [src] if isinstance(src, str) else src; q = [q] if isinstance(q, str) else q
        STAKE.append({'id': i, 'card': card, 'label': label, 'words': words, 'src': ' || '.join(src),
                      'q': ' || '.join(x if s.startswith(('table:', 'pack:')) else has(s, x) for s, x in zip(src, q))})      # a table or pack row is checked by check_rows.py
    assert bills['hr6875']['latest_action'].startswith('Ordered to be Reported') and bills['hr5885']['latest_action'] == 'Referred to the House Committee on Foreign Affairs.'
    stake('nv_chips', 'nvidia', 'Chips', 'It sells AI chips, and two of the chairmen have bills on their export. Mast\'s, his committee says, "applies long-standing congressional oversight to exports of America\'s sensitive, military-enhancing AI chips"; '
          'it has passed his committee and no further, and Moolenaar\'s has not left committee. Mast, in the release of Jan 21, 2026: "Companies like Nvidia are requesting to sell millions of advanced AI chips, '
          'which are the cutting edge of warfare, to Chinese military companies like Alibaba and Tencent."',
          ['art-hfac-overwatch-advances', 'art-hfac-overwatch-advances', 'table:chip_bills.csv#hr6875', 'table:chip_bills.csv#hr5885'],
          ['Companies like Nvidia are requesting to sell millions of advanced AI chips', "applies long-standing congressional oversight to exports of America's sensitive, military-enhancing AI chips",
           'Ordered to be Reported in the Nature of a Substitute by the Yeas and Nays: 42 - 2.', 'Referred to the House Committee on Foreign Affairs.'])
    stake('nv_models', 'nvidia', 'Now also AI models', 'It also releases open AI models, with data and tools. Its release of Dec 15, 2025: "NVIDIA is the first to release a collection of state-of-the-art open models, '
          'training datasets and reinforcement learning environments and libraries"; the same release describes developers using open models alongside "proprietary models for state-of-the-art reasoning". '
          'A trade report of Oct 16, 2026 says its newest models show it "reinforcing its own GPU infrastructure while supporting the open source community."',
          ['art-nvidia-nemotron3-release', 'art-nvidia-nemotron3-release', 'art-nvidia-nemotron3-release', 'art-techtarget-nvidia-open-models', 'art-techtarget-nvidia-open-models'],
          ['NVIDIA is the first to release a collection of state-of-the-art open models, training datasets and reinforcement learning environments and libraries', 'December 15, 2025',
           'proprietary models for state-of-the-art reasoning', 'reinforcing its own GPU infrastructure while supporting the open source community', '2026-10-16'])
    stake('nv_gain', 'nvidia', 'On the Senate\'s bill', 'TechSpot, Sep 4, 2025: "Nvidia has since posted a statement opposing the GAIN AI Act. The company says it is comparable to the Biden-era AI Diffusion Rule that was rescinded in May, and part of an attempt to overturn Trump\'s AI Action Plan". '
          'It also reported Nvidia\'s statement "that H20 sales have not reduced its supply of H100, H200, or Blackwell GPUs". '
          'Of that rule Huang had said, as Fortune quoted him on May 2, 2025: "the U.S. semiconductor industry is being pushed out of China, the world\'s largest market."',
          ['art-techspot-gain', 'art-techspot-gain', 'art-fortune-nvidia-tall-tales', 'art-fortune-nvidia-tall-tales', 'art-techspot-gain'],
          ["Nvidia has since posted a statement opposing the GAIN AI Act. The company says it is comparable to the Biden-era AI Diffusion Rule that was rescinded in May, and part of an attempt to overturn Trump's AI Action Plan", '2025-09-04',
           "the U.S. semiconductor industry is being pushed out of China, the world's largest market", 'PUBLISHED: 2025-05-02',
           'Nvidia posted a message on X stating that H20 sales have not reduced its supply of H100, H200, or Blackwell GPUs'])
    stake('an_models', 'anthropic', 'AI models', 'It makes the Claude AI models and runs them on other companies\' chips: "Currently, Anthropic uses a large number of chips, including Nvidia and AMD GPUs, Google TPUs, and Amazon Trainium hardware" '
          '(Data Center Dynamics, Aug 6, 2026).', ['art-dcd-anthropic-chip-team', 'art-dcd-anthropic-chip-team'], ['Currently, Anthropic uses a large number of chips, including Nvidia and AMD GPUs, Google TPUs, and Amazon Trainium hardware', 'August 06, 2026'])
    stake('an_chips', 'anthropic', 'Now also a chip-design team', 'In Aug 2026 its spokesperson confirmed "that the company was building an in-house silicon team to design custom chips for Claude", calling it "the latest step in our multi-chip approach" '
          'and saying the company would continue deploying a "diversified hardware stack". The report is of a design team: it does not describe finished chips, or chips for sale.',
          ['art-dcd-anthropic-chip-team', 'art-dcd-anthropic-chip-team', 'art-dcd-anthropic-chip-team'],
          ['confirmed that the company was building an in-house silicon team to design custom chips for Claude', 'the latest step in our multi-chip approach', 'and that the company would continue deploying a "diversified hardware stack."'])
    stake('an_controls', 'anthropic', 'On export controls', 'It asks for tighter limits on chip exports. Its co-founder to Moolenaar\'s committee on Jun 25, 2025, before either House bill was introduced: the government should be '
          '"maintaining and strengthening export controls of advanced semiconductors to China". That is its general position, not a statement on either bill.',
          ['house-hrg-zs00-20250625-clark-statement', 'table:chip_bills.csv#hr5885', 'table:chip_bills.csv#hr6875'], ['maintaining and strengthening export controls of advanced semiconductors to China', '2025-10-31', '2025-12-18'])
    # the second audit's addendum: Anthropic's own statement that the policies it backs are not for its benefit, attributed like Nvidia's statements
    stake('an_denial', 'anthropic', 'Its own account', 'Announcing its first gift to Public First Action on Feb 12, 2026, it said of the policies it backs: "Nor are they for the benefit of Anthropic as an AI developer—effective AI governance '
          'means more scrutiny of companies like ours, not less." That is the company\'s statement; no record here tests it.',
          ['anthropic-pfa-1', 'anthropic-pfa-1'], ['Nor are they for the benefit of Anthropic as an AI developer-effective AI governance means more scrutiny of companies like ours, not less.', 'PUBLISHED: 2026-02-12'])
    stake('clash', 'clash', 'May 1, 2025', 'After Anthropic argued for tighter controls and described chip smuggling, an Nvidia spokesperson said American firms should "rise to the challenge, rather than tell tall tales that large, heavy, '
          'and sensitive electronics are somehow smuggled in \'baby bumps\' or \'alongside live lobsters,\'" and: "America cannot manipulate regulators to capture victory in AI."',
          ['art-nbc-nvidia-tall-tale', 'art-nbc-nvidia-tall-tale', 'art-nbc-nvidia-tall-tale'],
          ["rise to the challenge, rather than tell tall tales that large, heavy, and sensitive electronics are somehow smuggled in 'baby bumps' or 'alongside live lobsters,'", 'America cannot manipulate regulators to capture victory in AI', '2025-05-01'])
    stake('reply', 'clash', '', 'Anthropic\'s spokesperson replied: "National security is bigger than the interest of any single company. Anthropic stands by its recently filed public submission in support of strong and balanced export controls".',
          'art-fortune-nvidia-tall-tales', 'National security is bigger than the interest of any single company. Anthropic stands by its recently filed public submission in support of strong and balanced export controls')
    stake('stock', 'clash', 'Also partners', 'Reported on Nov 10, 2026: Anthropic said seven companies, Nvidia among them, had agreed to buy $26 billion of its stock between them, in a private sale at the price of its public offering. '
          'Nvidia\'s own share is not given. Anthropic also runs Claude partly on Nvidia chips.',
          ['cnbc-1110-anthropic-ipo', 'cnbc-1110-anthropic-ipo', 'art-dcd-anthropic-chip-team'],
          ['Nvidia and Taiwan Semiconductor Manufacturing Co. to purchase $26 billion', 'in a private placement at a price per share equal to the IPO price', 'including Nvidia and AMD GPUs'])

    # ---- dated public events for the timeline
    import rows_ties
    TE = {(e[0], e[1], e[2]): e for e in rows_ties.EVENTS}

    def ev(lane, d, kind, words, src, q, end=''):
        src = [src] if isinstance(src, str) else src; q = [q] if isinstance(q, str) else q
        EVENTS.append({'lane': lane, 'date': d, 'end': end, 'kind': kind, 'words': words, 'src': ' || '.join(src), 'q': ' || '.join(q)})
    old = lambda lane, d, w: (TE[(lane, d, w)][3], TE[(lane, d, w)][4])
    assert bills['s4456']['introduced'] == '2026-04-30' and bills['hr3447']['latest_action_date'] == '2026-03-26' and '42 - 0' in bills['hr3447']['latest_action']
    assert bills['hr8170']['latest_action_date'] == '2026-04-22' and '36 - 8' in bills['hr8170']['latest_action']
    ev('all', '2025-05-01', 'clash', 'Nvidia: Anthropic tells "tall tales"', 'art-nbc-nvidia-tall-tale', has('art-nbc-nvidia-tall-tale', 'tall tales'))
    ev('all', '2025-09-04', 'clash', 'Report: Nvidia opposes the Senate\'s GAIN AI Act', 'art-techspot-gain', has('art-techspot-gain', 'Nvidia has since posted a statement opposing the GAIN AI Act'))
    ev('all', '2026-04-30', 'bill', 'Senate version of Mast\'s bill introduced', 'table:chip_bills.csv#s4456', '2026-04-30')
    ev('all', '2026-02-12', 'money', 'Anthropic announces $20 million for Public First Action', ['anthropic-pfa-1', 'anthropic-pfa-1'],
       [has('anthropic-pfa-1', 'Anthropic is contributing $20 million to Public First Action'), has('anthropic-pfa-1', 'PUBLISHED: 2026-02-12')])
    ev('all', '2026-07-21', 'money', 'Anthropic announces another $20 million for Public First Action', ['anthropic-pfa-2', 'anthropic-pfa-2'],
       [has('anthropic-pfa-2', 'bringing our total support to $40 million'), has('anthropic-pfa-2', 'PUBLISHED: 2026-07-21')])
    ev('all', '2026-08-06', 'clash', 'Anthropic confirms a chip-design team', 'art-dcd-anthropic-chip-team', has('art-dcd-anthropic-chip-team', 'August 06, 2026'))
    ev('all', '2026-10-29', 'press', 'Times report on Huang', *old('all', '2026-10-29', 'First Times report'))
    ev('all', '2026-11-05', 'letter', 'The three ask Huang to brief them', *old('all', '2026-11-05', 'Three chairmen ask Huang to brief them'))
    ev('all', '2026-11-12', 'letter', 'Their letter: interview on Dec 1, or a subpoena', ['x-chinaselect-letter-image', 'x-chinaselect-letter-image'],
       [has('x-chinaselect-letter-image', 'we request that you appear for a closed-door, transcribed interview on December 1, 2026'), has('x-chinaselect-letter-image', 'or a subpoena will be issued')])
    EVENTS[-1]['src'] += ' || x-chinaselect-letter-image'; EVENTS[-1]['q'] += ' || ' + has('x-chinaselect-letter-image', "We appreciated the conversation with NVIDIA staff yesterday regarding our committees' request.")
    ev('moolenaar', '2025-06-25', 'hearing', 'Anthropic\'s co-founder testifies to his committee', 'house-hrg-zs00-20250625-transcript', 'STATEMENT OF MR. JACK CLARK')
    ev('moolenaar', '2025-10-31', 'bill', 'Introduces H.R. 5885 (GAIN AI Act)', *old('moolenaar', '2025-10-31', 'Introduces H.R. 5885'))
    ev('moolenaar', '2025-12-18', 'bill', 'Original cosponsor of Mast\'s bill', *old('moolenaar', '2025-12-18', 'Original cosponsor of H.R. 6875'))
    ev('moolenaar', '2026-07-17', 'ad', 'Ads announced', *old('moolenaar', '2026-07-17', 'Ads praising his record announced'))
    ev('moolenaar', '2026-08-05', 'adrun', 'Ad naming him runs', *old('moolenaar', '2026-08-05', 'Public First Action ad naming him starts'), end='2026-08-25')
    ev('mast', '2025-12-18', 'bill', 'Introduces H.R. 6875 (AI OVERWATCH Act)', *old('mast', '2025-12-18', 'Introduces H.R. 6875'))
    ev('mast', '2026-01-21', 'bill', 'His committee approves it, 42–2', *old('mast', '2026-01-21', 'His committee approves it, 42–2'))
    ev('mast', '2026-03-26', 'bill', 'His committee approves the Chip Security Act, 42–0', 'table:chip_bills.csv#hr3447', 'Ordered to be Reported in the Nature of a Substitute by the Yeas and Nays: 42 - 0.')
    ev('mast', '2026-04-22', 'bill', 'His committee approves the MATCH Act, 36–8', 'table:chip_bills.csv#hr8170', 'Ordered to be Reported in the Nature of a Substitute (Amended) by the Yeas and Nays: 36 - 8.')
    ev('mast', '2026-07-17', 'ad', 'Ads announced', *old('mast', '2026-07-17', 'Ads praising his record announced'))
    ev('mast', '2026-08-19', 'adrun', 'Ad naming him runs', *old('mast', '2026-08-19', 'Public First Action ad naming him starts'), end='2026-09-02')
    ev('crawford', '2025-11-18', 'bill', 'Cosponsors H.R. 5885', *old('crawford', '2025-11-18', 'Cosponsors H.R. 5885'))
    ev('crawford', '2025-12-18', 'bill', 'Original cosponsor of Mast\'s bill', *old('crawford', '2025-12-18', 'Original cosponsor of H.R. 6875'))

    # ---- at a glance: one line per kind of record, one column per chairman
    T = lambda m, sec, typ: [t for t in TIES if t['member'] == m and t['section'] == sec and t['type'].startswith(typ)]
    N = {n['key']: n['value'] for n in NUMS}
    usd = lambda v: money(float(v)) if float(v) else '–'
    G = []

    def glance(group, label, f, note=''):
        G.append({'group': group, 'label': label, 'mast': f('mast'), 'moolenaar': f('moolenaar'), 'crawford': f('crawford'), 'note': note})
    glance('anthropic', 'Its employees\' own gifts', lambda m: f'{usd(N[f"emp:anthropic:{m}"])} · {N[f"emp_people:anthropic:{m}"]} {"people" if int(N[f"emp_people:anthropic:{m}"]) > 1 else "person"}')
    glance('anthropic', 'AnthroPAC, its political committee', lambda m: usd(next((t['usd'] for t in T(m, 'anthropic', 'company_pac') if t['usd']), 0)))
    glance('anthropic', 'Its lobbying reports naming a chip bill he sponsors', lambda m: next((f'{o["n"].split("/")[0]} report{"s" if o["n"].split("/")[0] != "1" else ""}' for o in TY if o['member'] == m and o['type'].startswith('lobbying')), '– (cosponsors both)'))
    glance('anthropic', 'Its co-founder testifying to his committee', lambda m: 'Jun 25, 2025' if T(m, 'anthropic', 'witness') else '–')
    glance('anthropic', 'Gifts from lobbyists at its firms', lambda m: usd(N[f'lob:anthropic:{m}:total']))
    glance('anthropic', 'PACs of trade groups that list it and not Nvidia', lambda m: '– (none found)')
    glance('pfa', 'An ad naming him, by Public First Action', lambda m: next((span([t['first'], t['last']]) for t in T(m, 'pfa', 'ad_run')), '– (its Arkansas ads name Sen. Cotton)'))
    glance('network', 'ARI\'s PAC', lambda m: next((usd(t['usd']) + (' (to a joint committee)' if 'joint' in t['words'] else '') for t in T(m, 'network', 'ari_pac')), '–'))
    glance('network', 'Fellows, advisers and former staff', lambda m: (lambda n: f'{n} record{"s" if n != 1 else ""}' if n else '–')(len(T(m, 'network', 'fellow') + T(m, 'network', 'advisor') + T(m, 'network', 'left') + T(m, 'network', 'aide'))))
    glance('network', 'Witnesses listed for his committee\'s hearings', lambda m: '6 people' if T(m, 'network', 'net_witness') else '–')
    glance('network', 'Gifts reported by lobbyists and PACs of their firms', lambda m: usd(N[f'lob:network:{m}:total']))
    glance('network', 'ARI\'s public support for a bill of his', lambda m: {'mast': 'his bill (Jan 2026)', 'moolenaar': 'the Senate version (Sep 2025)'}[m] if T(m, 'network', 'endorse') else '–')
    glance('nvidia', 'Its employees\' own gifts', lambda m: '$0')
    glance('nvidia', 'Nvidia\'s PAC', lambda m: '$0')
    glance('nvidia', 'Its lobbying reports naming a chip bill he sponsors', lambda m: next((f'{o["n"].split("/")[1]} report{"s" if o["n"].split("/")[1] != "1" else ""}' for o in TY if o['member'] == m and o['type'].startswith('lobbying')), '–'))
    glance('nvidia', 'Gifts from lobbyists and PACs of its firms', lambda m: usd(N[f'lob:nvidia:{m}:total']))
    glance('nvidia', 'PACs of trade groups that list it and not Anthropic', lambda m: usd(N[f'trade:nvidia:{m}']))
    glance('nvidia', 'Huang at a meeting of his committee', lambda m: 'reported, May 2025' if T(m, 'nvidia', 'meeting') else '–')
    glance('nvidia', 'A political ad by Nvidia on Google', lambda m: 'none found')

    # How many lines of that table hold a record for each chairman: counted from the table's own cells, so the figure can say plainly who has the fewest.
    import rows_chairmen
    SIDE = {'anthropic': 'aside', 'pfa': 'aside', 'network': 'aside', 'nvidia': 'nvidia'}
    lines_ = Counter(SIDE[g['group']] for g in G)
    held = {(sd, m): [g[m] for g in G if SIDE[g['group']] == sd and not rows_chairmen.quiet(g[m])] for sd in ('aside', 'nvidia') for m in THREE}
    assert min(THREE, key=lambda m: len(held[('aside', m)])) == 'crawford' and len({len(held[('aside', m)]) for m in THREE}) == 3, 'the sentence under the table says Crawford has the fewest'
    assert all(v.startswith('$') for v in held[('aside', 'crawford')] + held[('nvidia', 'crawford')]), 'the sentence under the table says all of Crawford\'s are gifts of money'
    for sd, what in (('aside', 'on the side of Anthropic and the groups in the key'), ('nvidia', 'on Nvidia\'s side')):
        num(f'glance:lines:{sd}', lines_[sd], f'lines of the at-a-glance table {what}')
        for m in THREE:
            num(f'glance:held:{sd}:{m}', len(held[(sd, m)]), f'of those lines, the ones that hold a record for {m.title()} (a dash, $0 or "none found" is not a record)')

    # Row ids are stable: a row keeps the id it had when an audit read it; a new row takes the next free number.
    # research/nv13_row_ids.csv is the register (table, key, id), seeded from the tables the second audit was given.
    KEYF = {'nv13_ties.csv': lambda r: f"{r['member']}|{r['section']}|{r['type']}", 'nv13_key.csv': lambda r: r['id'], 'nv13_stake.csv': lambda r: r['id'],
            'nv13_events.csv': lambda r: f"{r['lane']}|{r['date']}|{r['kind']}", 'nv13_numbers.csv': lambda r: r['key']}
    reg = {(r['table'], r['key']): r['row_id'] for r in table('nv13_row_ids.csv')}

    def ids(name, rows, prefix):
        used = {v for (t_, _), v in reg.items() if t_ == name}; nxt = max([int(v[2:]) for v in used] or [0]) + 1
        keys = [KEYF[name](r) for r in rows]; assert len(set(keys)) == len(keys), (name, [k for k in keys if keys.count(k) > 1][:3])
        for r, k in zip(rows, keys):
            if (name, k) not in reg:
                reg[(name, k)] = f'{prefix}{nxt:02d}'; nxt += 1
            r['row_id'] = reg[(name, k)]
        rows.sort(key=lambda r: int(r['row_id'][2:]))

    def write(name, rows, prefix, cols):
        ids(name, rows, prefix)
        with open(R / name, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['row_id'] + cols, lineterminator='\n'); w.writeheader(); w.writerows(rows)
        print(f'{name}: {len(rows)} rows')
    write('nv13_ties.csv', TIES, 'CT', ['member', 'section', 'type', 'mark', 'head', 'words', 'usd', 'first', 'last', 'audit', 'src', 'q'])
    write('nv13_key.csv', KEY, 'CK', ['id', 'card', 'label', 'words', 'audit', 'src', 'q'])
    write('nv13_stake.csv', STAKE, 'CS', ['id', 'card', 'label', 'words', 'src', 'q'])
    write('nv13_events.csv', EVENTS, 'CE', ['lane', 'date', 'end', 'kind', 'words', 'src', 'q'])
    ids('nv13_numbers.csv', NUMS, 'CN')
    with open(R / 'nv13_numbers.csv', 'w', newline='') as f:                       # the key comes first: the checker finds a table row by its first cell
        w = csv.DictWriter(f, fieldnames=['key', 'row_id', 'value', 'words', 'src', 'q'], lineterminator='\n'); w.writeheader(); w.writerows(NUMS)
    print(f'nv13_numbers.csv: {len(NUMS)} rows')
    with open(R / 'nv13_row_ids.csv', 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['table', 'key', 'row_id']); w.writerows([t_, k, v] for (t_, k), v in reg.items())
    with open(R / 'nv13_glance.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['group', 'label', 'mast', 'moolenaar', 'crawford', 'note'], lineterminator='\n'); w.writeheader(); w.writerows(G)
    print(f'nv13_glance.csv: {len(G)} rows')
    for m in THREE:
        print(m, {s: sum(1 for t in TIES if t['member'] == m and t['section'] == s) for s in ('anthropic', 'pfa', 'network', 'said', 'nvidia', 'searched')})


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT / 'scripts'))
    main()
