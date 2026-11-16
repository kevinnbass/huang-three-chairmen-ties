"""Build the tables behind the member-tie figures (nv13 and the map's third version).
Run: python3 -I scripts/build_member_ties.py
Writes research/employee_gifts.csv   one row per counted FEC line: an individual who gave a company as employer, to a committee
                                     keyed to a sitting member (no donor names; `donor` is a hash used only to count people)
       research/employee_gift_rates.csv  per company: how many of the 535 sitting members received such a gift, and how much
       research/member_ties.csv      one row per documented tie between one of the 23 drawn members and Anthropic, its
                                     employees, or an organisation in its funding network; plus Nvidia's side where the
                                     same record exists for it (employees' gifts, lobbying reports on the same bills)
Sources: the FEC lines saved by fec_sched_a_employer.py (both companies, one method); the congress, lineage, toner and
evaluators packs; this project's bill and lobbying tables. Where a company's FEC pull is not finished, the Anthropic side
falls back to the congress pack's reviewed rows and the file says so (`basis` column).

What counts as an employee's gift: an itemised receipt of a committee keyed to a sitting member, from an individual, not a
memo line (memo lines repeat a gift: a joint committee's allocation, a redesignation), amount above zero. A gift earmarked
through a conduit is counted once, on the member committee's own line. Committees are keyed to members by the FEC
candidate id printed on the line, and, for joint fundraising committees and leadership PACs, by the congress pack's keys.
Nothing here names a donor, and nothing says why anyone gave."""
import csv, hashlib, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'research'; PRIMARY = R / 'primary'
PACK = Path('EVIDENCE_SETS')
sys.path.insert(0, str(ROOT / 'scripts'))
import rows_ledger as L, rows_map
csv.field_size_limit(10**9)
CYCLE = '2026'
XREF = 'lake-bioguide-fec-xref-20261113'
SIDES = [('anthropic', 'Anthropic'), ('nvidia', 'Nvidia')]
EMP_OK = {'anthropic': re.compile(r'^\s*ANTHROPIC\b', re.I), 'nvidia': re.compile(r'^\s*NVIDIA\b', re.I)}   # the employer as filed must begin with the company's name


def pack(path):
    f = open(PACK / path, newline='', errors='replace'); pos = f.tell(); first = f.readline()
    if not first.startswith('#'):
        f.seek(pos)
    return list(csv.DictReader(f))


def money(v):
    return f'${v:,.0f}'


def mon(d):
    M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    p = d.split('-'); return f'{M[int(p[1]) - 1]} {int(p[2])}, {p[0]}' if len(p) == 3 else (f'{M[int(p[1]) - 1]} {p[0]}' if len(p) == 2 else d)


def span(ds):
    a, b = min(ds), max(ds); M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    f = lambda d: f'{M[int(d[5:7]) - 1]} {d[:4]}'
    return mon(a) if a == b else (f(a) if f(a) == f(b) else f'{f(a)} to {f(b)}')


# Clients of lobbying firms, as the lobbyists' gift lines name them (audit of Nov 14, 2026: "the network" named no one)
NARROW_LOBBY_LINE = False       # the line from the congress set's narrower table of lobbyists' gifts; replaced by step 5b for all three sides (Nov 15, 2026)
LOBBY_CLIENT = [('ANTHROPIC', 'Anthropic'), ('OPEN PHILANTHROPY ACTION FUND', "Open Philanthropy's action fund"), ('AMERICANS FOR RESPONSIBLE INNOVATION', 'Americans for Responsible Innovation'),
                ('CENTER FOR AI SAFETY ACTION FUND', "the Center for AI Safety's action fund"), ('ENCODE AI', 'Encode AI (no Open Philanthropy award on record)'), ('FATHOM', 'Fathom (no grant on record here)'), ('FUTURE OF LIFE INSTITUTE', 'the Future of Life Institute'), ('IFP ACTION', 'IFP Action')]


def lobby_words(lc, LOB, usd, yrs):
    """The line for a member's lobbyist gifts: the clients, in the lobbying table, of the firms the givers' reports name."""
    by = {}
    for x in LOB:
        if x.get('registrant') and x.get('client'):
            by.setdefault(x['registrant'], set()).add(x['client'])
    found = set()
    for r in lc:
        m = re.search(r'registrant=(.+?)(?: id=|;|\||$)', r['note'] or ''); assert m, r['row_id']
        cl = by.get(m.group(1).strip(), set()); assert cl, (r['row_id'], 'the firm has no client in the lobbying table')
        for c in cl:
            k = [nice for key, nice in LOBBY_CLIENT if key in c.upper()]; assert len(k) == 1, c
            found.add(k[0])
    names = [nice for _, nice in LOBBY_CLIENT if nice in found]
    joined = names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]
    who = 'A lobbyist at a firm that has lobbied for' if len(lc) == 1 else 'Lobbyists at firms that have lobbied for'
    return f'{who} {joined}: {money(usd)} of their own money, {yrs}'


def main():
    MB = {r['member_bioguide']: r for r in pack('congress/research/members_network.csv')}
    sitting = {b for b, r in MB.items() if r['cohort'] == 'sitting'}; assert len(sitting) == 535
    HM = {r['row_id']: r for r in pack('congress/research/hard_money.csv')}
    LCON = {r['row_id']: r for r in pack('congress/research/lobbyist_contributions.csv')}
    LMAP = list(csv.DictReader(open(R / 'lobbyist_gifts_map.csv', newline='')))
    REGISTERED_KEYS = {r['key'] for r in csv.DictReader(open(R / 'member_tie_ids.csv', newline=''))} if (R / 'member_tie_ids.csv').exists() else set()
    LYEARS = {r['what']: r['value'] for r in csv.DictReader(open(R / 'lobbyist_gifts_map_summary.tsv', newline=''), delimiter='\t')}['years of reports read'] if (R / 'lobbyist_gifts_map.csv').exists() else []      # written by scripts/build_lobbyist_gifts_map.py
    RD = {r['row_id']: r for r in pack('congress/research/revolving_door.csv')}
    LOB = pack('congress/research/lobbying.csv')
    # ------------------------------------------------------------ committees -> members
    cand = {r['fec_candidate_id']: b for b, r in MB.items() if r['fec_candidate_id']}
    x = defaultdict(set)
    for r in json.loads((PRIMARY / XREF / 'rows.json').read_text()):
        if r['confidence'] in ('exact', 'multi') and r['bioguide_id']:
            x[r['cand_id']].add(r['bioguide_id'])
    for c, bs in x.items():
        if len(bs) == 1:
            cand.setdefault(c, next(iter(bs)))
    # the FEC's own committee-to-candidate links for the cycle (ccl) and committee names (cm), fetched for this figure
    CM = sorted(PRIMARY.glob('fec-bulk-committees-2026-*'))[-1]
    link = defaultdict(set); cname = {}; cmeta = {}
    for ln in subprocess.run(['unzip', '-p', str(CM / 'ccl26.zip')], capture_output=True, check=True).stdout.decode('utf-8', 'replace').splitlines():
        f = ln.split('|')                                           # CAND_ID, CAND_ELECTION_YR, FEC_ELECTION_YR, CMTE_ID, CMTE_TP, CMTE_DSGN, LINKAGE_ID
        if len(f) >= 6:
            link[f[3]].add((f[0], f[4], f[5]))
    for ln in subprocess.run(['unzip', '-p', str(CM / 'cm26.zip')], capture_output=True, check=True).stdout.decode('utf-8', 'replace').splitlines():
        f = ln.split('|')
        if len(f) >= 15:
            cname[f[0]] = f[1]; cmeta[f[0]] = (f[8], f[9], f[14])       # designation, type, candidate id
    pay = defaultdict(set); ptype = {}           # committees the congress pack keyed to one member (its reviewed keys): joint committees,
    for r in HM.values():                        # leadership PACs, and a member's new campaign committee for another office
        if r['member_bioguide'] and r['payee_id'] and r['payee_type'] in ('candidate_committee', 'jfc', 'leadership_pac'):   # never a party committee
            pay[r['payee_id']].add(r['member_bioguide']); ptype[r['payee_id']] = r['payee_type']
    pay = {k: next(iter(v)) for k, v in pay.items() if len(v) == 1}
    # a candidate id the bioguide table lacks (a member running for another office) takes the member the pack keyed its committee to
    for cm_, b_ in pay.items():
        if ptype[cm_] == 'candidate_committee':
            for c_, tp_, ds_ in link.get(cm_, ()):
                if ds_ in ('P', 'A'):
                    cand.setdefault(c_, b_)

    jkey = {}; jread = set()            # filled further down from the statements of organisation read

    def member_of(cmte):
        """(bioguide, kind) for a committee: a member's own campaign committee; a joint committee linked to that one candidate
        only; or a joint committee or leadership PAC the congress pack keyed to one member."""
        if cmte in jread:                                # its statement of organisation has been read: that reading decides
            return jkey.get(cmte, (None, ''))
        ls = link.get(cmte, set())
        own = {cand[c] for c, tp, ds in ls if ds in ('P', 'A') and tp in ('H', 'S', 'P') and c in cand}
        if len(own) == 1:
            return next(iter(own)), 'candidate committee'
        if ls and all(ds == 'J' for _, _, ds in ls) and len({c for c, _, _ in ls}) == 1:
            c = next(iter(ls))[0]
            if c in cand:
                return cand[c], 'joint committee or leadership PAC'
        if cmte in pay:
            return pay[cmte], 'candidate committee' if ptype[cmte] == 'candidate_committee' else 'joint committee or leadership PAC'
        if cmte in jkey:
            return jkey[cmte]
        return None, ''

    def nhash(last_first):
        """Surname and first given name, hashed: used only to match one donor's lines across two captures of the same report."""
        a, _, b_ = last_first.upper().partition(',')
        return hashlib.sha256((re.sub(r'[^A-Z]', '', a) + '|' + (re.sub(r'[^A-Z ]', '', b_).split() or [''])[0]).encode()).hexdigest()[:10]

    def dhash(last_first, zip5):
        return hashlib.sha256((re.sub(r'\s+(MR|MS|MRS|DR|JR|SR)\.?$', '', last_first.upper().strip()) + '|' + zip5[:5]).encode()).hexdigest()[:10]

    # ------------------------------------------------------------ employees' gifts, both companies, one rule
    # Source 1: the FEC's bulk file of itemised individual contributions (one file, both companies).
    # Source 2: the same lines paged from the FEC's API (newest first), used as the check on source 1 and for any line
    # the weekly bulk file does not hold yet.
    cands = []                                   # every line that passes the rule, from either source
    negs = {}                                    # the same rule's negative lines (refunds, chargebacks), by SUB_ID: not netted, listed
    BULK = sorted(PRIMARY.glob('fec-bulk-indiv26-employers-*'))
    bulk_meta = json.loads((BULK[-1] / 'meta.json').read_text()) if BULK else None
    if BULK:
        it = iter((BULK[-1] / 'lines.txt').read_text(encoding='utf-8').splitlines()); cols = next(it).split('|')
        for ln in it:
            r = dict(zip(cols, ln.split('|')))
            side = next((s_ for s_, _ in SIDES if EMP_OK[s_].search(r['EMPLOYER'])), None)
            if side and r['ENTITY_TP'] == 'IND' and r['MEMO_CD'] != 'X' and float(r['TRANSACTION_AMT'] or 0) < 0 and len(r['TRANSACTION_DT']) == 8:
                d_ = r['TRANSACTION_DT']; negs[r['SUB_ID']] = {'side': side, 'committee_id': r['CMTE_ID'], 'date': f'{d_[4:]}-{d_[:2]}-{d_[2:4]}', 'usd': float(r['TRANSACTION_AMT']), 'sub_id': r['SUB_ID'], 'source': BULK[-1].name}
            if side is None or r['ENTITY_TP'] != 'IND' or r['MEMO_CD'] == 'X' or float(r['TRANSACTION_AMT'] or 0) <= 0 or len(r['TRANSACTION_DT']) != 8:
                continue
            dt = r['TRANSACTION_DT']
            cands.append({'key': r['SUB_ID'], 'side': side, 'committee_id': r['CMTE_ID'], 'date': f'{dt[4:]}-{dt[:2]}-{dt[2:4]}', 'usd': float(r['TRANSACTION_AMT']), 'tran': r['TRAN_ID'],
                          'file': int(r['FILE_NUM'] or 0), 'employer_as_filed': r['EMPLOYER'], 'occupation': r['OCCUPATION'], 'donor': dhash(r['NAME'], r['ZIP_CODE']), 'dn': nhash(r['NAME']),
                          'source': BULK[-1].name, 'page': 'lines.txt', 'image': r['IMAGE_NUM']})
    api_done = {}
    for side, _ in SIDES:
        d = PRIMARY / f'fec-sched_a-employer-{side}-{CYCLE}'
        api_done[side] = (d / 'SUMMARY.json').exists()
        # the cycle's pages, then the later pulls of lines dated after them (folders ...-since-<day>-<pull day>)
        for d, f in [(d, f) for d in [d] + sorted(PRIMARY.glob(f'fec-sched_a-employer-{side}-{CYCLE}-since-*')) if d.is_dir() for f in sorted(d.glob('page-*.json'))]:
            for ln in json.loads(f.read_text()).get('results') or []:
                if not EMP_OK[side].search(ln.get('contributor_employer') or '') or (ln.get('entity_type') or 'IND') != 'IND':
                    continue
                if ln.get('memo_code') != 'X' and float(ln.get('contribution_receipt_amount') or 0) < 0 and ln.get('contribution_receipt_date'):
                    negs.setdefault(str(ln['sub_id']), {'side': side, 'committee_id': ln['committee_id'], 'date': ln['contribution_receipt_date'][:10], 'usd': float(ln['contribution_receipt_amount']), 'sub_id': str(ln['sub_id']), 'source': d.name})
                if ln.get('memo_code') == 'X' or float(ln.get('contribution_receipt_amount') or 0) <= 0 or not ln.get('contribution_receipt_date'):
                    continue
                cands.append({'key': ln['sub_id'], 'side': side, 'committee_id': ln['committee_id'], 'date': ln['contribution_receipt_date'][:10], 'usd': float(ln['contribution_receipt_amount']),
                              'tran': ln.get('transaction_id') or '', 'file': int(ln.get('file_number') or 0), 'employer_as_filed': ln.get('contributor_employer') or '', 'occupation': ln.get('contributor_occupation') or '',
                              'donor': dhash(ln.get('contributor_name') or '', ln.get('contributor_zip') or ''), 'dn': nhash(ln.get('contributor_name') or ''), 'source': d.name, 'page': f.name, 'image': str(ln.get('image_number') or '')})
    cn = {}
    for ln in subprocess.run(['unzip', '-p', str(CM / 'cn26.zip')], capture_output=True, check=True).stdout.decode('utf-8', 'replace').splitlines():
        f = ln.split('|')
        if len(f) >= 10:
            cn[f[0]] = (f[1], f[4], f[5])                           # name, state, office
    sur = defaultdict(set)
    for b in sitting:
        sur[(re.sub(r'[^A-Z]', '', MB[b]['member_name'].upper().replace(' JR.', '').replace(' III', '').split()[-1]), MB[b]['state'])].add(b)
    flags = Counter()
    # ---- joint fundraising committees and leadership PACs that the FEC links to no candidate (amendment A1 of
    # research/NV8_GAPS_REMEDIATION_SPEC.md, Nov 14, 2026). A leadership PAC belongs to the candidate its FEC record names as
    # sponsor. A joint committee is tied to a member only when exactly one sitting member is among the participants its
    # statement of organisation lists (through that member's campaign committee or leadership PAC) and every participant
    # could be read. One shared by several members is listed in research/joint_committees.csv and attributed to none.
    def member_by_candidate(c_):
        """(bioguide or None, sure): the sitting member a candidate id belongs to. A member running for another office has a new
        candidate id: it is taken as theirs when surname, state and the first three letters of a given name agree; a candidate
        who shares only a member's surname and state is not sure, and blocks the tie."""
        if c_ in cand:
            return (cand[c_] if cand[c_] in sitting else None), True
        nm = cn.get(c_)
        if not nm:
            return None, True
        same = sur.get((re.sub(r'[^A-Z]', '', nm[0].split(',')[0].upper()), nm[1]), set())
        given = [w for w in re.sub(r'[^A-Z ]', ' ', nm[0].upper().partition(',')[2]).split() if len(w) >= 3]
        hit = {b for b in same if any(w[:3] == g[:3] for g in given for w in re.sub(r'[^A-Z ]', ' ', MB[b]['member_name'].upper()).split()[:-1] if len(w) >= 3)}
        if len(hit) == 1:
            return next(iter(hit)), True
        return None, not same

    # three pulls of statements of organisation: committees that had no key at all (Nov 14); committees whose gifts sit only in the
    # FEC's API pulls; and joint committees that had been tied to a member by the FEC's link or the pack's review without a reading
    # of the statement (the last two found by the second audit, Nov 15, 2026)
    JP = [r for name in ('jfc_participants.csv', 'jfc_participants_api_only.csv', 'jfc_participants_keyed.csv') if (R / name).exists() for r in csv.DictReader(open(R / name, newline=''))]
    keyed_before = {r['committee_id']: r.get('keyed_to', '') for r in JP if r.get('keyed_to')}
    SP = {r['committee_id']: r['sponsor_candidate_ids'].split() for r in csv.DictReader(open(R / 'lpac_sponsors.csv', newline=''))} if (R / 'lpac_sponsors.csv').exists() else {}
    for r in JP:
        if r['designation'] == 'D':
            SP.setdefault(r['committee_id'], []).append(r['participant_id'])

    def participant(pid):
        """(what it is, bioguide or '', read) for one participant of a joint committee."""
        own = {cand[c_] for c_, tp, ds in link.get(pid, ()) if ds in ('P', 'A') and tp in ('H', 'S', 'P') and c_ in cand}
        if len(own) == 1:
            b = next(iter(own)); return 'campaign committee', (b if b in sitting else ''), True
        if pid not in cmeta:
            return 'not in the FEC committee list', '', False
        ds, tp, c_ = cmeta[pid]
        if ds in ('P', 'A'):
            b, sure = member_by_candidate(c_) if c_ else (None, False)
            return 'campaign committee', b or '', sure
        if ds == 'D':
            if pid not in SP:
                return 'leadership PAC', '', False
            bs = [member_by_candidate(s) for s in SP[pid]]
            got = {b for b, _ in bs if b}
            return 'leadership PAC', (next(iter(got)) if len(got) == 1 else ''), all(s for _, s in bs) and len(got) <= 1
        if tp in ('X', 'Y', 'Z'):
            return 'party committee', '', True
        if ds == 'J':
            return 'another joint committee', '', False
        return 'other committee', '', True

    JOINT = []
    byj = defaultdict(list)
    for r in JP:
        byj[r['committee_id']].append(r)
    for cid, ps in sorted(byj.items()):
        r0 = ps[0]
        if r0['designation'] == 'D':
            bs = [member_by_candidate(s) for s in SP.get(cid, [])]; got = {b for b, _ in bs if b}
            if len(got) == 1 and all(s for _, s in bs):
                jkey[cid] = (next(iter(got)), 'joint committee or leadership PAC'); out_ = 'tied to its sponsor'
            else:
                out_ = 'sponsor is not a sitting member' if all(s for _, s in bs) and not got else 'sponsor could not be settled'
            members = sorted(got); parts = []; unread = []
        else:
            parts = [(p['participant_id'], p['participant'], *participant(p['participant_id'])) for p in ps]
            members = sorted({b for _, _, _, b, _ in parts if b}); unread = [x for x in parts if not x[4]]
            if len(members) == 1 and not unread:
                jkey[cid] = (members[0], 'joint fundraising committee'); out_ = 'tied to the one sitting member among its participants'
            elif len(members) > 1:
                out_ = f'not attributed: {"at least " if unread else ""}{len(members)} sitting members share it'
            elif unread:
                out_ = 'not attributed: a participant could not be settled'
            else:
                out_ = 'no sitting member among its participants'
            jread.add(cid)
            was = keyed_before.get(cid, '')
            if was and jkey.get(cid, ('',))[0] != was:
                print(f'  A JOINT COMMITTEE TIED BEFORE ITS STATEMENT WAS READ NO LONGER COUNTS FOR {was}: {cid} {r0["committee"]}: {out_}; sitting members: {members}')
        JOINT.append({'committee_id': cid, 'committee': r0['committee'], 'kind': 'leadership PAC' if r0['designation'] == 'D' else 'joint fundraising committee', 'participants': len(parts) or '',
                      'sitting_members': '; '.join(MB[b]['member_name'] for b in members), 'outcome': out_, 'member_bioguide': jkey[cid][0] if cid in jkey else '',
                      'other_participants': '; '.join(sorted({cname.get(i, n_) for i, n_, _, b, _ in parts if not b})) if len(parts) <= 12 else f'{sum(1 for x in parts if not x[3])} other committees',
                      'not_settled': '; '.join(sorted(f'{cname.get(i, n_)} ({w})' for i, n_, w, _, s in parts if not s)),
                      'statement_of_organisation': r0['f1_file'], 'source': r0['source']})
    # a joint committee whose statement of organisation could not be read (filed on paper, or not served) is tied to no one:
    # the rule asks for the statement, and an earlier key (the FEC's link, the pack's review) does not stand in for it
    for name in ('jfc_participants_gaps.csv', 'jfc_participants_api_only_gaps.csv', 'jfc_participants_keyed_gaps.csv'):
        for g in (csv.DictReader(open(R / name, newline='')) if (R / name).exists() else ()):
            cid = g['committee_id']
            if cid in byj or cid in jread:
                continue
            was = member_of(cid)[0]; jread.add(cid)
            out_ = 'not attributed: its statement of organisation could not be read (' + ('filed on paper; the FEC queue does not serve the image' if 'paper' in g['what_failed'] else 'the record was not served') + ')'
            if was:
                print(f'  A JOINT COMMITTEE TIED BEFORE ITS STATEMENT WAS READ NO LONGER COUNTS FOR {was}: {cid} {cname.get(cid, g.get("committee", ""))}: {out_}')
            JOINT.append({'committee_id': cid, 'committee': cname.get(cid, g.get('committee', '')), 'kind': 'joint fundraising committee', 'participants': '', 'sitting_members': '', 'outcome': out_,
                          'member_bioguide': '', 'other_participants': '', 'not_settled': 'its statement of organisation', 'statement_of_organisation': '', 'source': ''})
    gifts, basis, unkeyed, seen = [], {}, Counter(), {}
    in_bulk = {c['key'] for c in cands if c['source'].startswith('fec-bulk')}; in_api = defaultdict(set)
    for c in cands:
        if not c['source'].startswith('fec-bulk'):
            in_api[c['side']].add(c['key'])
    for c in sorted(cands, key=lambda c: (not c['source'].startswith('fec-bulk'), c['key'])):      # the bulk file's copy of a line stands; the API adds only what it lacks
        b, kind = member_of(c['committee_id'])
        if b is None:
            for c_, tp_, ds_ in link.get(c['committee_id'], ()):
                nm = cn.get(c_)
                if nm and ds_ in ('P', 'A') and (re.sub(r'[^A-Z]', '', nm[0].split(',')[0].upper()), nm[1]) in sur:
                    flags[(c['side'], cname.get(c['committee_id'], ''), c_, nm[0], nm[1])] += 1
            ls = link.get(c['committee_id'], set())
            if any(ds in ('J', 'D') for _, _, ds in ls):
                unkeyed[(c['side'], cname.get(c['committee_id'], c['committee_id']))] += 1
            continue
        if b not in sitting or c['key'] in seen:
            continue
        k2 = (c['committee_id'], c['tran'] or c['key'])
        if k2 in seen and seen[k2]['file'] >= c['file']:
            continue                                             # an amended report repeats the line: the latest filing stands
        later = k2 in seen                                       # the API's copy is from a later filing of a line the bulk file also holds
        if k2 in seen:
            seen.pop(seen[k2]['key'], None)
        g = {**c, 'bioguide': b, 'committee_kind': kind, 'later': later}; seen[k2] = g; seen[c['key']] = g
    for g in {id(v): v for v in seen.values()}.values():
        gifts.append({'key': g['key'], 'side': g['side'], 'bioguide': g['bioguide'], 'member': L.KEY_MAP.get(g['bioguide'], ''), 'date': g['date'], 'usd': f"{g['usd']:.2f}", 'committee_id': g['committee_id'],
                      'committee': cname.get(g['committee_id'], ''), 'committee_kind': g['committee_kind'], 'employer_as_filed': g['employer_as_filed'], 'occupation': g['occupation'], 'donor': g['donor'], 'dn': g['dn'],
                      'source': g['source'], 'page': g['page'], 'note': 'a later filing of a line the bulk file also holds' if g['later'] else '',
                      'sub_id': g['key'], 'tran_id': g['tran'], 'file_num': str(g['file'] or ''), 'image_num': g['image']})
    for side, label in SIDES:
        mine = [g for g in gifts if g['side'] == side]
        if not BULK:
            basis[side] = 'not pulled yet'; continue
        nb = sum(g['source'].startswith('fec-bulk') for g in mine)
        basis[side] = (f'FEC lines from the commission\'s bulk file of itemised individual contributions for the {CYCLE} cycle (the file as downloaded on {bulk_meta["zip_saved_utc"][:10]}), '
                       f'{len(mine) - nb} newer line{"s" if len(mine) - nb != 1 else ""} added from its API')
        # check: the same rule applied to the API's pages must find the same lines
        a_ids = {g['key'] for g in mine if g['key'] in in_api[side]} | {c['key'] for c in cands if c['side'] == side and not c['source'].startswith('fec-bulk') and member_of(c['committee_id'])[0] in sitting}
        b_ids = {g['key'] for g in mine if g['source'].startswith('fec-bulk')}
        oldest = min((c['date'] for c in cands if c['side'] == side and not c['source'].startswith('fec-bulk')), default='')
        b_win = {g['key'] for g in mine if g['source'].startswith('fec-bulk') and g['date'] >= oldest} if oldest else set()
        print(f'check ({label}): API pages {"complete" if api_done[side] else "partial"}, reaching back to {oldest or "-"}; counted lines in that window: in both {len(a_ids & b_win)}, API only {len(a_ids - b_ids)}, bulk file only {len(b_win - a_ids)}')
    # the congress pack's reviewed Anthropic rows: a second check, on lines to Aug 11, 2026
    EMPNOTE = re.compile(r"employer as filed=\s*'?ANTHROPIC", re.I)
    packrows = defaultdict(list)
    for b in sitting:
        for i in MB[b]['t1_ids'].split():
            r = HM.get(i)
            if r and EMPNOTE.search(r['note']) and r['date'] >= '2025-01-01' and member_of(r['payee_id'])[0] == b:
                packrows[b].append(r)                              # the same committee rule as every other line
    if BULK:
        cut = max(r['date'] for rs in packrows.values() for r in rs)
        sub = lambda r: (re.search(r'sub_id=(\d+)', r['note']) or [None, ''])[1]
        # an amended report gives a line a new id, so the comparison is on committee, day and amount (as multisets).
        # The bulk file carries whole dollars (cents dropped: 143.56 is 143 there), so amounts are compared in whole dollars.
        whole = lambda v: int(float(v))
        pc = Counter((r['payee_id'], r['date'], whole(r['amount_usd'])) for rs in packrows.values() for r in rs if float(r['amount_usd']) > 0)
        oc = Counter((g['committee_id'], g['date'], whole(g['usd'])) for g in gifts if g['side'] == 'anthropic' and '2025-01-01' <= g['date'] <= cut)
        both = sum((pc & oc).values()); ponly = pc - oc; oonly = oc - pc
        print(f'check (Anthropic, against the congress pack\'s reviewed rows, Jan 2025 to {cut}, by committee, day and amount): in both {both}, congress pack only {sum(ponly.values())}, this build only {sum(oonly.values())}')
        print('   pack only, by committee:', Counter(cname.get(k[0], k[0])[:30] for k in ponly.elements()).most_common(6))
        print('   build only, by month:', sorted(Counter(k[1][:7] for k in oonly.elements()).items()), '| by committee:', Counter(cname.get(k[0], k[0])[:30] for k in oonly.elements()).most_common(5))
        gifts = [g for g in gifts if g['date'] >= '2025-01-01']
        for side, _ in SIDES:                                    # the basis line counts only lines that are counted (dated Jan 2025 or later)
            na = sum(1 for g in gifts if g['side'] == side and not g['source'].startswith('fec-bulk') and not g['note'])
            basis[side] = (f'FEC lines from the commission\'s bulk file of itemised individual contributions for the {CYCLE} cycle (the file as downloaded on {bulk_meta["zip_saved_utc"][:10]}), '
                           f'{na} line{"s" if na != 1 else ""} added from its API that the file does not hold')
        # A committee's amended report can drop the employer from a line. Where the congress pack captured a line with Anthropic
        # as employer (its saved FEC pages, pulled by Sep 2026) and today's FEC data shows no line for that donor, committee and
        # amount with that employer, the earlier capture is counted and marked. No such earlier capture exists for Nvidia.
        have = Counter((g['committee_id'], g['dn'], g['date'], whole(g['usd'])) for g in gifts if g['side'] == 'anthropic')
        donor_of = {}
        for g in gifts:
            donor_of.setdefault(g['dn'], g['donor'])
        added = Counter()
        for b, rs in packrows.items():
            for r in sorted(rs, key=lambda r: r['row_id']):
                if float(r['amount_usd']) <= 0:
                    continue
                k = (r['payee_id'], nhash(r['payer']), r['date'], whole(r['amount_usd']))
                if have[k] > 0:
                    have[k] -= 1; continue
                o = re.search(r'occupation=([^;]+);', r['note']); dn = nhash(r['payer'])
                gifts.append({'key': r['row_id'], 'side': 'anthropic', 'bioguide': b, 'member': L.KEY_MAP.get(b, ''), 'date': r['date'], 'usd': f"{float(r['amount_usd']):.2f}", 'committee_id': r['payee_id'],
                              'committee': r['payee'], 'committee_kind': 'candidate committee' if r['payee_type'] == 'candidate_committee' else 'joint committee or leadership PAC',
                              'employer_as_filed': (re.search(r'filed=\s*([^;|]+)', r['note']) or [0, 'ANTHROPIC'])[1].strip(), 'occupation': o.group(1) if o else '', 'donor': donor_of.get(dn, 'p' + dn[:9]), 'dn': dn,
                              'source': 'pack:congress/research/hard_money.csv#' + r['row_id'], 'page': '', 'note': 'employer given on an earlier capture of the report; not on the line in today\'s FEC data',
                              'sub_id': sub(r), 'tran_id': '', 'file_num': (re.search(r'FILE_NUM=(\d+)', r['note']) or [None, ''])[1], 'image_num': (re.search(r'fecimg/\?(\d+)', r['url']) or [None, ''])[1]})
                added[r['payee']] += 1
        print(f'lines counted from the earlier capture only (Anthropic): {sum(added.values())}', added.most_common(8))
        # Each such line is paired with the line the bulk file holds now (the amended report's: same donor, day and whole-dollar
        # amount, employer field empty), so both filings can be looked up. The file number in the pack's note is the amended report's.
        AM = sorted(PRIMARY.glob('fec-bulk-indiv26-banks-amended-*'))
        pool = defaultdict(list)
        if AM:
            it2 = iter((AM[-1] / 'lines.txt').read_text(encoding='utf-8').splitlines()); c2 = next(it2).split('|')
            for ln in it2:
                r = dict(zip(c2, ln.split('|'))); dt = r['TRANSACTION_DT']; assert r['EMPLOYER'] == ''
                pool[(r['CMTE_ID'], nhash(r['NAME']), f'{dt[4:]}-{dt[:2]}-{dt[2:4]}', whole(r['TRANSACTION_AMT']))].append(r)
        for g in sorted((g for g in gifts if g['note'].startswith('employer given')), key=lambda g: g['sub_id']):
            cand_ = sorted(pool.get((g['committee_id'], g['dn'], g['date'], whole(g['usd'])), []), key=lambda r: r['SUB_ID'])
            assert cand_, ('no amended line saved for', g['key'])
            r = cand_[0]; pool[(g['committee_id'], g['dn'], g['date'], whole(g['usd']))].remove(r)
            g['file_num'] = ''                                   # the original report's file number is not in the capture
            g['amended_sub_id'] = r['SUB_ID']; g['amended_file_num'] = r['FILE_NUM']; g['amended_image_num'] = r['IMAGE_NUM']
        for g in gifts:
            for k in ('amended_sub_id', 'amended_file_num', 'amended_image_num'):
                g.setdefault(k, '')
    else:
        for b, rs in packrows.items():                           # fallback while nothing is pulled: the pack's rows stand in, marked as such
            for r in rs:
                m = re.search(r'sub_id=(\d+)', r['note']); o = re.search(r'occupation=([^;]+);', r['note'])
                gifts.append({'key': m.group(1) if m else r['row_id'], 'side': 'anthropic', 'bioguide': b, 'member': L.KEY_MAP.get(b, ''), 'date': r['date'], 'usd': f"{float(r['amount_usd']):.2f}",
                              'committee_id': r['payee_id'], 'committee': r['payee'], 'committee_kind': 'candidate committee' if r['payee_type'] == 'candidate_committee' else 'joint committee or leadership PAC',
                              'employer_as_filed': 'ANTHROPIC', 'occupation': o.group(1) if o else '', 'donor': dhash(r['payer'], ''), 'dn': nhash(r['payer']), 'source': 'pack:congress/research/hard_money.csv#' + r['row_id'], 'page': '', 'note': '', 'sub_id': m.group(1) if m else '', 'tran_id': '', 'file_num': '', 'image_num': ''})
        basis['anthropic'] = 'the congress pack\'s reviewed rows (its FEC pull ends Aug 11, 2026); this figure\'s own pull was not finished'
    read_through = max(c['date'] for c in cands)             # the latest day any line read is dated (either company, any committee)
    if JOINT:
        tot = defaultdict(lambda: [0, 0.0]); seen_l = set()
        for c in sorted(cands, key=lambda c: (not c['source'].startswith('fec-bulk'), c['key'])):
            k_ = (c['committee_id'], c['tran'] or c['key'])
            if c['key'] in seen_l or k_ in seen_l or c['date'] < '2025-01-01':
                continue
            seen_l.add(c['key']); seen_l.add(k_); tot[(c['committee_id'], c['side'])][0] += 1; tot[(c['committee_id'], c['side'])][1] += c['usd']
        for j in JOINT:
            for side, _ in SIDES:
                j[f'{side}_lines'] = tot[(j['committee_id'], side)][0]; j[f'{side}_usd'] = f"{tot[(j['committee_id'], side)][1]:.2f}"
        with open(R / 'joint_committees.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(JOINT[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(sorted(JOINT, key=lambda j: (j['outcome'], j['committee'])))
        print('joint committees and leadership PACs read:', len(JOINT), dict(Counter(j['outcome'].split(':')[0] for j in JOINT)))
    ours = defaultdict(list)
    for g in gifts:
        ours[(g['side'], g['bioguide'])].append(g)
    gifts.sort(key=lambda g: (g['side'], g['member'] or 'zz', g['bioguide'], g['date'], g['key']))
    with open(R / 'employee_gifts.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(gifts[0].keys()) if gifts else ['key'], lineterminator='\n'); w.writeheader(); w.writerows(gifts)
    # Gifts through the conduits (ActBlue, WinRed) dated after the last candidate-committee line on file: the conduit's own line
    # is on file, the recipient committee's is not yet, and a gift is counted only on the recipient's line. Counted here so the
    # figure can say how much is waiting, and for whom among the members drawn.
    last_own = max((g['date'] for g in gifts if g['committee_kind'] == 'candidate committee'), default='')
    conduit = {s_: {'lines': 0, 'usd': 0.0, 'drawn': defaultdict(lambda: [0, 0.0])} for s_, _ in SIDES}
    for side, _ in SIDES:
        for d_ in sorted(PRIMARY.glob(f'fec-sched_a-employer-{side}-{CYCLE}-since-*')):
            for f_ in sorted(d_.glob('page-*.json')):
                for ln in json.loads(f_.read_text()).get('results') or []:
                    if ln.get('committee_id') not in ('C00401224', 'C00694323') or ln.get('memo_code') == 'X' or not EMP_OK[side].search(ln.get('contributor_employer') or ''):
                        continue
                    if (ln.get('contribution_receipt_date') or '')[:10] <= last_own:
                        continue
                    v_ = float(ln.get('contribution_receipt_amount') or 0); conduit[side]['lines'] += 1; conduit[side]['usd'] += v_
                    m_ = re.search(r'\((C\d{8})\)', ln.get('memo_text') or '')
                    b_ = member_of(m_.group(1))[0] if m_ else None
                    if b_ in L.KEY_MAP:
                        conduit[side]['drawn'][L.KEY_MAP[b_]][0] += 1; conduit[side]['drawn'][L.KEY_MAP[b_]][1] += v_
    NEG = []
    for n_ in sorted(negs.values(), key=lambda n_: (n_['side'], n_['date'], n_['sub_id'])):
        b_, _k = member_of(n_['committee_id'])
        if b_ in sitting:
            NEG.append({'side': n_['side'], 'member': L.KEY_MAP.get(b_, ''), 'bioguide': b_, 'date': n_['date'], 'usd': f"{n_['usd']:.2f}", 'committee_id': n_['committee_id'],
                        'committee': cname.get(n_['committee_id'], ''), 'sub_id': n_['sub_id'], 'source': n_['source']})
    rates = []
    for side, label in SIDES:
        tot = defaultdict(float)
        for g in gifts:
            if g['side'] == side:
                tot[g['bioguide']] += float(g['usd'])
        order = sorted(tot, key=lambda b: -tot[b]); mine = [g for g in gifts if g['side'] == side]
        neg_side = [n_ for n_ in NEG if n_['side'] == side]
        rates.append({'side': side, 'sitting_members': 535, 'members_with_a_gift': len(tot), 'usd': f'{sum(tot.values()):.2f}', 'lines': len(mine), 'donors': len({g['dn'] for g in mine}),
                      'negative_lines_not_netted': len(neg_side), 'negative_usd_not_netted': f"{sum(float(n_['usd']) for n_ in neg_side):.2f}",
                      'democrats': sum(MB[b]['party'] == 'D' for b in tot), 'republicans': sum(MB[b]['party'] == 'R' for b in tot),
                      'latest_line': max((g['date'] for g in mine), default=''), 'read_through': read_through, 'last_candidate_committee_line': last_own,
                      'conduit_lines_after': conduit[side]['lines'], 'conduit_usd_after': f"{conduit[side]['usd']:.2f}",
                      'conduit_after_drawn': ' '.join(f'{k}:{v[0]}:{v[1]:.2f}' for k, v in sorted(conduit[side]['drawn'].items())), 'basis': basis[side],
                      'ranks': ' '.join(f'{L.KEY[b]}:{order.index(b) + 1}' for b in order if b in L.KEY)})
    with open(R / 'employee_gift_rates.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rates[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(rates)
    with open(R / 'employee_gift_negatives.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['side', 'member', 'bioguide', 'date', 'usd', 'committee_id', 'committee', 'sub_id', 'source'], lineterminator='\n'); w.writeheader(); w.writerows(NEG)

    # ------------------------------------------------------------ the ties, member by member
    T = []

    def tie(member, typ, side, node, kind, words, panel, src, q, usd='', n='', first='', last='', draw='line'):
        src = src if isinstance(src, list) else [src]; q = q if isinstance(q, list) else [q]; assert len(src) == len(q), (member, typ)
        T.append({'key': f'{member}:{typ}:{side}', 'member': member, 'type': typ, 'side': side, 'node': node, 'kind': kind, 'draw': draw, 'usd': usd, 'n': n, 'first': first, 'last': last,
                  'words': words, 'panel': panel, 'src': ' || '.join(src), 'q': ' || '.join(q)})

    chip = list(csv.DictReader(open(R / 'chip_bills.csv', newline='')))
    rep = {(r['side'], r['bill']): r for r in csv.DictReader(open(R / 'lobbying_bill_reports.csv', newline=''))}
    pacs = {(r['member_bioguide'], r['pac']): r for r in csv.DictReader(open(R / 'pacs_by_member.csv', newline=''))}
    for key, bg, _ in L.MAP_MEMBERS:
        m = MB[bg]
        # 1. employees' own gifts, each company
        for side, label in SIDES:
            gs = ours.get((side, bg), [])
            if basis[side] == 'not pulled yet':
                continue
            if gs:
                usd = sum(float(g['usd']) for g in gs); nd = len({g['dn'] for g in gs}); ds = [g['date'] for g in gs]      # people are counted by name
                src = [g['source'] for g in gs]; q = [g['key'] if not g['source'].startswith('pack:') else g['committee'] for g in gs]
                jg = [g for g in gs if cmeta.get(g['committee_id'], ('',))[0] == 'J']; ju = sum(float(g['usd']) for g in jg); jn = sorted({g['committee'].title() for g in jg})      # every joint fundraising committee, however it was tied to the member
                tie(key, 'employee_gifts', side, f'{label} employees' if side == 'anthropic' else '', 'own',
                    f'{label} employees\' own gifts: {money(usd)} from {nd} {"person" if nd == 1 else "people"} · {span(ds)}' + (f'; {money(ju)} of it to a joint committee' if jg else ''),
                    f'{money(usd)} from {nd} {"person" if nd == 1 else "people"} who gave {label} as employer, in {len(gs)} contribution{"s" if len(gs) != 1 else ""}, {span(ds)}. Their own money, not the company\'s.'
                    + (f' {money(ju)} of it went to {"a joint fundraising committee" if len(jn) == 1 else "joint fundraising committees"} ({", ".join(jn)}) that the member shares with other committees; the FEC lines do not show how much of it reached the member\'s own campaign.' if jg else '')
                    + (f' {sum(1 for g in gs if g["note"].startswith("employer given"))} of these lines gave the employer on the committee\'s original report; its amended report leaves the field blank.' if any(g['note'].startswith('employer given') for g in gs) else ''),
                    src, q, usd=f'{usd:.2f}', n=str(nd), first=min(ds), last=max(ds), draw='line' if side == 'anthropic' else 'words')
            else:
                tie(key, 'employee_gifts', side, '', 'none', f'No gift from an {label} employee in FEC records, Jan 2025 to {mon(read_through)}', f'None on file from anyone who gave {label} as employer.',
                    'table:employee_gift_rates.csv#' + side, side, draw='words')
        # 2. the company PACs (this project's table, built from FEC filings through Sep 30, 2026)
        for side, pac, label in (('anthropic', 'anthropic', 'AnthroPAC'), ('nvidia', 'nvidia', 'Nvidia\'s PAC')):
            r = pacs.get((bg, pac))
            if r:
                when = mon(r['first_date']) if r['first_date'] == r['last_date'] else f'{r["lines"]} contributions, {mon(r["first_date"])} and {mon(r["last_date"])}' if r['lines'] == '2' else f'{r["lines"]} contributions, {mon(r["first_date"])} to {mon(r["last_date"])}'
                tie(key, 'company_pac', side, 'AnthroPAC' if side == 'anthropic' else '', 'money', f'{label}: {money(float(r["net_usd"]))} · {when}',
                    f'{label}, {"Anthropic" if side == "anthropic" else "Nvidia"}\'s own political committee, gave {money(float(r["net_usd"]))}{" on " + when if r["first_date"] == r["last_date"] else " in " + when}.', f'table:pacs_by_member.csv#{bg}:{pac}', r['net_usd'],
                    usd=r['net_usd'], n=r['lines'], first=r['first_date'], last=r['last_date'], draw='held' if side == 'anthropic' else 'words')
        # 3. the PAC of Americans for Responsible Innovation
        ari = [HM[i] for i in m['t2_ids'].split() if i in HM and 'RESPONSIBLE INNOVATION' in HM[i]['payer']]
        if ari:
            usd = sum(float(r['amount_usd']) for r in ari); ds = [r['date'] for r in ari]
            fec_ = [r for r in ari if r['source_type'] != 'lda_api']; lda_ = [r for r in ari if r['source_type'] == 'lda_api']
            ari_words = f'Americans for Responsible Innovation\'s PAC: {money(usd)} · {span(ds)}'
            if fec_ and lda_:          # two disclosure systems may report the same gift: never add them (audit of Nov 14, 2026)
                ari_words = (f'Americans for Responsible Innovation\'s PAC: {money(sum(float(r["amount_usd"]) for r in fec_))} in FEC records · {span([r["date"] for r in fec_])}; a lobbying-disclosure report separately lists '
                             f'{money(sum(float(r["amount_usd"]) for r in lda_))} on {mon(lda_[0]["date"])}, which may be the same gifts')
            tie(key, 'ari_pac', 'network', rows_map.ARI, 'money', ari_words,
                f'The PAC of Americans for Responsible Innovation (ARI) gave {money(usd)} ({span(ds)}).',
                ['pack:congress/research/hard_money.csv#' + r['row_id'] for r in ari], [r['payee'] for r in ari], usd=f'{usd:.2f}', n=str(len(ari)), first=min(ds), last=max(ds))
        # 4. lobbying reports naming a chip-export bill he sponsors, both companies
        for b in chip:
            if b['sponsor_bioguide'] != bg:
                continue
            a = rep.get(('anthropic', b['bill'])); nv = rep.get(('nvidia', b['bill']))
            if not a and not nv:
                continue
            na = int(a['reports']) if a else 0; nn = int(nv['reports']) if nv else 0
            src = [f'table:lobbying_bill_reports.csv#{s}:{b["bill"]}' for s, r_ in (('anthropic', a), ('nvidia', nv)) if r_] + [f'table:chip_bills.csv#{b["key"]}']
            q = [r_['reports'] for r_ in (a, nv) if r_] + [bg]
            tw = L.TITLE_WORDS.get(b['family']); gloss = ''
            if tw and tw[0] == b['key']:                         # the official title's own words, from the bill record
                gloss = f' Its official title includes the words "{tw[1]}".'; src.append(b['source']); q.append(tw[1])
            tie(key, 'lobbying:' + b['key'], 'both', 'Anthropic' if na else '', 'lobby', f'His {b["bill"]} ({b["family"]}) is named in {na} Anthropic lobbying report{"s" if na != 1 else ""} and {nn} of Nvidia\'s',
                f'{b["bill"]}, the {b["family"]}, which he sponsors (introduced {mon(b["introduced"])}), is named in {na} lobbying report{"s" if na != 1 else ""} filed for Anthropic and {nn} filed for Nvidia.{gloss} '
                f'A report names a bill; it does not say which office was contacted or what was asked.', src, q, n=f'{na}/{nn}', draw='line' if na else 'words')
        # 5. lobbyists' own gifts (second-hand: the client did not direct them)
        lc = [LCON[i] for i in m['t4b_ids'].split() if i in LCON]
        if lc and NARROW_LOBBY_LINE:
            usd = sum(float(r['amount_usd']) for r in lc); ds = [r['date'] for r in lc]
            yrs = min(ds)[:4] if min(ds)[:4] == max(ds)[:4] else f'{min(ds)[:4]}–{max(ds)[:4]}'
            lsrc = ['pack:congress/research/lobbyist_contributions.csv#' + r['row_id'] for r in lc]; lq = [r['amount_usd'] for r in lc]
            ptxt = f'{money(usd)} in {len(lc)} gift{"s" if len(lc) != 1 else ""} from lobbyists\' own pockets, {yrs}, made while their firms were registered for a client in the network. Second-hand: no client directed them.'
            if len(lc) <= 2 and all(re.search(r'registrant=(.+?) id=', r['note']) for r in lc):   # few enough to say which firm and which client
                parts = []; ok_ = True; lsrc0, lq0 = list(lsrc), list(lq)
                for r in lc:
                    reg = re.search(r'registrant=(.+?) id=', r['note']).group(1)
                    nice = lambda c: 'Anthropic' if c.upper().startswith('ANTHROPIC') else {'OPEN PHILANTHROPY ACTION FUND': 'Open Philanthropy Action Fund', 'AMERICANS FOR RESPONSIBLE INNOVATION': 'Americans for Responsible Innovation (ARI)'}.get(c, c)
                    firsts = {}                                  # per client (by its plain name): the firm's earliest filing on file
                    for x in LOB:
                        if x['registrant'] == reg and x['client'] and (nice(x['client']) not in firsts or x['date'] < firsts[nice(x['client'])]['date']):
                            firsts[nice(x['client'])] = x
                    then = sorted(c for c, x in firsts.items() if x['date'] <= r['date']); later = sorted((x['date'], c) for c, x in firsts.items() if x['date'] > r['date'])
                    if not then or any(c not in ('Anthropic', 'Open Philanthropy Action Fund', 'Americans for Responsible Innovation (ARI)') for c in firsts):
                        ok_ = False; break                       # no client on file at the gift date: keep the general wording
                    firm = re.sub(r'\s*\(.*?\)|\s+LLC\b', '', reg).title()
                    parts.append(f'{money(float(r["amount_usd"]))} on {mon(r["date"])} from a lobbyist at {firm}, a firm then registered to lobby for {" and ".join(then)}'
                                 + ''.join(f' (and, from {mon(d_[:7])}, for {c})' for d_, c in later) + '.')
                    lsrc += ['pack:congress/research/lobbyist_contributions.csv#' + r['row_id']] + ['pack:congress/research/lobbying.csv#' + firsts[c]['row_id'] for c in then + [c for _, c in later]]
                    lq += ['registrant=' + reg] + [firsts[c]['client'] for c in then + [c for _, c in later]]
                if ok_:
                    ptxt = ' '.join(parts) + ' The lobbyist\'s own money: no client directed it.'
                else:
                    lsrc, lq = lsrc0, lq0
            tie(key, 'lobbyist_gifts', 'network', '', 'none', lobby_words(lc, LOB, usd, yrs),
                ptxt, lsrc, lq, usd=f'{usd:.2f}', n=str(len(lc)), first=min(ds), last=max(ds), draw='words')
        # 5b. lobbyists' own gifts, one record and one rule for the three sides (research/lobbyist_gifts_map.csv, reports of 2020 to 2026):
        # gifts made while the lobbyist's firm was registered for the client; both measures are said. A firm registered for two clients
        # puts one gift on two sides, so the sides are never added up. Until the last reading of Nov 15, 2026 the row showed Nvidia's
        # firms from this table beside an earlier and narrower line for Anthropic's and the groups' (step 5, now off).
        for side in ('anthropic', 'network', 'nvidia'):
            OWN_ = ('named', 'firm_only', 'firm_only_not_classified')
            # a lobbyist's own money only: a committee's contribution that a lobbyist's report lists (the firm's PAC, a PAC the lobbyist serves)
            # is kept in the table and not counted here (the ninth reading, Nov 16, 2026: 54 such lines had been counted, 27 pac_gifts listed up to three times)
            sm = [r for r in LMAP if r['member'] == key and r['side'] == side and r['measure'] in OWN_ and r['own_money'] == 'yes']
            pac_rows = [r for r in LMAP if r['member'] == key and r['side'] == side and r['measure'] in OWN_ and r['own_money'] == 'no']
            pac_note = ''
            if pac_rows:
                pac_gifts = [r for r in pac_rows if not r['repeat_of']]; pusd = sum(float(r['amount_usd']) for r in pac_gifts)
                pac_note = (f' Not counted here: {money(pusd)} in {len(pac_gifts)} contribution{"" if len(pac_gifts) == 1 else "s"} of a political committee that those lobbyists\' reports list '
                            f'({len(pac_rows)} listing{"" if len(pac_rows) == 1 else "s"}); until Nov 16, 2026 this line counted them as lobbyists\' own money.')
            if not sm and pac_rows and f'{key}:lobbyist_gifts:{side}' in REGISTERED_KEYS:
                what = {'network': 'one of the groups', 'anthropic': 'Anthropic', 'nvidia': 'Nvidia'}[side]
                tie(key, 'lobbyist_gifts', side, '', 'none', f'No gift of a lobbyist\'s own money on file from a firm registered for {what}, 2020–2026',
                    f'The lobbyists\' contribution reports of 2020 to 2026 show no gift of a lobbyist\'s own money to this member from a firm then registered for {what}.' + pac_note,
                    ['table:lobbyist_gifts_map.csv#' + r['item'] for r in pac_rows], [r['amount_usd'] for r in pac_rows], draw='words')
                continue
            if not sm:
                # a line an audit has read is never dropped: where the earlier, narrower line has no gift under the common rule, the row says so
                if f'{key}:lobbyist_gifts:{side}' in REGISTERED_KEYS:
                    what = {'network': 'one of the groups', 'anthropic': 'Anthropic', 'nvidia': 'Nvidia'}[side]
                    moved = [r for r in LMAP if r['member'] == key and r['side'] != side and r['measure'] in OWN_ and r['own_money'] == 'yes']
                    assert moved, (key, side, 'a registered lobbyist line has no gift on any side of the shared table')
                    tie(key, 'lobbyist_gifts', side, '', 'none', f'No gift on file from a lobbyist at a firm registered for {what}, 2020–2026',
                        f'The lobbyists\' contribution reports of 2020 to 2026 show no gift to this member from a lobbyist at a firm then registered for {what}. A gift shown on this line before is counted on the line of the client the firm was registered for.',
                        ['table:lobbyist_gifts_map.csv#' + r['item'] for r in moved], [r['amount_usd'] for r in moved], draw='words')
                continue
            if side == 'network':
                cl = sorted({nice_ for r in sm for k_, nice_ in LOBBY_CLIENT if k_ in r['client'].upper()}); assert cl, (key, {r['client'] for r in sm})
                who = cl[0] if len(cl) == 1 else ', '.join(cl[:-1]) + ' and ' + cl[-1]; short = 'those clients' if len(cl) > 1 else 'that client'
            else:
                who = short = side.capitalize()
            usd = sum(float(r['amount_usd']) for r in sm); ds = [r['date'] for r in sm]; nm_ = [r for r in sm if r['measure'] == 'named']; nusd = sum(float(r['amount_usd']) for r in nm_)
            yrs = min(ds)[:4] if min(ds)[:4] == max(ds)[:4] else f'{min(ds)[:4]}–{max(ds)[:4]}'
            one = len(sm) == 1
            listed = (f'{money(nusd)} of it from lobbyists listed for {short} then' if nm_ and len(nm_) < len(sm) else f'all of it from lobbyists listed for {short} then' if nm_ else f'none of it from a lobbyist listed for {short} then')
            tie(key, 'lobbyist_gifts', side, '', 'none', f'{"A lobbyist at a firm" if one else "Lobbyists at firms"} registered for {who}: {money(usd)} of their own money, {yrs}; {listed}',
                f'{money(usd)} in {len(sm)} gift{"" if one else "s"} from lobbyists\' own pockets, {yrs}, made while their firms were registered to lobby for {who}; {listed}. Second-hand: no client directed them.' + pac_note,
                ['table:lobbyist_gifts_map.csv#' + r['item'] for r in sm], [r['amount_usd'] for r in sm], usd=f'{usd:.2f}', n=str(len(sm)), first=min(ds), last=max(ds), draw='words')
    # 6. ties that rest on one named record each
    RDP = 'pack:congress/research/revolving_door.csv#'
    for member, kind, rid, passage, when in L.STAFF:
        if kind == 'horizon':
            yrs = when.replace('-', '–')
            tie(member, 'fellow:' + rid, 'network', rows_map.HORIZON, 'post' if '2026' in when or '2025' in when else 'past', f'A Horizon fellow placed in his office, {yrs}',
                f'Horizon Institute for Public Service lists a fellow placed in his office, {yrs}.', RDP + rid, passage, first=when[:4])
        else:
            tie(member, 'council:' + rid, 'anthropic', 'Anthropic', 'past', 'His former national security adviser sits on Anthropic\'s advisory council (announced Aug 27, 2025)',
                'His former national security adviser is a member of Anthropic\'s national security advisory council, announced Aug 27, 2025.', RDP + rid, passage, first=when)
    r = RD['RD1229']; tie('moolenaar', 'fellow:RD1229', 'network', rows_map.HORIZON, 'post', 'A Horizon AI fellow placed with the committee he chairs, 2025–26',
                           'Horizon Institute for Public Service lists an AI fellow placed with the House Select Committee on the CCP, which he chairs, for 2025–26.', RDP + 'RD1229', r['org_now'], first='2025')
    r = RD['RD1233']; tie('mast', 'fellow:RD1233', 'network', rows_map.HORIZON, 'post', 'A Horizon nuclear fellow placed with the committee he chairs, 2025–26',
                           'Horizon Institute for Public Service lists a fellow (nuclear track) placed with the House Foreign Affairs Committee, which he chairs, for 2025–26.', RDP + 'RD1233', r['org_now'], first='2025')
    tie('moolenaar', 'witness', 'anthropic', 'Jack Clark', 'meet', 'Jack Clark testified before the committee he chairs · Jun 25, 2025',
        'Jack Clark, Anthropic\'s co-founder, testified before the House Select Committee on the CCP on Jun 25, 2025, at the hearing "Algorithms and Authoritarians: Why U.S. AI Must Lead". He chairs the committee.',
        ['pack:congress/research/travel.csv#TV2012', 'house-hrg-zs00-20250625-transcript'], ['Algorithms and Authoritarians: Why U.S. AI Must Lead', 'STATEMENT OF MR. JACK CLARK'], first='2025-06-25')
    # Anthropic's chief executive before a subcommittee one of the 23 chaired (the transcript names who presided)
    tie('blumenthal', 'witness', 'anthropic', 'Anthropic', 'meet', 'Anthropic\'s chief executive testified at a hearing he chaired · Jul 25, 2023',
        'Dario Amodei, Anthropic\'s chief executive, testified on Jul 25, 2023 at "Oversight of A.I.: Principles for Regulation", a hearing of the Senate Judiciary Subcommittee on Privacy, Technology, and the Law. He chaired the subcommittee and presided.',
        ['pack:congress/research/travel.csv#TV1977', 'govinfo-chrg-118shrg53503'], ['Amodei, Dario, chief executive officer, Anthropic', 'Hon. Richard Blumenthal, Chair of the Subcommittee, presiding'], first='2023-07-25')
    # witnesses from groups Open Philanthropy has funded, before subcommittees of the committee Mast has chaired since Jan 2025 (words only)
    TV = {r['row_id']: r for r in pack('congress/research/travel.csv')}
    GRT = pack('congress/research/grants.csv')
    hw = sorted((r for r in TV.values() if r['source_type'] in ('congress_gov_api', 'govinfo_chrg') and r['sponsor'].startswith('House Foreign Affairs') and r['date'] >= '2025-01-03'), key=lambda r: r['date'])
    ORGS = [('Center for a New American Security', 'Center for a New American Security'), ('Carnegie Endowment for International Peace', 'Carnegie Endowment'), ('Foundation for American Innovation', 'Foundation for American Innovation')]
    org_of = lambda r: next((short for full, short in ORGS if full in r['traveler_role']), None)
    assert hw and all(org_of(r) for r in hw), [r['row_id'] for r in hw if not org_of(r)]
    gsrc, gq = [], []
    for full, short in ORGS:
        gr = sorted((g for g in GRT if g['payer'] == 'Coefficient Giving' and g['payee'] == full), key=lambda g: g['date'])
        assert gr, full
        gsrc.append('pack:congress/research/grants.csv#' + gr[-1]['row_id']); gq.append(full)
    cnt = Counter(org_of(r) for r in hw); chipr = [r for r in hw if 'Export Control Loopholes' in r['event']]; assert len(chipr) == 1
    nword = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight'}[len(hw)]
    nword3 = {1: 'one', 2: 'two', 3: 'three'}[len(cnt)]
    tie('mast', 'net_witness', 'network', '', 'none', f'{nword} people from groups Open Philanthropy has funded were listed as witnesses for subcommittees of his committee, {span([r["date"] for r in hw])}',
        f'{nword} witnesses from {nword3} groups Open Philanthropy has funded (' + ', '.join(f'{short} {cnt[short]}' for _, short in ORGS if cnt[short]) + f') testified to House Foreign Affairs subcommittees, {span([r["date"] for r in hw])}. '
        f'One hearing, on {mon(chipr[0]["date"])}, was "Export Control Loopholes: Chipmaking Tools and their Subcomponents". None of the witnesses was from Anthropic.',
        ['pack:congress/research/travel.csv#' + r['row_id'] for r in hw] + gsrc, [r['sponsor'] for r in hw] + gq, n=str(len(hw)), first=hw[0]['date'], last=hw[-1]['date'], draw='words')
    tie('moolenaar', 'advisor', 'network', rows_map.IFP, 'post', 'An Institute for Progress fellow is described as senior advisor to his committee (Jul 2025)',
        'A Georgetown CSET event page of Jul 16, 2025 describes Saif Khan as "a Distinguished Fellow at the Institute for Progress and a Senior Advisor to the U.S. House Select Committee on the CCP."',
        'pack:toner/research/people_graph.csv#TGR910', 'a Senior Advisor to the U.S. House Select Committee on the CCP', first='2025-07-16')
    tie('moolenaar', 'left:RD056', 'network', rows_map.ARI, 'past', 'A former policy assistant of his committee now works at Americans for Responsible Innovation',
        'Americans for Responsible Innovation lists a policy analyst who is a "Former Policy Assistant with the House Select Committee on the CCP". The page gives no dates of service.',
        RDP + 'RD056', RD['RD056']['prior_org'])
    tie('moolenaar', 'left:WPE3178', 'network', '', 'none', 'A former senior staff member of his committee now heads an institute at the Center for AI Safety (Jun 2026)',
        'The Center for AI Safety\'s release of Jun 2, 2026 names as head of its Frontier Security Institute a former Senior Professional Staff Member of the House Select Committee on the Chinese Communist Party. It gives no dates of service.',
        'pack:evaluators-deep/research/people_edges.csv#WPE3178', 'Senior Professional Staff Member of the House Select Committee on the Chinese Communist Party', first='2026-06-02', draw='words')
    tie('mast', 'aide', 'network', '', 'none', 'A former legislative assistant of his lobbied for Open Philanthropy\'s action fund in 2025, on foreign aid',
        'A lobbyist registered in early 2025 for Open Philanthropy Action Fund, on foreign assistance, lists "Legislative Assistant, Rep. Brian Mast" among past posts.',
        'pack:congress/research/lobbying.csv#LB323', 'Legislative Assistant, Rep. Brian Mast', first='2025', draw='words')
    # the group's ads as run: Google's political-ads report, each ad's own page with frames of the video, and, for an ad aimed
    # at zip codes, the Census Bureau's table of zip-code areas by district
    GA = 'google-political-ads-pfa-20260916'
    adrows = [r for r in csv.DictReader(open(PRIMARY / GA / 'creative-stats.csv', newline='', errors='replace')) if r['Advertiser_Name'] == 'Public First Action Inc']
    cz = [l.split('|') for l in (PRIMARY / 'census-cd119-zcta-20261113' / 'tab20_cd11920_zcta520_natl.txt').read_text(encoding='utf-8-sig').splitlines()[1:]]
    zctas = lambda cd: {l[8] for l in cz if l[1] == cd and l[8]}
    fzip = lambda r: set(re.findall(r'(\d{5}),Florida', r['Geo_Targeting_Included']))
    for member, pid, pick, where, name, extra in (
            ('moolenaar', 'google-ads-creative-mi2-20261113', lambda r: r['Geo_Targeting_Included'].startswith('MI-2 '), 'his district (MI-2)', 'John Moolenaar', None),
            ('mast', 'google-ads-creative-fl21-20261113', lambda r: fzip(r) and fzip(r) == zctas('1221'),
             f'{len(zctas("1221"))} Florida zip codes: every zip-code area that lies wholly or partly in his district (FL-21), by the Census Bureau\'s table', 'Brian Mast', 'census-cd119-zcta-20261113')):
        rs = [r for r in adrows if pick(r)]; assert len(rs) == 1, (member, len(rs))
        r = rs[0]; lo, hi = (int(x) for x in r['Impressions'].split('-')); d0, d1 = r['Date_Range_Start'], r['Date_Range_End']
        frames = (PRIMARY / pid / 'text.txt').read_text(); up = name.upper()
        q1 = f'CONGRESSMAN {up} BACKING LEGISLATION TO PUT EXPORT CONTROLS ON ADVANCED CHIPS'; q2 = f'CALL CONGRESSMAN {up} TELL HIM TO KEEP FIGHTING TO KEEP ADVANCED CHIPS FROM GOING TO OUR ENEMIES'
        assert q1 in frames and q2 in frames and r['Ad_ID'] in frames and 'PAID FOR BY PUBLIC FIRST ACTION' in frames
        src = [GA, GA, GA, pid, pid, pid] + ([extra] if extra else []); q = ['Ad_ID=' + r['Ad_ID'], 'Date_Range_Start=' + d0, 'Impressions=' + r['Impressions'], q1, q2, 'PAID FOR BY PUBLIC FIRST ACTION'] + (['Congressional District 21'] if extra else [])
        tie(member, 'ad_run', 'anthropic', 'Public First Action', 'ad', f'Public First Action: a video ad naming him, aimed at his district, ran · {mon(d0)} to {mon(d1)}',
            f'A 30-second video by Public First Action ran from {mon(d0)} to {mon(d1)}, aimed at {where}. Google\'s political-ads report gives {lo:,} to {hi:,} showings and '
            f'${int(r["Spend_Range_Min_USD"]):,} to ${int(r["Spend_Range_Max_USD"]):,} spent. On screen: "Congressman {name} backing legislation to put export controls on advanced chips" and '
            f'"Call Congressman {name}. Tell him to keep fighting to keep advanced chips from going to our enemies."',
            src, q, n=r['Num_of_Days'], first=d0, last=d1, draw='words')
    T.sort(key=lambda t: ([k for k, _, _ in L.MAP_MEMBERS].index(t['member']), t['type'], t['side']))
    # Row ids are registered (research/member_tie_ids.csv, seeded on Nov 15, 2026 from the table two audits had read): a line keeps
    # its id whatever is added around it, a new line takes the next free number, and a registered line may not vanish.
    regp = R / 'member_tie_ids.csv'
    reg = {r['key']: r['row_id'] for r in csv.DictReader(open(regp, newline=''))}
    gone = sorted(set(reg) - {t['key'] for t in T}); assert not gone, ('a registered member line is no longer built', gone)
    for t in T:
        if t['key'] not in reg:
            reg[t['key']] = f"TY{max(int(v[2:]) for v in reg.values()) + 1:03d}"; print('  new member line:', reg[t['key']], t['key'])
    assert len(set(reg.values())) == len(reg), 'two member lines share an id'
    with open(regp, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['key', 'row_id']); w.writerows(sorted(reg.items(), key=lambda kv: kv[1]))
    T = [{'row_id': reg[t['key']], **t} for t in T]                           # the id rides in the table, so a subset keeps its ids
    with open(R / 'member_ties.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(T[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(T)
    # the header facts of the three-chairmen figure, as a table (so the figure builds from tables alone)
    import member_mentions, rows_ties
    n_pages, hit = member_mentions.count_pages(); actors = {a[0]: a for a in rows_map.ACTORS}      # nv13 keeps its count of pages of the first census; the map counts articles
    with open(R / 'nv13_members.csv', 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['key', 'bioguide', 'name', 'role', 'pages_naming', 'pages_total'])
        for k in rows_ties.THREE:
            w.writerow([k, L.BG[k], actors[k][2], actors[k][3], len(hit[actors[k][2].split()[-1]]), n_pages])
    # the key of the three-chairmen figure: how each group named in the panels connects to Anthropic, one record per line.
    # Award totals are recomputed here from the evidence sets' yearly rows.
    FA = {r['row_id']: r for r in pack('lineage/research/flows_annual.csv')}
    GRT_ = {r['row_id']: r for r in pack('congress/research/grants.csv')}
    LINP = 'pack:lineage/research/'; CONP = 'pack:congress/research/'
    def award(ids, tbl, payer_ok, payee):
        rs = [tbl[i] for i in ids]
        for r in rs:
            assert payer_ok(r.get('from_name') or r.get('payer')) and payee.lower() in (r.get('to_name') or r.get('payee')).lower(), (r['row_id'], payee)
        ys = sorted((r.get('year') or r['date'])[:4] for r in rs); tot = sum(float(r['amount_usd']) for r in rs)
        return f'${tot / 1e6:,.1f}M in award{"s" if len(rs) != 1 else ""}, {ys[0] if ys[0] == ys[-1] else ys[0] + "–" + ys[-1][2:]}', tot
    isop = lambda n: n in ('Open Philanthropy / Coefficient Giving', 'Coefficient Giving')
    faq = lambda ids: ([LINP + 'flows_annual.csv#' + i for i in ids], ['Open Philanthropy / Coefficient Giving'] * len(ids))
    grq = lambda ids, payee: ([CONP + 'grants.csv#' + i for i in ids], [payee] * len(ids))
    ari_w, _ = award(['FA014', 'FA015'], FA, isop, 'Americans for Responsible Innovation')
    ifp_w, _ = award(['FA132', 'FA133', 'FA134'], FA, isop, 'Institute for Progress')
    cais_w, _ = award(['FA033', 'FA034'], FA, isop, 'Center for AI Safety')
    cnas_w, _ = award(['FA045', 'FA046', 'FA047', 'FA048', 'FA049', 'FA050'], FA, isop, 'Center for a New American Security')
    car_ids = sorted(i for i, r in GRT_.items() if r['payer'] == 'Coefficient Giving' and r['payee'] == 'Carnegie Endowment for International Peace')
    fai_ids = sorted(i for i, r in GRT_.items() if r['payer'] == 'Coefficient Giving' and r['payee'] == 'Foundation for American Innovation')
    car_w, _ = award(car_ids, GRT_, isop, 'Carnegie Endowment for International Peace'); fai_w, _ = award(fai_ids, GRT_, isop, 'Foundation for American Innovation')
    hz = FA['FA849']; assert hz['from_name'] == 'Good Ventures Foundation' and 'Horizon' in hz['to_name'] and hz['year'] == '2023'
    K = []
    def klink(id_, card, label, words, src, q):
        src = src if isinstance(src, list) else [src]; q = q if isinstance(q, list) else [q]; assert len(src) == len(q), id_
        K.append({'id': id_, 'card': card, 'label': label, 'words': words, 'src': ' || '.join(src), 'q': ' || '.join(q)})
    klink('article', 'context', '', 'An article on X on Nov 12, 2026 said "Anthropic\'s people overlap with the think tanks, ex-officials and forums behind this coverage."',
         'x-dream1984-article', "Anthropic's people overlap with the think tanks, ex-officials and forums behind this coverage")
    klink('anthropic', 'anthropic', 'Anthropic', 'An AI company. It says it supports "smart export controls on AI chips".', 'anthropic-pfa-1', 'Supporting smart export controls on AI chips')
    klink('employees', 'anthropic', 'Its employees', 'A gift from an employee is that person\'s own money. The FEC record shows the employer the donor wrote down.',
         'table:employee_gift_rates.csv#anthropic', str(next(r['members_with_a_gift'] for r in rates if r['side'] == 'anthropic')))
    klink('anthropac', 'anthropic', 'AnthroPAC', 'Anthropic\'s own political committee, registered with the FEC on Apr 3, 2026.',
         [CONP + 'timeline.csv#TL111'] * 2, ['naming Anthropic PBC as the connected organization', '2026-04-03'])
    klink('lobbyists', 'anthropic', 'Its lobbyists', 'Anthropic and the firms it hires report each quarter which bills they lobbied on.',
         'table:lobbying_bill_reports.csv#anthropic:H.R. 6875', rep[('anthropic', 'H.R. 6875')]['reports'])
    klink('clark', 'anthropic', 'Jack Clark', 'A co-founder of Anthropic and its head of policy.', CONP + 'travel.csv#TV2012', 'Co-Founder and Head of Policy; Anthropic')
    klink('pfa', 'pfa', 'Public First Action', 'An advocacy group. Anthropic gave it $40 million in 2026 and says the money cannot be used to influence any candidate\'s election.',
         ['anthropic-pfa-2', 'anthropic-pfa-2'], ['bringing our total support to $40 million', 'cannot be used to influence the election of any candidate'])
    klink('pfa_carson', 'pfa', '', 'One of its founders, Brad Carson, is also the president of Americans for Responsible Innovation (ARI).',
         [CONP + 'entities.csv#EN2202', 'art-pfa-conservative'], ['Co-Founder & President, Americans for Responsible Innovation', 'Brad Carson, co-founder of Public First Action'])
    klink('op', 'op', 'Open Philanthropy', 'A grant-maker, now called Coefficient Giving. It is a separate organisation from Anthropic. Three records link the two:',
         LINP + 'flows_annual.csv#FA014', 'Open Philanthropy / Coefficient Giving')
    klink('op_1', 'op', '', 'Dustin Moskovitz, one of its directors, invested in Anthropic\'s Series A funding round in 2021.',
         [CONP + 'interlocks.csv#80', LINP + 'equity.csv#EQ011'], ['DUSTIN MOSKOVITZ', 'Dustin Moskovitz, the Center for Emerging Risk Research'])
    klink('op_2', 'op', '', 'Luke Muehlhauser, who leads its grants on AI governance and policy, sat on Anthropic\'s board until May 2024.',
         [LINP + 'tenures.csv#T1798', LINP + 'tenures.csv#T1798', LINP + 'tenures.csv#T1536'],
         ['Luke Muehlhauser has decided to step down from his Board role to focus on his work at Open Philanthropy', '2024-05-29', 'He leads our grantmaking on AI governance and international policy'])
    klink('op_3', 'op', '', 'Holden Karnofsky, its former chief executive, joined Anthropic\'s staff in Jan 2025.',
         [LINP + 'tenures.csv#T022', LINP + 'tenures.csv#T142'], ['He served as Open Philanthropy’s CEO and then co-CEO until 2023', 'joined Anthropic last month'])
    klink('ari', 'op_group', 'Americans for Responsible Innovation (ARI)', f'An advocacy group with its own PAC. {ari_w}.', *faq(['FA014', 'FA015']))
    klink('horizon', 'op_group', 'Horizon Institute for Public Service',
         f'Places fellows in congressional offices and committees. ${float(hz["amount_usd"]) / 1e6:,.1f}M in 2023 from Good Ventures Foundation, which Open Philanthropy\'s tax return lists as a related organisation.',
         [LINP + 'flows_annual.csv#FA849', CONP + 'interlocks.csv#214'], ['Good Ventures Foundation', 'GOOD VENTURES FOUNDATION'])
    klink('ifp', 'op_group', 'Institute for Progress', f'{ifp_w}.', *faq(['FA132', 'FA133', 'FA134']))
    klink('cais', 'op_group', 'Center for AI Safety', f'{cais_w}.', *faq(['FA033', 'FA034']))
    cs, cq = faq(['FA045', 'FA046', 'FA047', 'FA048', 'FA049', 'FA050'])
    klink('cnas', 'op_group', 'Center for a New American Security (CNAS)', f'{cnas_w}. Its chief executive, Richard Fontaine, was named in Jun 2025 to the trust that will elect most of Anthropic\'s board.',
         cs + ['art-anthropic-fontaine', 'anthropic-ltbt'], cq + ['today announced the appointment of Richard Fontaine', 'the Trust will elect a majority of the board within 4 years'])
    klink('carnegie', 'op_group', 'Carnegie Endowment for International Peace', f'{car_w}.', *grq(car_ids, 'Carnegie Endowment for International Peace'))
    klink('fai', 'op_group', 'Foundation for American Innovation', f'{fai_w}.', *grq(fai_ids, 'Foundation for American Innovation'))
    klink('opaf', 'op_group', 'Open Philanthropy Action Fund', 'A related body with the same president as Open Philanthropy. It hires lobbying firms.',
         [CONP + 'interlocks.csv#30', CONP + 'interlocks.csv#38', CONP + 'lobbying.csv#LB312'], ['CARI TUNA', 'CARI TUNA', 'OPEN PHILANTHROPY ACTION FUND'])
    with open(R / 'nv13_links.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(K[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(K)
    print('key lines:', len(K), '|', ari_w, '|', ifp_w, '|', cais_w, '|', cnas_w, '|', car_w, '|', fai_w)
    # every committee that holds a counted line, with the member it is tied to and on what basis
    seenc = {}
    for g in gifts:
        c = g['committee_id']
        if c in seenc:
            continue
        ls = link.get(c, set())
        own = {cand[c_] for c_, tp, ds in ls if ds in ('P', 'A') and tp in ('H', 'S', 'P') and c_ in cand}
        if len(own) == 1:
            basis_ = 'FEC committee-candidate link: the candidate\'s principal or authorised committee'
        elif ls and all(ds == 'J' for _, _, ds in ls) and len({c_ for c_, _, _ in ls}) == 1 and next(iter(ls))[0] in cand:
            basis_ = 'FEC committee-candidate link: a joint fundraising committee linked to this one candidate'
        elif c in jkey and c not in pay:
            basis_ = ('the committee\'s statement of organisation (FEC Form 1) lists this member\'s committee and no other sitting member\'s among its participants' if g['committee_kind'] == 'joint fundraising committee'
                      else 'the committee\'s FEC record names this member as the sponsor of the leadership PAC')
        else:
            basis_ = 'keyed to the member in the congress evidence set (its reviewed rows), committee type ' + ptype.get(c, '')
        seenc[c] = {'committee_id': c, 'committee': g['committee'], 'bioguide': g['bioguide'], 'member_name': MB[g['bioguide']]['member_name'], 'party': MB[g['bioguide']]['party'],
                    'chamber': MB[g['bioguide']]['chamber'], 'state': MB[g['bioguide']]['state'], 'kind': g['committee_kind'], 'basis': basis_,
                    'fec_candidate_ids_linked': ' '.join(sorted({c_ for c_, _, _ in ls}))}
    with open(R / 'committee_keys.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(next(iter(seenc.values())).keys()), lineterminator='\n'); w.writeheader(); w.writerows(sorted(seenc.values(), key=lambda r: (r['member_name'], r['committee_id'])))
    print('committees holding a counted line:', len(seenc), dict(Counter(r['basis'][:34] for r in seenc.values())))
    print(f'gifts: {len(gifts)} lines | basis: {basis}')
    for r in rates:
        print(f"  {r['side']}: {r['members_with_a_gift']} of 535 sitting members, ${float(r['usd']):,.0f}, {r['lines']} lines, {r['donors']} donors, latest {r['latest_line']} (D {r['democrats']}, R {r['republicans']})")
    print('ties:', len(T), dict(Counter(t['type'].split(':')[0] + '/' + t['side'] for t in T)))
    if flags:
        print('NOT KEYED, but the candidate shares a sitting member\'s surname and state (check by hand):', flags.most_common(20))
    if unkeyed:
        print('joint or leadership committees not keyed to a member (lines):', unkeyed.most_common(12))


if __name__ == '__main__':
    main()
