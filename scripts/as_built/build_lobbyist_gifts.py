"""Lobbyists' own gifts to the three chairmen, by company: the same rule for Nvidia and for Anthropic.

Run: python3 -I scripts/build_lobbyist_gifts.py
Reads the lobbyists' contribution reports (LD-203) saved under research/primary/lda-gov-contrib-<member>-<year>/ and each
company's lobbying filings (research/primary/lda-gov-<company>-<year>/body.json). Writes research/lobbyist_gifts.csv.

Three sides under one rule: "nvidia" and "anthropic" (each company's own registrants, from its saved filings) and "network"
(firms registered for groups Open Philanthropy funds, from the evidence pack's lb_network_windows.csv).
An item counts when all hold:
  1. it is a contribution item of an LD-203 report whose honoree is Mast, Moolenaar or Crawford (the honoree as written is
     kept; a line that lists several honorees is flagged as a shared event);
  2. the report was filed by a registrant (a firm, or the company itself), or by a lobbyist it employs, and the registrant
     had a lobbying registration for that client on the day of the gift (effective date to termination date);
  3. measure "named": the lobbyist is listed for that client by that registrant, from the first quarter listed (or the
     registration date) to 90 days after the last quarter listed; "firm_only": the lobbyist works at the registrant but is
     not listed for the client then; "firm_pac": the registrant's own report (its political committee's gift);
     "own_pac": the same where the registrant is the client itself (the group's own committee, counted elsewhere as its PAC).
     For "network" lines the named/firm_only call is the pack's (lb_4b_measures.csv); a line the pack does not hold is
     "firm_only_not_classified".
The same gift appears in more than one pull and again in amended reports: an item is counted once per filer, member, payee,
date and amount. No lobbyist is named in the output: each gets a number within its side (A-1, N-1, ...).
"""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; P = ROOT / 'research' / 'primary'
# The honoree as the filer wrote it. The surname must end there, or run straight into "for Congress" ("MastForCongress": the second
# audit found a $500 gift written that way, which a plain word-boundary rule missed). "Masto" and "Masters" are other people.
# Crawford: other people share the surname, so strings naming another Crawford are refused.
END = r'(?=\W|$|for\s*congress|4\s*congress)'
MEMBERS = {
    'mast': re.compile(r'\bMast' + END, re.I),
    'moolenaar': re.compile(r'\bMoolenaar' + END, re.I),
    'crawford': re.compile(r'^(?!.*\b(?:Susan|C\.)\s+Crawford\b).*\bCrawford' + END, re.I | re.S),
}
# every honoree string that contains the letters of a surname is listed, accepted or refused, so a missed spelling shows up in the run's printout
SURNAME = {'mast': re.compile(r'Mast', re.I), 'moolenaar': re.compile(r'Moolenaar', re.I), 'crawford': re.compile(r'Crawford', re.I)}
SEVERAL = re.compile(r'[;,]|\band\b', re.I)          # an honoree line that lists several people: a shared event
TAG = {'nvidia': 'NV', 'anthropic': 'AN', 'network': 'OP'}
PACK = Path('EVIDENCE_SETS/congress/research')
QSTART = {'first_quarter': '01-01', 'second_quarter': '04-01', 'third_quarter': '07-01', 'fourth_quarter': '10-01'}
QEND = {'first_quarter': '03-31', 'second_quarter': '06-30', 'third_quarter': '09-30', 'fourth_quarter': '12-31'}
COMPANY = {'nvidia': ('2024', '2025', '2026'), 'anthropic': ('2024', '2025', '2026', '2026-p2')}


def norm(s):
    return re.sub(r'[^A-Z0-9]+', ' ', (s or '').upper()).strip()


def plus90(day):
    from datetime import date, timedelta
    return (date.fromisoformat(day) + timedelta(days=90)).isoformat()


def windows():
    """(group, registrant id, client) -> name, client, from, to, and for each listed lobbyist the span it is listed for.
    A lobbyist counts as listed from the start of the first quarter (or the registration date, if on the registration) to
    90 days after the end of the last quarter listed, the pack's measure B."""
    w, got, need = {}, {}, {}
    for co, tags in COMPANY.items():
        for tag in tags:
            j = json.loads((P / f'lda-gov-{co}-{tag}' / 'body.json').read_text())
            got[(co, tag[:4])] = got.get((co, tag[:4]), 0) + len(j['results']); need[(co, tag[:4])] = j['count']
            for f in j['results']:
                if co not in norm(f['client']['name']).lower():
                    continue
                k = (co, f['registrant']['id'], '')
                x = w.setdefault(k, {'name': f['registrant']['name'], 'client': f['client']['name'], 'from': f['client'].get('effective_date') or '9999',
                                     'to': '', 'lobbyists': {}, 'filings': 0})
                x['from'] = min(x['from'], f['client'].get('effective_date') or '9999'); x['filings'] += 1
                if f.get('termination_date'):
                    x['to'] = max(x['to'], f['termination_date'][:10])
                y = str(f['filing_year']); per = f['filing_period']
                start = (f['client'].get('effective_date') if f['filing_type'].startswith('R') else None) or f'{y}-{QSTART[per]}'
                end = plus90(f'{y}-{QEND[per]}')
                for a in f.get('lobbying_activities') or []:
                    for l in a.get('lobbyists') or []:
                        sp = x['lobbyists'].setdefault(l['lobbyist']['id'], [start, end])
                        sp[0] = min(sp[0], start); sp[1] = max(sp[1], end)
    assert got == need, ('a year of filings is incomplete', got, need)
    for r in csv.DictReader([l for l in (PACK / 'lb_network_windows.csv').open(newline='') if not l.startswith('#')]):
        if r['tier'] == 'T3' or not r['status'].startswith('window'):      # T3 is Anthropic itself, built above from its filings
            continue
        w[('network', int(r['registrant_id']), r['client_name'])] = {'name': r['registrant_name'], 'client': r['client_name'], 'from': r['window_start'],
                                                                   'to': r['window_end'], 'lobbyists': None, 'filings': 0}
    return w


# The three-chairmen figure states its window: gifts dated Jan 2024 to Jun 2026. Reports for 2020 to 2023 were saved later for the companion map
# figure (scripts/build_lobbyist_gifts_map.py reads them); without this floor a rebuild on Nov 16, 2026 took in two gifts of 2023.
FROM = '2024-01-01'


def items():
    seen, out, dup, variants = set(), [], 0, defaultdict(Counter)
    for d in sorted(P.glob('lda-gov-contrib-*')):
        pages = sorted(d.glob('page-*.json'))
        got = 0
        for pg in pages:
            j = json.loads(pg.read_text()); got += len(j['results']); total = j['count']
            for r in j['results']:
                lob = (r.get('lobbyist') or {}).get('id')
                for it in r.get('contribution_items') or []:
                    hon = it.get('honoree_name') or ''
                    for m, rx in MEMBERS.items():
                        if SURNAME[m].search(hon):
                            variants[m][(hon.strip(), bool(rx.search(hon)))] += 1
                        if not rx.search(hon):
                            continue
                        if (it.get('date') or '') < FROM:           # this table's window, as the figure's notes state it
                            continue
                        key = (r['registrant']['id'], lob, m, norm(it.get('payee_name')), it.get('date'), it.get('amount'))
                        if key in seen:
                            dup += 1; continue
                        seen.add(key)
                        out.append({'member': m, 'registrant_id': r['registrant']['id'], 'registrant': r['registrant']['name'], 'lobbyist_id': lob,
                                    'filer_type': r['filer_type_display'], 'date': it.get('date'), 'amount_usd': it.get('amount'),
                                    'payee': it.get('payee_name'), 'honoree_as_written': hon.strip(), 'contribution_type': it.get('contribution_type_display'),
                                    'contributor_is_filer': norm(it.get('contributor_name')) != norm(r['registrant']['name']),
                                    'report_url': r['filing_document_url'], 'report_year': r['filing_year'], 'report_period': r['filing_period_display'],
                                    'source': f'{d.name}/{pg.name}'})
        assert got == total, (d.name, got, total)
    return out, dup, variants


def pack_measures():
    """(member, registrant id, date, whole dollars) -> the pack's measure for that line, for the groups Open Philanthropy funds."""
    B = {'M001199': 'mast', 'M001194': 'moolenaar', 'C001087': 'crawford'}
    rd = lambda f: list(csv.DictReader([l for l in (PACK / f).open(newline='') if not l.startswith('#')]))
    meas = {r['row_id']: r for r in rd('lb_4b_measures.csv')}
    out = {}
    for r in rd('lobbyist_contributions.csv'):
        m = meas.get(r['row_id'])
        if r['member_bioguide'] in B and m and m['measure'] in ('named', 'firm_only'):
            out[(B[r['member_bioguide']], int(m['registrant_id']), r['date'], int(float(r['amount_usd'])))] = (m['measure'], r['row_id'])
    return out


def main():
    W = windows(); its, dup, variants = items(); PM = pack_measures()
    print(f'LD-203 items naming one of the three as honoree: {len(its)} (repeats across pulls and amended reports dropped: {dup})')
    print('by member:', dict(Counter(i['member'] for i in its)))
    for m, c in variants.items():
        rej = [(h, n) for (h, ok), n in c.items() if not ok]
        print(f'  honoree strings with the surname "{m}": accepted {sum(n for (h, ok), n in c.items() if ok)} in {sum(1 for (h, ok) in c if ok)} spellings; '
              f'refused {sum(n for h, n in rej)}: {sorted(rej, key=lambda x: -x[1])[:8]}')
    print('registration windows:')
    for (co, rid, cl), x in sorted(W.items(), key=lambda kv: (kv[0][0], kv[1]['from'])):
        n = 'pack' if x['lobbyists'] is None else len(x['lobbyists'])
        print(f"  {co:9} {x['name'][:40]:40} for {x['client'][:34]:34} from {x['from']} to {x['to'] or 'open'}; lobbyists listed: {n}")
    rows, ids = [], {}
    for i in sorted(its, key=lambda i: (i['date'] or '', i['member'], str(i['lobbyist_id']))):
        for (co, rid, cl), x in W.items():
            day = i['date'] or ''
            if rid != i['registrant_id'] or not (x['from'] <= day and (not x['to'] or day <= x['to'])):
                continue
            pack_row = ''
            if i['lobbyist_id'] is None:        # the registrant's own report: its political committee's gift
                measure = 'own_pac' if norm(x['name'])[:20] == norm(x['client'])[:20] else 'firm_pac'
            elif x['lobbyists'] is None:
                measure, pack_row = PM.get((i['member'], rid, day, int(float(i['amount_usd']))), ('firm_only_not_classified', ''))
            else:
                sp = x['lobbyists'].get(i['lobbyist_id'])
                measure = 'named' if sp and sp[0] <= day <= sp[1] else 'firm_only'
            tag = ''
            if i['lobbyist_id'] is not None:
                tag = ids.setdefault((co, i['lobbyist_id']), f"{TAG[co]}-{sum(1 for k in ids if k[0] == co) + 1}")
            rows.append({'item': '', 'side': co, 'member': i['member'], 'date': day, 'amount_usd': i['amount_usd'], 'measure': measure,
                         'registrant': x['name'], 'client': x['client'], 'registered_from': x['from'], 'registration_ended': x['to'],
                         'filer': i['filer_type'], 'lobbyist_no': tag, 'payee': i['payee'], 'honoree_as_written': i['honoree_as_written'],
                         'shared_event': 'yes' if SEVERAL.search(i['honoree_as_written']) else 'no',
                         'contribution_type': i['contribution_type'], 'report_year': i['report_year'], 'report_period': i['report_period'],
                         'report_url': i['report_url'], 'pack_row': pack_row, 'source': i['source']})
    # Item ids and lobbyist numbers are stable: a line keeps what it had when an audit read it; a new line takes the next free number.
    # research/lobbyist_gift_ids.csv is the register, seeded from the table the second audit was given.
    KEY = lambda r: '|'.join(r[k] for k in ('side', 'member', 'date', 'amount_usd', 'measure', 'registrant', 'payee', 'honoree_as_written', 'report_url'))
    regp = ROOT / 'research' / 'lobbyist_gift_ids.csv'
    if regp.exists():
        reg = {r['key']: (r['item'], r['lobbyist_no']) for r in csv.DictReader(regp.open(newline=''))}
    else:
        reg = {KEY(r): (r['item'], r['lobbyist_no']) for r in csv.DictReader((ROOT / 'research' / 'lobbyist_gifts.before-round2-fixes.csv').open(newline=''))}
    keys = [KEY(r) for r in rows]; assert len(set(keys)) == len(keys), 'two lines share a key'
    same = {}                                                    # this run's number for a lobbyist -> the registered number
    for r, k in zip(rows, keys):
        if k in reg and r['lobbyist_no']:
            assert same.setdefault(r['lobbyist_no'], reg[k][1]) == reg[k][1], ('one lobbyist, two registered numbers', r['lobbyist_no'])
    used_no = {v[1] for v in reg.values() if v[1]}; used_item = {v[0] for v in reg.values()}
    for r, k in zip(rows, keys):
        if k not in reg:
            no = ''
            if r['lobbyist_no']:
                no = same.get(r['lobbyist_no'])
                if no is None:
                    tag = r['lobbyist_no'].split('-')[0]; no = f"{tag}-{max([int(u.split('-')[1]) for u in used_no if u.startswith(tag + '-')] or [0]) + 1}"
                    same[r['lobbyist_no']] = no; used_no.add(no)
            item = f"LG{max(int(u[2:]) for u in used_item) + 1:03d}"; used_item.add(item); reg[k] = (item, no)
            print(f'  new line since the register was made: {item} {r["side"]} {r["member"]} {r["date"]} ${float(r["amount_usd"]):,.0f} {r["measure"]}')
        r['item'], r['lobbyist_no'] = reg[k]
    gone = [v[0] for k, v in reg.items() if k not in set(keys)]; assert not gone, ('a registered line is no longer in the table', gone)
    # Whose money each line is (added Nov 16, 2026). A lobbyist's report also lists contributions of committees: a firm's PAC, a PAC the lobbyist
    # serves, a campaign committee. A reading of the companion map figure found one line of this table, a campaign committee's $1,000, worded here
    # as a lobbyist's own gift. The rule is the one written for that figure's wider table, applied to every member alike: the report says SELF or
    # gives the filer's own name and nothing else (scripts/build_lobbyist_gifts_map.py, whose(); run that script first). The two columns are
    # copied from that table by the line's key; no line, id or measure of this table changes.
    wide = {KEY(r): r for r in csv.DictReader((ROOT / 'research' / 'lobbyist_gifts_map.csv').open(newline=''))}
    for r, k in zip(rows, keys):
        assert k in wide, ('a line of this table is not in the wider table', r['item'])
        r['own_money'] = wide[k]['own_money']; r['contributor'] = wide[k]['contributor']
        assert r['own_money'] in ('yes', 'no') and (r['own_money'] == 'yes') == (not r['contributor']), r['item']
        assert r['own_money'] == 'no' or r['lobbyist_no'], ('a line counted as a lobbyist\'s own money has no lobbyist', r['item'])
    rows.sort(key=lambda r: r['item'])
    with regp.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['key', 'item', 'lobbyist_no']); w.writerows([k, v[0], v[1]] for k, v in sorted(reg.items(), key=lambda kv: kv[1][0]))
    with open(ROOT / 'research' / 'lobbyist_gifts.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f'items inside a registration window: {len(rows)} (shared events: {sum(r["shared_event"] == "yes" for r in rows)})')
    c, s = Counter(), Counter()
    for r in rows:
        k = (r['side'], r['member'], r['measure']); c[k] += 1; s[k] += float(r['amount_usd'])
    for k in sorted(c):
        print(f'  {k[0]:9} {k[1]:10} {k[2]:24} items={c[k]:3d} usd={s[k]:>10,.0f} lobbyists={len({r["lobbyist_no"] for r in rows if (r["side"], r["member"], r["measure"]) == k and r["lobbyist_no"]})}')
    tot = Counter()
    for r in rows:
        tot[(r['side'], r['member'])] += float(r['amount_usd'])
    print('totals:', {f'{k[0]}/{k[1]}': v for k, v in sorted(tot.items())})
    # controls: the two pack lines for groups Open Philanthropy funds must be found and classified as the pack has them
    for firm, m, day, amt in (('KYLE HOUSE GROUP', 'mast', '2024-09-25', 1000.0), ('NAVIGATORS GLOBAL', 'moolenaar', '2024-06-28', 500.0)):
        hit = [r for r in rows if firm in norm(r['registrant']) and r['member'] == m and r['date'] == day and float(r['amount_usd']) == amt and r['side'] == 'network']
        print(f'  control: {firm} / {m} / {day} / ${amt:,.0f}: {[(h["measure"], h["pack_row"]) for h in hit] or "NOT FOUND"}')
        assert len(hit) == 1 and hit[0]['measure'] == 'named', 'control failed'


if __name__ == '__main__':
    main()
