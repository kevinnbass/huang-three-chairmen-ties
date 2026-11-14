"""Recompute every number the three-chairmen figure states from the tables in research/ and the copies in sources/, and
check every quoted passage that has a copy in this repository. Standard library only.
Run: python3 scripts/verify_nv13.py          (exit 0 if every check passes, 1 otherwise)
It does not fetch anything. Passages whose source is only linked (not copied here) are listed with their links in
research/evidence.tsv for a reader to open."""
import csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'research'; S = ROOT / 'sources'
csv.field_size_limit(10**9)
THREE = ['mast', 'moolenaar', 'crawford']
CAND = {'mast': 'H6FL18097', 'moolenaar': 'H4MI04126', 'crawford': 'H0AR01083'}
FAIL = []


def table(name, delimiter=','):
    return list(csv.DictReader(open(R / name, newline=''), delimiter=delimiter))


def check(ok, what, detail=''):
    print(('PASS  ' if ok else 'FAIL  ') + what + (f'   [{detail}]' if detail and not ok else ''))
    if not ok:
        FAIL.append(what)


def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–', '-').replace('—', '-').replace(' ', ' ').replace('​', '')
    for a, b in (('ﬁ', 'fi'), ('ﬂ', 'fl'), ('ﬃ', 'ffi'), ('ﬄ', 'ffl'), ('ﬀ', 'ff'), ('ʼ', "'")):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip().lower()


def money(v):
    v = float(v)
    return (f'${v / 1e6:,.1f}M' if v < 100e6 else f'${v / 1e6:,.0f}M') if v >= 1e6 else f'${v:,.0f}'


def main():
    gifts = table('employee_gifts.csv'); keys = {r['committee_id']: r for r in table('committee_keys.csv')}; rates = {r['side']: r for r in table('employee_gift_rates.csv')}
    ties = table('nv13_ties.csv'); key = {r['id']: r for r in table('nv13_key.csv')}; who = {r['key']: r for r in table('nv13_members.csv')}
    N = {r['key']: r['value'] for r in table('nv13_numbers.csv')}; lg = table('lobbyist_gifts.csv'); glance = table('nv13_glance.csv')
    html = (ROOT / 'figures' / 'nv13-three-chairmen.html').read_text(encoding='utf-8'); flat = re.sub(r'<[^>]+>', '', html).replace('&amp;', '&')
    NV = 'The same records for Nvidia' in flat            # True for the fuller version, which also draws Nvidia's side; the published figure leaves it out and says so
    name = {'anthropic': 'ANTHROPIC', 'nvidia': 'NVIDIA'}
    tie = lambda m, sec, typ: [t for t in ties if t['member'] == m and t['section'] == sec and t['type'].startswith(typ)]
    # ---------------------------------------------------------------- every employee-gift line obeys the counting rule
    check(len({g['sub_id'] for g in gifts}) == len(gifts), 'each gift line has its own FEC sub_id', f'{len(gifts)} lines')
    check(all(g['employer_as_filed'].strip().upper().startswith(name[g['side']]) for g in gifts), 'the employer as filed begins with the company\'s name on every line')
    check(all(g['date'] >= '2025-01-01' and float(g['usd']) > 0 for g in gifts), 'every line is dated Jan 1, 2025 or later and is above zero')
    check(all(g['committee_id'] in keys and keys[g['committee_id']]['bioguide'] == g['bioguide'] for g in gifts), 'every line\'s committee is in committee_keys.csv, tied to the same member')
    check(all(g['image_num'] and (g['file_num'] or g['amended_file_num']) for g in gifts), 'every line carries an FEC page-image number and a filing number')
    early = [g for g in gifts if g['source'] == 'earlier-capture']
    check(len(early) == 9 and all(g['side'] == 'anthropic' and g['committee'] == 'BANKS FOR SENATE' and g['amended_sub_id'] and g['amended_file_num'] and g['amended_image_num'] for g in early),
          'nine lines come from the earlier capture, all Anthropic, all to Banks for Senate, each paired with its amended line', str(len(early)))
    # ---------------------------------------------------------------- the rates across the 535 sitting members
    party = {r['bioguide']: r['party'] for r in keys.values()}
    for side in ('anthropic', 'nvidia'):
        mine = [g for g in gifts if g['side'] == side]; tot = defaultdict(float)
        for g in mine:
            tot[g['bioguide']] += float(g['usd'])
        r = rates[side]; d_, r_ = sum(party[b] == 'D' for b in tot), sum(party[b] == 'R' for b in tot); ind = len(tot) - d_ - r_
        got = (len(tot), round(sum(tot.values()), 2), len(mine), len({g['donor_id'] for g in mine}), d_, r_)
        want = (int(r['members_with_a_gift']), round(float(r['usd']), 2), int(r['lines']), int(r['donors']), int(r['democrats']), int(r['republicans']))
        check(got == want, f'{side}: members reached, dollars, lines, people, Democrats, Republicans recomputed from the gift lines = {want}', str(got))
        parties = f'{d_} Democrats, {r_} Republicans, {ind} independent{"s" if ind != 1 else ""}'
        check(N[f'rate:{side}:members'] == str(len(tot)) and N[f'rate:{side}:usd'] == f'{sum(tot.values()):.0f}' and N[f'rate:{side}:parties'] == parties and (parties in flat or (side == 'nvidia' and not NV)),
              f'{side}: the tile says {len(tot)} of 535, {money(sum(tot.values()))}; {parties}', N[f'rate:{side}:parties'])
        if side == 'anthropic':
            for k in THREE:
                b = who[k]['bioguide']; above = sum(1 for x in tot.values() if x > tot[b] + 1e-9); same = sum(1 for x in tot.values() if abs(x - tot[b]) < 1e-9)
                check(N[f'rank:{k}'] == ('joint ' if same > 1 else '') + str(above + 1), f'{k}: rank by dollars from Anthropic employees is {N[f"rank:{k}"]} ({above} members received more, {same - 1} the same)')
    # ---------------------------------------------------------------- the three chairmen: employees' gifts and their scale
    wt = (S / 'fec-candidate-totals-three-chairmen.txt').read_text(); three = 0.0; window = 0.0
    for k in THREE:
        gs = [g for g in gifts if g['member'] == k and g['side'] == 'anthropic']; usd = sum(float(g['usd']) for g in gs); people = len({g['donor_id'] for g in gs}); three += usd
        window += sum(float(g['usd']) for g in gs if '2026-04-29' <= g['date'] <= '2026-05-20')
        t = tie(k, 'anthropic', 'employee_gifts')[0]
        ok = N[f'emp:anthropic:{k}'] == f'{usd:.0f}' and N[f'emp_people:anthropic:{k}'] == str(people) and abs(float(t['usd']) - usd) < 0.005 and t['first'] == min(g['date'] for g in gs) \
            and t['last'] == max(g['date'] for g in gs) and t['words'].startswith(f'{money(usd)} from ')
        check(ok, f'{k}: Anthropic employees gave {money(usd)} ({people} people, {len(gs)} lines, {t["first"]} to {t["last"]}), as the panel says')
        check(not [g for g in gifts if g['member'] == k and g['side'] == 'nvidia'] and N[f'emp:nvidia:{k}'] == '0', f'{k}: no line from anyone who gave Nvidia as employer')
        m = re.search(rf'CAND_ID={CAND[k]}; CAND_NAME=[^;]+; TTL_RECEIPTS=([\d.]+);.*?CVG_END_DT=(\S+)', wt)
        rec = float(m.group(1)); share = f'{usd / rec * 100:.1f}'
        check(N[f'receipts:{k}'] == f'{rec:.2f}' and N[f'share:{k}'] == share and m.group(2) == '10/14/2026' and f'it equals {share}% of the {money(rec)}' in t['words'],
              f'{k}: campaign receipts {money(rec)} through Oct 14, 2026 (FEC summary file); the employees\' gifts equal {share}% of them')
    check(N['emp:anthropic:three'] == f'{three:.0f}' and N['emp:anthropic:three:window'] == f'{window:.0f}' and f'{money(window)} of the {money(three)} that Anthropic employees gave the three chairmen' in flat,
          f'the three together: {money(three)}, of which {money(window)} is dated Apr 29 to May 20, 2026')
    # ---------------------------------------------------------------- lobbyists' own gifts, three sides, one rule
    ok_rows = all(r['registered_from'] <= r['date'] and (not r['registration_ended'] or r['date'] <= r['registration_ended']) for r in lg)
    check(ok_rows, f'all {len(lg)} lobbyist-gift lines are dated inside the firm\'s registration for the client')
    check(all(r['measure'] in ('named', 'firm_only', 'firm_only_not_classified', 'firm_pac', 'own_pac') and r['member'] in THREE and r['shared_event'] == 'no' for r in lg), 'every line has a known measure, names one of the three, and is not a shared event')
    check(all((r['measure'] in ('firm_pac', 'own_pac')) == (not r['lobbyist_no']) for r in lg), 'a line has a lobbyist number unless it is a firm\'s or a group\'s own PAC')
    cnt = [r for r in lg if r['measure'] != 'own_pac']
    for side in ('anthropic', 'network', 'nvidia'):
        for k in THREE:
            rs = [r for r in cnt if r['side'] == side and r['member'] == k]; u = sum(float(r['amount_usd']) for r in rs); nm = sum(float(r['amount_usd']) for r in rs if r['measure'] == 'named')
            t = tie(k, 'nvidia' if side == 'nvidia' else side, 'lobbyists'); tu = float(t[0]['usd']) if t and t[0]['usd'] else 0.0
            check(N[f'lob:{side}:{k}:total'] == f'{u:.0f}' and N[f'lob:{side}:{k}:named'] == f'{nm:.0f}' and N[f'lob:{side}:{k}:items'] == str(len(rs)) and abs(tu - u) < 0.005,
                  f'{k}, firms registered for {side}: {money(u)} in {len(rs)} gifts ({money(nm)} from lobbyists listed for the client)')
        u = sum(float(r['amount_usd']) for r in cnt if r['side'] == side)
        check(N[f'lob:{side}:three'] == f'{u:.0f}', f'firms registered for {side}: {money(u)} to the three together')
    w = sum(float(r['amount_usd']) for r in cnt if r['side'] == 'nvidia' and r['member'] == 'mast' and '2025-11-17' <= r['date'] <= '2025-12-31')
    check(N['lob:nvidia:mast:window'] == f'{w:.0f}' and (not NV or f'{money(w)} of the {money(float(N["lob:nvidia:mast:total"]))} that lobbyists and a PAC at Nvidia\'s firms gave Mast' in flat), f'Mast: {money(w)} from Nvidia\'s firms is dated Nov 17 to Dec 31, 2025')
    title = re.sub(r'<[^>]+>', '', re.search(r'<h1>(.*?)</h1>', html, re.S).group(1))
    check((f'gave their committees {money(three)}' in title and 'Nvidia' not in title) if not NV else f'gave their committees {money(three)}, Nvidia\'s $0' in title and f'lobbyists and PACs at Nvidia\'s lobbying firms gave {money(float(N["lob:nvidia:three"]))}, at Anthropic\'s {money(float(N["lob:anthropic:three"]))}' in title
          and any(r['side'] == 'nvidia' and r['measure'] == 'firm_pac' for r in cnt) and not any(r['side'] == 'anthropic' and r['measure'] == 'firm_pac' for r in cnt),
          'the title\'s amounts are the sums above' + ('' if NV else ' (it names the employees\' sum and no sum for Nvidia)'), title)
    # ---------------------------------------------------------------- the at-a-glance table repeats the tables
    rows_a = [r for r in glance if r['group'] == 'anthropic']; rows_n = [r for r in glance if r['group'] == 'nvidia']; rows_w = [r for r in glance if r['group'] == 'network']
    usd = lambda v: money(float(v)) if float(v) else '–'
    check(all(rows_a[0][k] == f'{money(float(N[f"emp:anthropic:{k}"]))} · {N[f"emp_people:anthropic:{k}"]} {"people" if int(N[f"emp_people:anthropic:{k}"]) > 1 else "person"}' for k in THREE)
          and all(rows_a[4][k] == usd(N[f'lob:anthropic:{k}:total']) for k in THREE) and all(rows_w[3][k] == usd(N[f'lob:network:{k}:total']) for k in THREE)
          and all(rows_n[3][k] == usd(N[f'lob:nvidia:{k}:total']) and rows_n[0][k] == '$0' and rows_n[4][k] == usd(N[f'trade:nvidia:{k}']) for k in THREE), 'the at-a-glance table\'s money cells equal the numbers above')
    check(all(f'>{r[k].replace("&", "&amp;")}<' in html for r in glance for k in THREE if NV or r['group'] != 'nvidia'), 'every cell of the at-a-glance table that the figure draws is drawn as the table has it')
    # the sentence under the table: how many of its lines hold a record for each chairman (a dash, $0 or "none found" is not a record)
    quiet = lambda v: v.startswith('–') or v in ('$0', 'none found')
    side = lambda r: 'nvidia' if r['group'] == 'nvidia' else 'aside'
    held = {(sd, k): sum(1 for r in glance if side(r) == sd and not quiet(r[k])) for sd in ('aside', 'nvidia') for k in THREE}
    lines = Counter(side(r) for r in glance)
    check(all(N[f'glance:held:{sd}:{k}'] == str(held[(sd, k)]) for sd, k in held) and all(N[f'glance:lines:{sd}'] == str(lines[sd]) for sd in lines)
          and f'Mast has {held[("aside", "mast")]} of {lines["aside"]}, Moolenaar {held[("aside", "moolenaar")]} and Crawford {held[("aside", "crawford")]}, the fewest, all of them gifts of money' in flat
          and (not NV or f'Mast has {held[("nvidia", "mast")]} of {lines["nvidia"]}, Moolenaar {held[("nvidia", "moolenaar")]} and Crawford {held[("nvidia", "crawford")]}' in flat)
          and held[('aside', 'crawford')] < min(held[('aside', 'mast')], held[('aside', 'moolenaar')])
          and all(r['crawford'].startswith('$') for r in glance if not quiet(r['crawford'])),
          f'lines of the table that hold a record: Anthropic\'s side {[held[("aside", k)] for k in THREE]} of {lines["aside"]}, Nvidia\'s side {[held[("nvidia", k)] for k in THREE]} of {lines["nvidia"]}; Crawford\'s are all gifts of money')
    # ---------------------------------------------------------------- the timeline's marks: one dollar scale for the three shapes, and nothing drawn off the canvas
    import math
    per = []                                             # (dollars, area) of every mark that carries an amount
    usd1 = lambda tip: float(re.search(r'\$([\d,]+(?:\.\d+)?)', tip.replace('&#x27;', "'")).group(1).replace(',', ''))
    for m in re.finditer(r'<circle cx="([-\d.]+)" cy="[-\d.]+" r="([\d.]+)"[^>]*><title>([^<]*)</title>', html):
        per.append((usd1(m.group(3)), math.pi * float(m.group(2)) ** 2, float(m.group(1))))
    for m in re.finditer(r'<rect x="([-\d.]+)" y="[-\d.]+" width="([\d.]+)" height="([\d.]+)"[^>]*><title>([^<]*)</title>', html):
        per.append((usd1(m.group(4)), float(m.group(2)) * float(m.group(3)), float(m.group(1))))
    for m in re.finditer(r'<path d="M([-\d.]+),([-\d.]+) L([-\d.]+),([-\d.]+) L[^"]*Z"[^>]*><title>([^<]*)</title>', html):
        q = float(m.group(3)) - float(m.group(1)); per.append((usd1(m.group(5)), 2 * q * q, float(m.group(1))))
    big = [a / u for u, a, x in per]                     # every mark, whatever its size or shape
    shown = [r for r in cnt if NV or r['side'] != 'nvidia']                    # the gifts the figure's timeline covers
    drawn_2024 = [r for r in shown if r['date'] < '2025-01-01']
    notes = all(f'not drawn: {n} gift{"s" if n != 1 else ""} dated 2024 ({money(u)})' in flat
                for n, u in [(len(x), sum(float(r['amount_usd']) for r in x)) for x in ([r for r in drawn_2024 if r['member'] == k and (r['side'] == 'nvidia') == nv] for k in THREE for nv in (True, False)) if x])
    check(len(per) >= (40 if NV else 20) and max(big) / min(big) < 1.02 and 'rx="2" fill-opacity' not in html and min(x for u, a, x in per) > 0 and notes and len(per) == len([r for r in shown if r['date'] >= '2025-01-01']) + sum(1 for g in gifts if g['member'] in THREE and g['side'] == 'anthropic')
          + sum(1 for t in ties if t['type'] in ('company_pac', 'ari_pac') and t['usd']) + (sum(1 for x in table('trade_pac_gifts.csv') if x['lists_nvidia'] == 'yes' and x['lists_anthropic'] == 'no') if NV else 0),
          f'the timeline draws {len(per)} gifts, equal dollars with equal areas whatever the shape (areas per dollar within {100 * (max(big) / min(big) - 1):.1f}%), none off the canvas; {len(drawn_2024)} gifts dated 2024 are announced, not drawn')
    if not NV:                                           # the published figure: Nvidia's side is not drawn, and the notes give its result from the tables
        check(not any(x in flat for x in ('Nvidia\'s firms and trade groups', 'Lobbyists at Nvidia\'s firms', 'Lobbyists and a PAC at Nvidia\'s firms', 'Nvidia\'s PAC.')),
              'no record of Nvidia\'s side is drawn')
        check('Nvidia\'s employees and its PAC gave the three chairmen nothing' in flat and all(N[f'emp:nvidia:{k}'] == '0' for k in THREE) and N['pac:nvidia:members'] == '0'
              and f'lobbyists and PACs at firms registered to lobby for Nvidia gave them {money(float(N["lob:nvidia:three"]))}' in flat
              and f'the PACs of two trade groups that list Nvidia gave Mast {money(float(N["trade:nvidia:three"]))}' in flat,
              f'the notes say what the figure leaves out, with the tables\' sums: Nvidia\'s employees and PAC $0, lobbyists and PACs at its firms {money(float(N["lob:nvidia:three"]))}, two trade groups\' PACs {money(float(N["trade:nvidia:three"]))}')
    # ---------------------------------------------------------------- who funds the group that ran the ads
    ff = (S / 'fec-filings-C30003586-public-first-action.txt').read_text(encoding='utf-8')
    check('filings listed: 1 (pages: 1)' in ff and 'form_type: F9' in ff and 'document_description: 24 HOUR NOTIFICATION 2026' in ff and 'it names no donor, and it is not an account of the group' in flat,
          'the FEC lists one filing by Public First Action Inc.: a 24-hour notice of spending on an ad (form F9)')
    # ---------------------------------------------------------------- page counts in the panel headers
    pages = table('story_pages.tsv', '\t')
    for k in THREE:
        n = sum(1 for p in pages if p['names_' + k] == 'yes')
        check(n == int(who[k]['pages_naming']) and len(pages) == int(who[k]['pages_total']) and f'named on {n} of the {len(pages):,} news pages saved' in flat, f'{k}: named on {n} of the {len(pages):,} saved news pages (story_pages.tsv)')
    # ---------------------------------------------------------------- PAC money
    pacs = table('pacs_by_member.csv'); base = {r['pac']: r for r in table('pac_base_rates.csv')}
    a = [r for r in pacs if r['pac'] == 'anthropic' and float(r['net_usd']) > 0]
    check(len(a) == int(base['anthropic']['sitting_members_with_net_above_zero']) == int(N['pac:anthropic:members']) and abs(sum(float(r['net_usd']) for r in a) - float(N['pac:anthropic:usd'])) < 0.5,
          f'AnthroPAC: {len(a)} sitting members, {money(sum(float(r["net_usd"]) for r in a))}, recomputed from pacs_by_member.csv')
    check(int(base['nvidia']['sitting_members_with_net_above_zero']) == 0 == int(N['pac:nvidia:members']) and not [r for r in pacs if r['pac'] == 'nvidia'], 'Nvidia\'s employee PAC: no sitting member')
    for k in THREE:
        t = [t for t in tie(k, 'anthropic', 'company_pac') if t['usd']]; r = [r for r in a if r['member_bioguide'] == who[k]['bioguide']]
        check(len(t) == len(r) and all(abs(float(x['usd']) - float(y['net_usd'])) < 0.005 for x, y in zip(t, r)), f'{k}: the AnthroPAC line matches pacs_by_member.csv ({r[0]["net_usd"] if r else "none"})')
    ari = [l.split('|') for l in (S / 'fec-committee-to-candidate-ari-pacs.txt').read_text(encoding='latin-1').splitlines()[1:]]
    cand = Counter()
    for l in ari:
        if l[5] in ('24K', '24Z'):
            cand[l[16]] += float(l[14])
    check(N['ari_pac_candidates'] == str(sum(1 for v in cand.values() if v > 0)) and N['ari_pac_usd'] == f'{sum(cand.values()):.0f}' and cand[CAND['mast']] == 2500 and cand[CAND['crawford']] == 1000 and CAND['moolenaar'] not in cand,
          f'ARI\'s two PACs: {sum(1 for v in cand.values() if v > 0)} candidates, {money(sum(cand.values()))}; Mast $2,500, Crawford $1,000 (FEC committee-to-candidate lines)')
    # trade groups: each group's member list as saved, and its PAC's gifts in the FEC committee-to-candidate file
    tg = table('trade_pac_gifts.csv'); G = {'sia': ('C00613521', 'sia-members.txt'), 'iti': ('C00419036', 'iti-members.txt'), 'technet': ('C00328369', 'technet-members.txt')}
    tl = [l.split('|') for l in (S / 'fec-committee-to-candidate-trade-pacs.txt').read_text(encoding='latin-1').splitlines()[1:]]
    back = {v: k for k, v in CAND.items()}
    # a line with no candidate id takes the candidate of its recipient committee, from the FEC's committee master
    cmc = {l.split('|')[0]: l.split('|')[2] for l in (S / 'fec-committee-master-for-blank-candidate-ids.txt').read_text(encoding='latin-1').splitlines()[1:]}
    n_blank = sum(1 for l in tl if not l[16])
    for l in tl:
        l[16] = l[16] or cmc.get(l[15], '')
    check(all(l[16] for l in tl), f'every trade-group PAC line names a candidate, {n_blank} of them through the recipient committee (the FEC line leaves the candidate id blank)')
    for g, (cid, fn) in G.items():
        t = (S / 'trade-groups' / fn).read_text(); nv, an = 'Nvidia is listed.' in t, 'Anthropic is listed.' in t; names = int(re.search(r'\((\d+) names;', t).group(1))
        mine = [l for l in tl if l[0] == cid and l[5] in ('24K', '24Z')]
        got = sorted((back[l[16]], f'{l[13][4:]}-{l[13][:2]}-{l[13][2:4]}', float(l[14])) for l in mine if l[16] in back)
        want = sorted((r['member'], r['date'], float(r['usd'])) for r in tg if r['group'] == g)
        check(got == want and N[f'trade:{g}:members'] == str(names) and N[f'trade:{g}:candidates'] == str(len({l[16] for l in mine}))
              and all((r['lists_nvidia'] == 'yes') == nv and (r['lists_anthropic'] == 'yes') == an for r in tg if r['group'] == g),
              f'{g}: its list ({names} members) {"lists" if nv else "does not list"} Nvidia and {"lists" if an else "does not list"} Anthropic; its PAC gave the three {money(sum(x[2] for x in got))} in {len(got)} gifts')
    for k in THREE:
        u = sum(float(r['usd']) for r in tg if r['member'] == k and r['lists_nvidia'] == 'yes' and r['lists_anthropic'] == 'no'); t = tie(k, 'nvidia', 'trade_pacs')[0]
        check(N[f'trade:nvidia:{k}'] == f'{u:.0f}' and abs((float(t['usd']) if t['usd'] else 0.0) - u) < 0.005, f'{k}: {money(u)} from PACs of trade groups that list Nvidia and not Anthropic')
    check(N['trade:nvidia:three'] == f'{sum(float(r["usd"]) for r in tg if r["group"] in ("sia", "iti")):.0f}' and N['trade:technet:three'] == '0' and not [r for r in tg if r['group'] == 'technet'],
          'the three together: the trade-group total, and nothing from the PAC of TechNet, which lists both companies')
    own = [r for r in lg if r['measure'] == 'own_pac']
    for k in THREE:
        t = tie(k, 'network', 'ari_pac'); o = sum(float(r['amount_usd']) for r in own if r['member'] == k)
        check(len(t) == 1 and abs(float(t[0]['usd']) - o) < 0.005, f'{k}: the ARI PAC line ({money(float(t[0]["usd"]))}) equals what ARI\'s own report to the Senate lists')
    # ---------------------------------------------------------------- lobbying reports naming each bill
    lb = {r['key']: r for r in table('lobbying_bill_reports.csv')}; lf = {r['uuid']: r for r in table('lobbying_filings.csv')}
    for t in ties:
        if t['type'].startswith('lobbying:') and t['section'] == 'anthropic':
            m = re.search(r'^(H\.R\. \d+).*?is named in (\d+) lobbying reports? filed for Anthropic and (\d+) filed for Nvidia', t['words']); bill = m.group(1)
            for side, n in (('anthropic', int(m.group(2))), ('nvidia', int(m.group(3)))):
                r = lb.get(f'{side}:{bill}'); u = r['uuids'].split() if r else []
                check(len(u) == n and all(x in lf and bill in lf[x]['bills'] and lf[x]['side'] == side for x in u), f'{t["member"]}: {n} {side} lobbying reports name {bill}, each in lobbying_filings.csv')
    # ---------------------------------------------------------------- the key: grant totals
    gr = defaultdict(list)
    for r in table('grants_cited.csv'):
        gr[r['link']].append(r)
    for i, rs in gr.items():
        tot = sum(float(r['amount_usd']) for r in rs); ys = sorted(r['year'] for r in rs)
        span = ys[0] if ys[0] == ys[-1] else f'{ys[0]}–{ys[-1][2:]}'
        words = key[i]['words']
        ok = (f'${tot / 1e6:,.1f}M in award' in words and span in words) if i != 'horizon' else f'${tot / 1e6:,.1f}M in its fiscal year ending Jun {ys[0]}' in words
        check(ok, f'key, {i}: {len(rs)} grant rows sum to ${tot / 1e6:,.1f}M ({span}), as the key says', words)
    # ---------------------------------------------------------------- the ads as run
    ads = list(csv.DictReader(open(S / 'google-political-ads-pfa-20260916.csv', newline='')))
    check(N['pfa_google_entries'] == str(sum(1 for x in ads if x['Advertiser_Name'] == 'Public First Action Inc')), f'Google\'s report lists {N["pfa_google_entries"]} entries by Public First Action')
    cz = [l.split('|') for l in (S / 'census-cd119-zcta-fl21.txt').read_text(encoding='utf-8').splitlines() if re.match(r'\d+\|\d{4}\|', l)]
    fl21 = {l[8] for l in cz if l[1] == '1221' and l[8]}; also = {l[8] for l in cz if l[1] != '1221' and l[8] in fl21}
    for t in ties:
        if t['type'] == 'ad_run':
            cr = re.search(r'Ad_ID=(CR\d+)', t['q']).group(1); r = next(x for x in ads if x['Ad_ID'] == cr); lo, hi = (int(x) for x in r['Impressions'].split('-'))
            ok = r['Advertiser_Name'] == 'Public First Action Inc' and r['Ad_Type'] == 'VIDEO' and r['Date_Range_Start'] == t['first'] and r['Date_Range_End'] == t['last'] \
                and f'{lo:,} to {hi:,} showings' in t['words'] and f'${int(r["Spend_Range_Min_USD"]):,} to ${int(r["Spend_Range_Max_USD"]):,} spent' in t['words']
            check(ok, f'{t["member"]}: the ad\'s dates, showings and spending match Google\'s report line {cr}')
            if t['member'] == 'mast':
                z = set(re.findall(r'(\d{5}),Florida', r['Geo_Targeting_Included']))
                check(z == fl21 and f'{len(z)} Florida zip codes' in t['words'] and N['fl21_zip_areas'] == str(len(fl21)) and N['fl21_zip_areas_shared'] == str(len(also)),
                      f'mast: the ad\'s {len(z)} zip codes are exactly the zip-code areas the Census table places wholly or partly in Florida district 21; {len(also)} of them also lie in another district', f'{len(z)} vs {len(fl21)}')
            else:
                check(r['Geo_Targeting_Included'].startswith('MI-2 '), 'moolenaar: the ad\'s target on Google\'s report line is MI-2')
    # ---------------------------------------------------------------- evidence: every row has it; every copied passage is in its copy
    ev = table('evidence.tsv', '\t'); by = defaultdict(list)
    for e in ev:
        by[e['row_id']].append(e)
    used = re.search(r'<!-- rows: (.*?) -->', html).group(1).split()
    check(all(i in by for i in used), f'each of the {len(used)} rows the figure rests on has evidence lines', str([i for i in used if i not in by][:5]))
    cache = {}; tables = {}; n_copy = n_ok = 0; miss = []
    for e in ev:
        if not e['copy_in_repo']:
            continue
        p = ROOT / e['copy_in_repo'].split('#')[0]
        if p not in cache:
            cache[p] = norm(p.read_text(encoding='utf-8', errors='replace'))
        n_copy += 1
        kv = re.match(r'^(\w+)=(.+)$', e['passage']) if p.suffix == '.csv' else None      # a cell of a copied table, written column=value
        if kv and p.name.startswith('google-political-ads'):
            if p not in tables:
                tables[p] = list(csv.DictReader(open(p, newline='')))
            found = any(r.get(kv.group(1)) == kv.group(2) for r in tables[p])
        else:
            found = norm(e['passage']) in cache[p]
        if found:
            n_ok += 1
        else:
            miss.append((e['row_id'], e['copy_in_repo'], e['passage'][:50]))
    check(n_ok == n_copy, f'{n_copy} passages have a copy of their source here and all are found in it', str(miss[:4]))
    check(all(e['url'] or e['copy_in_repo'] for e in ev), f'all {len(ev)} evidence lines give a link or a copy')
    linked = sum(1 for e in ev if not e['copy_in_repo'])
    print(f'\n{len(ev)} evidence lines: {n_copy} checked against a copy in this repository; {linked} are a link and a passage for a reader to open (research/evidence.tsv).')
    print('Not recomputed here (the source is linked, not copied): the 11 House members on Public First Action\'s list of Jul 17, 2026.')
    print('ALL CHECKS PASS' if not FAIL else f'{len(FAIL)} CHECK(S) FAILED')
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
