"""Lobbyists' own gifts to the members the map figure draws (27 since Nov 15, 2026), by side, under the rule of scripts/build_lobbyist_gifts.py
(which covers the three chairmen and was audited twice; that table is not touched here).

Run: python3 -I scripts/build_lobbyist_gifts_map.py            (prints the checks; writes the tables)
     python3 -I scripts/build_lobbyist_gifts_map.py --look     (prints only: every honoree spelling, accepted or refused)
Reads the contribution reports (LD-203) saved by registrant under research/primary/lda-gov-contrib-reg<id>-<year>/ (every
report of the 33 registrants on either side and of their lobbyists, 2024 to 2026: scripts/lda_contributions_by_registrant.py)
and, for the three chairmen, the pulls by honoree. Writes research/lobbyist_gifts_map.csv and its id register
research/lobbyist_gifts_map_ids.csv.

Sides: "nvidia" and "anthropic" (each company's own registrants, from its saved lobbying filings) and "network" (firms
registered for groups Open Philanthropy funds, from the evidence pack's lb_network_windows.csv): the windows of
build_lobbyist_gifts.windows(). An item counts when the report's registrant had a registration for that client on the day of
the gift; measures as in that script (named, firm_only, firm_pac, own_pac).

Whose gift it is: the honoree as the filer wrote it. A surname alone is not enough where other politicians share it, so each
member has the given names that may stand with the surname, and a string that puts another given name with it is refused.
Every spelling that holds a member's surname is printed with the call made, so a wrong call can be seen.

Controls (the run stops if one fails):
  A. for the three chairmen every line of the audited table research/lobbyist_gifts.csv is found again, with the same measure;
  B. for the firms registered for groups Open Philanthropy funds, the pack's own lines for these 24 members
     (congress/research/lobbyist_contributions.csv with lb_4b_measures.csv) are set beside the lines found here.
No lobbyist is named in the output: each has a number within its side."""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / 'research' / 'primary'; R = ROOT / 'research'
sys.path.insert(0, str(ROOT / 'scripts')); sys.dont_write_bytecode = True
import build_lobbyist_gifts as B, rows_ledger as L
PACK = Path('EVIDENCE_SETS/congress/research')
# given names that may stand with the surname; "strict" members share the surname with other sitting politicians, so the
# surname alone (or with a bare title) is not enough for them
GIVEN = {'warren': ('elizabeth', 'liz'), 'coons': ('chris', 'christopher'), 'cramer': ('kevin',), 'schumer': ('chuck', 'charles'), 'banks': ('jim', 'james'),
         'blumenthal': ('richard', 'dick'), 'warner': ('mark',), 'cornyn': ('john',), 'kennedy': ('john',), 'thune': ('john',), 'wyden': ('ron', 'ronald'),
         'mast': ('brian',), 'crawford': ('rick', 'eric'), 'meeks': ('gregory', 'greg'), 'himes': ('jim', 'james'), 'huizenga': ('bill', 'william'),
         'johnson': ('mike', 'michael'), 'moolenaar': ('john',), 'jeffries': ('hakeem',), 'magaziner': ('seth',), 'subramanyam': ('suhas',),
         'bacon': ('don', 'donald'), 'mccaul': ('michael', 'mike'), 'cotton': ('tom', 'thomas'),
         'scott': ('tim', 'timothy'), 'ricketts': ('pete', 'peter'), 'neal': ('richard', 'richie', 'rich')}
# members who share the surname with other politicians of these years: the surname alone is not enough, a given name (or its
# initial), or one of these titles, must stand with it
STRICT = {'johnson': ('speaker',), 'kennedy': ('sen', 'senator', 'sens', 'senators'),
          'scott': ()}        # two senators and several representatives carry the surname: no title settles it, only the given name (or its initial)
# strings that hold the letters of a surname and name something else
REFUSE = {'banks': re.compile(r'Home Loan|Food Bank|Community Bank|Bankers', re.I), 'meeks': re.compile(r'Miller[- ]?Meeks', re.I),
          'kennedy': re.compile(r'Fitzgerald|John\.? F\b|Kennedy Center|Library|President John', re.I),
          'scott': re.compile(r'Staff Director for', re.I)}       # an item honouring a member of his committee's staff is not a gift to him
TITLE = {'sen', 'sens', 'senator', 'senators', 'rep', 'reps', 'representative', 'representatives', 'congressman', 'congresswoman', 'hon', 'honorable', 'the', 'chairman', 'chair',
         'chairwoman', 'leader', 'speaker', 'mr', 'mrs', 'ms', 'dr', 'whip', 'majority', 'minority', 'us', 'ranking', 'member', 'vice', 'house', 'senate', 'democratic', 'republican',
         'congress', 'cong', 'elect', 'team', 'friends', 'of', 'for', 'committee', 'pac', 'leadership', 'candidate'}
AFTER_OK = {'for', 'victory', 'senate', 'congress', 'committee', 'pac', 'campaign', 'leadership', 'fund', 'jfc', 'majority', 'team', 'action', 'joint', 'in', 'of', 'r', 'd',
            'la', 'ma', 'de', 'nd', 'ny', 'ind', 'ct', 'va', 'tx', 'sd', 'or', 'fl', 'ark', 'ar', 'mi', 'ne', 'ri', 'jr', 'sr', 'iii', 'ii', 'us', 'u', 's', 'house', 'reelect',
            'lpac', 'candidate', 'leadership', 'and', 'is', 'was', 'on', 'at', 'to', 'the', 'a'}
COMMITTEE = re.compile(r'\b(?:victory|fund|committee|pac|jfc|lpac)\b', re.I)
SEP = re.compile(r'\s*(?:;|/|&|\band\b|\n|\|)\s*', re.I)


def call(member, hon):
    """'yes', 'no' or '' (the surname is not in the string) for one honoree string.
    The three chairmen keep the rule of the audited table. For the others, in order: a given name of the member (or its initial)
    standing with the surname settles it; the surname used as someone's given or middle name ("Warren Davidson", "Davidson,
    Warren") is refused unless the string is a committee's name; another given name standing with it ("Mark Huizenga",
    "Kennedy, Timothy") is refused unless it is a misspelling of the member's (same first two letters); where other
    politicians share the surname a title of the member must stand with it; otherwise the surname is taken as the member's."""
    if member in B.MEMBERS:
        return ('yes' if B.MEMBERS[member].search(hon) else 'no') if B.SURNAME[member].search(hon) else ''
    s = member; g = GIVEN[member]; ini = {x[0] for x in g}
    if not re.search(r'\b' + s + B.END, hon, re.I):
        return ''
    if member in REFUSE and REFUSE[member].search(hon):
        return 'no'
    W = lambda t: re.findall(r"[A-Za-z']+", t.replace('.', ' '))
    # the member's given name, or a misspelling of it (same first two letters); where other politicians share the surname a misspelling
    # is not accepted: only the given name itself, or its initial, stands with the surname (the eighth reading, Nov 16, 2026)
    like = lambda w: w.lower() in g or (member not in STRICT and any(w.lower()[:2] == x[:2] for x in g))
    name_like = lambda w: len(w) > 1 and (w[0].isupper() or hon.isupper()) and w.lower() not in AFTER_OK and w.lower() not in TITLE
    verdicts = []
    for seg in SEP.split(hon):
        parts = seg.split(',')
        for pi, part in enumerate(parts):
            for m in re.finditer(r'\b' + s + B.END, part, re.I):
                wb = W(part[:m.start()]); wa = W(part[m.end():]); nxt = W(parts[pi + 1]) if pi + 1 < len(parts) else []
                names_b = []                                             # the words standing right before the surname, back to the nearest title
                for w in reversed(wb):
                    if w.lower() in TITLE:
                        break
                    if len(w) > 1:
                        names_b.insert(0, w)
                first_initial = bool(wb) and len(wb[-1]) == 1 and wb[-1].lower() in ini and (len(wb) < 2 or len(wb[-2]) == 1 or wb[-2].lower() in TITLE)
                if any(w.lower() in g for w in wb[-3:]) or any(w.lower() in g for w in wa[:2]) or any(w.lower() in g for w in nxt[:2]) or first_initial:
                    verdicts.append('yes'); continue
                if wa and wa[0].lower() in ('for', 'victory', 'majority', 'leadership', 'pac', 'lpac', 'committee', 'campaign') and member not in STRICT:
                    verdicts.append('yes'); continue                     # the member's own committee ("Cotton for Senate, Inc.", "via Thune Victory Committee")
                if wa and name_like(wa[0]):                              # the surname as a given or middle name, or a committee's name
                    verdicts.append('yes' if COMMITTEE.search(seg) and member not in STRICT else 'no'); continue
                if names_b:                                              # another word stands right before the surname
                    verdicts.append('yes' if like(names_b[-1]) else 'no'); continue
                if len(parts) == 2 and pi == 1 and not wb and len(W(parts[0])) and all(name_like(w) or len(w) == 1 for w in W(parts[0])):
                    verdicts.append('no'); continue                      # "Davidson, Warren": the surname is here a given name
                if len(parts) == 2 and pi == 0 and nxt and name_like(nxt[0]) and not like(nxt[0]):
                    verdicts.append('no'); continue                      # "Huizenga, Mark": another person
                if member in STRICT:
                    verdicts.append('yes' if any(w.lower() in STRICT[member] for w in wb) else 'no'); continue
                verdicts.append('yes')
    return 'yes' if 'yes' in verdicts else 'no'


# the rule's test cases: each must give the call written beside it, on every run
# the years of reports read. The pull of 2020 to 2023 (some registrations start before 2024) is added here once it is complete for every firm.
YEARS = ('2020', '2021', '2022', '2023', '2024', '2025', '2026')

CASES = [('scott', 'Tina Scott', 'no'), ('scott', 'Sen. Tim Scott', 'yes'),
         ('thune', 'Reps. Mike Johnson, Hakeem Jeffries, and Joyce Beatty. Sens. Thune, Schumer, Whitehouse', 'yes'), ('warren', 'Rep. Warren Davidson', 'no'), ('warren', 'Davidson, Warren', 'no'),
         ('warren', 'Elizabeth Warren', 'yes'), ('warren', 'Sen. Warren', 'yes'), ('warren', 'Warren, Elizabeth', 'yes'), ('johnson', 'Rep. Dustin M. Johnson', 'no'), ('johnson', 'Reps. M.Johnson, H.Jeffries', 'yes'),
         ('johnson', 'Speaker Johnson', 'yes'), ('johnson', 'Sen. Ron Johnson', 'no'), ('johnson', 'Johnson, James Michael', 'yes'), ('johnson', 'Johnson Leadership Fund', 'no'), ('kennedy', 'Kennedy, Timothy', 'no'),
         ('kennedy', 'Sen. John Neely Kennedy', 'yes'), ('kennedy', 'John F. Kennedy Library Foundation', 'no'), ('kennedy', 'Senator Kennedy', 'yes'), ('huizenga', 'Mark Huizenga', 'no'), ('huizenga', 'Huizenga, Bill', 'yes'),
         ('cramer', 'The Honorable Keven Cramer', 'yes'), ('cotton', 'Cotton for Senate, Inc.', 'yes'), ('cotton', 'National Cotton Council', 'no'), ('bacon', 'BOLD ACTIVE CONSERVATIVES OF NEBRASKA PAC-BACON PAC', 'yes'),
         ('thune', 'NRSC Headquarters Fund (via Thune Victory Committee)', 'yes'), ('meeks', 'Miller-Meeks, Mariannette', 'no'), ('meeks', 'Rep. Gregory Meeks', 'yes'), ('banks', 'Federal Home Loan Banks', 'no'),
         ('banks', 'Banks for Senate', 'yes'), ('coons', 'Coons Hickenlooper Victory Fund', 'yes'), ('cornyn', 'Capito, Husted, Ricketts, Cornyn, Hyde-Smith', 'yes'), ('warner', 'M Hassan J Shaheen, M Warner', 'yes'),
         ('mast', 'Sen. Catherine Cortez Masto', 'no'), ('scott', 'Sen. Rick Scott', 'no'), ('scott', 'Senator Scott', 'no'), ('scott', 'Scott, Tim', 'yes'), ('scott', 'Tim Scott for Senate', 'yes'),
         ('scott', 'Rep. Scott Peters', 'no'), ('scott', 'Austin Scott', 'no'), ('neal', 'Rep. Neal Dunn', 'no'), ('neal', 'Richard E. Neal', 'yes'), ('ricketts', 'Sen. Pete Ricketts', 'yes'), ('scott', 'Lila Nieves-Lee, Staff Director for Sen. Tim Scott U.S. Senate Committee on Banking', 'no'), ('mast', 'MastForCongress', 'yes'), ('bacon', 'D Bacon, T Balderson', 'yes'), ('wyden', 'Thune John', '')]


ORG = re.compile(r'PAC\b|POLITICAL|COMMITTEE|FUND\b|ASSOC|LLC|INC\b|LLP|GROUP|COUNCIL|CHAMBER|UNION|FEDERATION|SOCIETY|LEAGUE', re.I)


SUFFIX = {'jr', 'sr', 'ii', 'iii', 'iv', 'mr', 'mrs', 'ms', 'dr', 'hon', 'esq'}
CAMPAIGN = re.compile(r'\bFOR\s+(?:U\.?\s?S\.?\s+)?(?:CONGRESS|SENATE|HOUSE|GOVERNOR|PRESIDENT|AMERICA)\b|^FRIENDS\s+OF\b|\bFOR\s+\w+\s+\w+\s*$', re.I)
CARRIES = "a campaign committee that carries the filer's name"


def name_words(t):
    return re.sub(r'[^a-z ]', ' ', re.sub(r"['’.\-]", '', (t or '').lower())).split()


def whose(lob, contributor):
    """Whose money a line of a lobbyist's report is, from the contributor the report names: 'own' when it says SELF or gives the filer's own name
    and nothing else (every word a part of the filer's name as the register holds it, an initial or a title); 'committee' when the name is a
    political committee's or a firm's; 'campaign' when it is a campaign committee (it can carry the filer's surname: the tenth reading, Nov 16, 2026,
    found one such line still counted as a lobbyist's own after the ninth had found the PACs); otherwise 'unread': a reader decides
    (research/lobbyist_contributor_read.tsv), and the build stops until one has."""
    c = contributor.strip()
    if c.upper() == 'SELF':
        return 'own'
    name = set()
    for f in ('first_name', 'middle_name', 'last_name', 'nickname', 'suffix', 'suffix_display', 'prefix', 'prefix_display'):
        name |= set(name_words(str(lob.get(f) or '')))
    last = set(name_words(str(lob.get('last_name') or ''))); cw = name_words(c)
    if last and last <= set(cw) and all(w in name or len(w) == 1 or w in SUFFIX for w in cw):
        return 'own'                                             # a surname can hold a word of the committee pattern, so the name is tried first
    return 'committee' if ORG.search(c) else 'campaign' if CAMPAIGN.search(c) else 'unread'


def items(members):
    seen, out, dup = set(), [], 0; variants = defaultdict(Counter); folders = Counter()
    for d in sorted(P.glob('lda-gov-contrib-*')):
        if not (d / 'meta.json').exists() or d.name[-4:] not in YEARS:
            continue
        got = 0; total = None
        for pg in sorted(d.glob('page-*.json')):
            j = json.loads(pg.read_text()); got += len(j['results']); total = j['count']
            for r in j['results']:
                lob = (r.get('lobbyist') or {}).get('id')
                for it in r.get('contribution_items') or []:
                    hon = it.get('honoree_name') or ''
                    for m in members:
                        c = call(m, hon)
                        if not c:
                            continue
                        variants[m][(hon.strip(), c)] += 1
                        if c != 'yes':
                            continue
                        key = (r['registrant']['id'], lob, m, B.norm(it.get('payee_name')), it.get('date'), it.get('amount'))
                        if key in seen:
                            dup += 1; continue
                        seen.add(key)
                        out.append({'member': m, 'registrant_id': r['registrant']['id'], 'registrant': r['registrant']['name'], 'lobbyist_id': lob,
                                    'filer_type': r['filer_type_display'], 'date': it.get('date'), 'amount_usd': it.get('amount'),
                                    'payee': it.get('payee_name'), 'honoree_as_written': hon.strip(), 'contribution_type': it.get('contribution_type_display'),
                                    'contributor': (it.get('contributor_name') or '').strip(), 'whose': whose(r.get('lobbyist') or {}, it.get('contributor_name') or ''),
                                    'report_url': r['filing_document_url'], 'report_year': r['filing_year'], 'report_period': r['filing_period_display'],
                                    'source': f'{d.name}/{pg.name}'})
        assert got == total, (d.name, got, total)
        folders['by registrant' if d.name.startswith('lda-gov-contrib-reg') else 'by honoree'] += 1
    return out, dup, variants, folders


def pack_lines(bio):
    """The pack's own lines for these members at firms registered for groups Open Philanthropy funds: (member, registrant id, date, whole dollars) -> (measure, row id)."""
    rd = lambda f: list(csv.DictReader([l for l in (PACK / f).open(newline='') if not l.startswith('#')]))
    meas = {r['row_id']: r for r in rd('lb_4b_measures.csv')}; out = {}
    for r in rd('lobbyist_contributions.csv'):
        m = meas.get(r['row_id'])
        if r['member_bioguide'] in bio and m and m['measure'] in ('named', 'firm_only'):
            out[(bio[r['member_bioguide']], int(m['registrant_id']), r['date'], int(float(r['amount_usd'])))] = (m['measure'], r['row_id'])
    return out


def main():
    look = '--look' in sys.argv
    wrong = [(m, h, want, call(m, h)) for m, h, want in CASES if call(m, h) != want]; assert not wrong, ('the honoree rule fails its own cases', wrong)
    members = [k for k, _, _ in L.MAP_MEMBERS]; assert set(members) == set(GIVEN), set(members) ^ set(GIVEN)
    bio = {b: k for k, b, _ in L.MAP_MEMBERS}
    W = B.windows(); its, dup, variants, folders = items(members); PM = pack_lines(bio)
    reg_years = {(int(m.group(1)), m.group(2)) for d in P.glob('lda-gov-contrib-reg*') if (d / 'meta.json').exists() for m in [re.match(r'lda-gov-contrib-reg(\d+)-(\d{4})$', d.name)] if m}
    need = {(rid, y) for (_, rid, _) in W for y in YEARS}
    print(f'saved pulls read: {dict(folders)}; registrant-years complete: {len(need & reg_years)} of {len(need)}')
    if need - reg_years:
        print('  NOT COMPLETE YET:', sorted(need - reg_years)[:8], '...' if len(need - reg_years) > 8 else '')
    print(f'LD-203 items naming one of the 24 as honoree: {len(its)} (repeats across pulls and amended reports dropped: {dup})')
    for m in members:
        c = variants[m]; yes = sorted(((h, n) for (h, v), n in c.items() if v == 'yes'), key=lambda x: -x[1]); no = sorted(((h, n) for (h, v), n in c.items() if v == 'no'), key=lambda x: -x[1])
        print(f'  {m:11} accepted {sum(n for _, n in yes):4d} in {len(yes):3d} spellings; refused {sum(n for _, n in no):4d} in {len(no):3d}')
        if look:
            for h, n in yes:
                print(f'      yes {n:4d}  {h[:110]!r}')
            for h, n in no:
                print(f'      NO  {n:4d}  {h[:110]!r}')
    if look:
        return
    rows, ids = [], {}
    for i in sorted(its, key=lambda i: (i['date'] or '', i['member'], str(i['lobbyist_id']))):
        for (co, rid, cl), x in W.items():
            day = i['date'] or ''
            if rid != i['registrant_id'] or not (x['from'] <= day and (not x['to'] or day <= x['to'])):
                continue
            pack_row = ''
            if i['lobbyist_id'] is None:
                measure = 'own_pac' if B.norm(x['name'])[:20] == B.norm(x['client'])[:20] else 'firm_pac'
            elif x['lobbyists'] is None:
                measure, pack_row = PM.get((i['member'], rid, day, int(float(i['amount_usd']))), ('firm_only_not_classified', ''))
            else:
                sp = x['lobbyists'].get(i['lobbyist_id'])
                measure = 'named' if sp and sp[0] <= day <= sp[1] else 'firm_only'
            rows.append({'item': '', 'side': co, 'member': i['member'], 'date': day, 'amount_usd': i['amount_usd'], 'measure': measure,
                         'registrant': x['name'], 'client': x['client'], 'registered_from': x['from'], 'registration_ended': x['to'],
                         'filer': i['filer_type'], 'lobbyist_no': '', '_lob': (co, i['lobbyist_id']) if i['lobbyist_id'] is not None else None, 'payee': i['payee'],
                         'honoree_as_written': i['honoree_as_written'], 'shared_event': 'yes' if B.SEVERAL.search(i['honoree_as_written']) else 'no',
                         'contribution_type': i['contribution_type'], 'report_year': i['report_year'], 'report_period': i['report_period'],
                         'report_url': i['report_url'], 'pack_row': pack_row, 'source': i['source'],
                         # whose money: a lobbyist's own (the report says SELF or gives the filer's own name) or a committee's that the report lists.
                         # The measure and the line's key are kept as first published, so no audited line changes its number; own_money says what counts.
                         'own_money': 'yes' if i['lobbyist_id'] is not None and i['whose'] == 'own' else 'no',
                         'contributor': '' if i['lobbyist_id'] is not None and i['whose'] == 'own' else ('the registrant itself' if i['contributor'].upper() == 'SELF' else i['contributor']),
                         'repeat_of': '', '_rid': rid, '_whose': i['whose'] if i['lobbyist_id'] is not None else 'registrant', '_contrib': i['contributor']})
    KEY = lambda r: '|'.join(str(r[k]) for k in ('side', 'member', 'date', 'amount_usd', 'measure', 'registrant', 'payee', 'honoree_as_written', 'report_url'))
    keys = [KEY(r) for r in rows]; assert len(set(keys)) == len(keys), 'two lines share a key'
    # ---- control A: the audited three-chairmen table
    old = list(csv.DictReader(open(R / 'lobbyist_gifts.csv', newline=''))); bykey = {KEY(r): r for r in rows}
    missing = [o['item'] for o in old if KEY(o) not in bykey]
    extra = [r for r in rows if r['member'] in ('mast', 'moolenaar', 'crawford') and KEY(r) not in {KEY(o) for o in old}]
    print(f'control A: {len(old)} lines of the audited three-chairmen table; found again here: {len(old) - len(missing)}; missing: {missing}')
    for r in extra:
        print(f'  A LINE FOR A CHAIRMAN THAT THE AUDITED TABLE LACKS: {r["side"]} {r["member"]} {r["date"]} ${float(r["amount_usd"]):,.0f} {r["measure"]} {r["registrant"][:30]} honoree={r["honoree_as_written"][:50]!r} {r["source"]}')
    assert not missing, 'control A failed'
    # lobbyist numbers: the audited table's numbers are kept for the same person; a new person takes the next free number of the side
    no = {}
    for o in old:
        r = bykey[KEY(o)]
        if r['_lob'] and o['lobbyist_no']:
            assert no.setdefault(r['_lob'], o['lobbyist_no']) == o['lobbyist_no'], 'one lobbyist, two numbers'
    regp = R / 'lobbyist_gifts_map_ids.csv'; reg = {}
    if regp.exists():
        reg = {r['key']: (r['item'], r['lobbyist_no']) for r in csv.DictReader(regp.open(newline=''))}
        for r, k in zip(rows, keys):
            if k in reg and r['_lob'] and reg[k][1]:
                assert no.setdefault(r['_lob'], reg[k][1]) == reg[k][1], 'one lobbyist, two registered numbers'
    used = set(no.values()) | {v[1] for v in reg.values() if v[1]}
    for r in rows:
        if r['_lob'] and r['_lob'] not in no:
            tag = B.TAG[r['_lob'][0]]; n = max([int(u.split('-')[1]) for u in used if u.startswith(tag + '-')] or [0]) + 1
            no[r['_lob']] = f'{tag}-{n}'; used.add(no[r['_lob']])
        r['lobbyist_no'] = no.get(r['_lob'], '') if r['_lob'] else ''
    used_item = {v[0] for v in reg.values()}
    for r, k in zip(rows, keys):
        if k not in reg:
            item = f"LM{max([int(u[2:]) for u in used_item] or [0]) + 1:04d}"; used_item.add(item); reg[k] = (item, r['lobbyist_no'])
        r['item'] = reg[k][0]
    gone = [v[0] for k, v in reg.items() if k not in set(keys)]; assert not gone, ('a registered line is no longer in the table', gone[:5])
    # ---- control B: the pack's lines for the same members and firms
    mine = {(r['member'], next(rid for (co, rid, cl), x in W.items() if co == 'network' and x['name'] == r['registrant'] and x['client'] == r['client']), r['date'], int(float(r['amount_usd'])))
            for r in rows if r['side'] == 'network' and r['filer'] != 'Registrant'}
    in_reach = {k for k in PM if any(co == 'network' and rid == k[1] for (co, rid, cl) in W) and '2024-01-01' <= k[2]}
    print(f'control B: the pack holds {len(in_reach)} lines for these 24 members at the firms and years pulled; found here: {len(in_reach & mine)}; '
          f'in the pack and not here: {len(in_reach - mine)}; here and not in the pack: {len(mine - in_reach)}')
    for k in sorted(in_reach - mine)[:12]:
        print('  pack only:', k, PM[k])
    for k in sorted(mine - in_reach)[:12]:
        print('  here only:', k)
    rows.sort(key=lambda r: r['item'])
    # a contributor the rule cannot place is decided by a reader, line by line; a campaign committee that carries the filer's surname would name
    # the lobbyist, so the table says what it is and not its name
    readp = R / 'lobbyist_contributor_read.tsv'
    read = {x['item']: x for x in csv.DictReader(readp.open(newline=''), delimiter='\t')} if readp.exists() else {}
    unread = []
    for r in rows:
        if r['_whose'] == 'unread':
            v = read.get(r['item'], {}).get('whose')
            if v not in ('own', 'committee'):
                unread.append(r['item']); continue
            r['own_money'] = 'yes' if v == 'own' else 'no'; r['contributor'] = '' if v == 'own' else 'a committee (read; its name would name the filer)'
        elif r['_whose'] == 'campaign':
            r['contributor'] = CARRIES
    assert not unread, ('lines whose contributor is neither SELF, the filer\'s own name nor a committee by the rule: read each and add it to ' + readp.name, unread)
    stale = sorted(set(read) - {r['item'] for r in rows if r['_whose'] == 'unread'}); assert not stale, ('a read verdict for a line that the rule now places by itself', stale)
    # a committee's gift that several lobbyists of one firm each list is one gift: later listings point at the first
    first = {}
    for r in rows:
        if r['own_money'] == 'no':
            assert r['_whose'] in ('registrant', 'committee', 'campaign') or r['item'] in read, ('a contributor that is neither the filer nor a committee', r['item'])
            assert r['_whose'] != 'registrant' or r['contributor'] == 'the registrant itself' or ORG.search(r['_contrib']), ('a registrant\'s line with an unplaced contributor', r['item'])
            k = (r['side'], r['_rid'], r['_contrib'].upper(), r['member'], B.norm(r['payee']), r['date'], r['amount_usd'])
            if k in first:
                r['repeat_of'] = first[k]
            else:
                first[k] = r['item']
    bad = [r['item'] for r in rows if r['measure'] in ('firm_pac', 'own_pac') and r['own_money'] == 'yes']; assert not bad, bad
    cols = [c for c in rows[0] if c not in ('_lob', '_rid', '_whose', '_contrib')]
    with regp.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['key', 'item', 'lobbyist_no']); w.writerows([k, v[0], v[1]] for k, v in sorted(reg.items(), key=lambda kv: kv[1][0]))
    with open(R / 'lobbyist_gifts_map.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore', lineterminator='\n'); w.writeheader(); w.writerows(rows)
    with open(R / 'lobbyist_gifts_map_summary.tsv', 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(['what', 'value'])
        w.writerows([('firms whose reports were read (registered for Nvidia, for Anthropic or for a group Open Philanthropy funds)', len({rid for (_, rid, _) in W})),
                     ('years of reports read', f'{YEARS[0]} to {YEARS[-1]}'), ('firm-years read in full', len(need & reg_years)),
                     ('contribution items naming one of the members drawn', len(its)), ('of them made while the firm was registered for the client', len(rows)),
                     ('members drawn', len(members)), ('first gift counted', min(r['date'] for r in rows)), ('last gift counted', max(r['date'] for r in rows))])
    print(f'items inside a registration window: {len(rows)} (shared events: {sum(r["shared_event"] == "yes" for r in rows)})')
    agg = defaultdict(lambda: [0, 0.0, set()])
    for r in rows:
        own = 'own money' if r['measure'] in ('named', 'firm_only', 'firm_only_not_classified') and r['own_money'] == 'yes' else "a committee's money"
        if r['repeat_of']:
            continue
        a = agg[(r['member'], r['side'], own)]; a[0] += 1; a[1] += float(r['amount_usd']); a[2].add(r['lobbyist_no'])
    for m in members:
        line = [f"{s} {o}: {agg[(m, s, o)][0]} items ${agg[(m, s, o)][1]:,.0f} ({len(agg[(m, s, o)][2] - {''})} people)" for s in ('nvidia', 'anthropic', 'network') for o in ('own money', "a committee's money") if (m, s, o) in agg]
        print(f'  {m:11} ' + ('; '.join(line) or 'no item inside a registration window'))


if __name__ == '__main__':
    main()
