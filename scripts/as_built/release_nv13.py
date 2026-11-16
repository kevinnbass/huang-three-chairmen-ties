"""Assemble the public copy of everything behind the three-chairmen figure (nv13).
Run: python3 scripts/release_nv13.py <target folder>
Writes into the target folder (created if missing; files of the same name are replaced, nothing is removed):
  figures/    the figure as .html, .png, .jpg
  research/   the tables the figure is drawn from, the gift lines with their FEC identifiers, one evidence line per cited source
  sources/    copies of the sources that can be copied (official records, the group's ads as frames, the committees' letters)
  audit/      the two independent audit rounds (round1/, round2/): brief, report, findings, recount; and the disposition of every finding
  scripts/    the figure code, a builder and a verifier that run on this copy, and the scripts as they were run (as_built/)
  README.md, CHANGES.md
No donor and no lobbyist is named anywhere in the copy: the script scans every file for the names it knows and stops on a hit.
It then rebuilds the figure inside the copy (the HTML must equal the project's) and runs the copy's own verifier.
Nothing here pushes anywhere."""
import csv, hashlib, json, re, shutil, subprocess, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'research'; PRIMARY = R / 'primary'
PACK = Path('EVIDENCE_SETS'); LANES = {'round1': Path('audit/round1'), 'round2': Path('audit/round2'),
                                                'round3': Path('audit/round3')}
sys.path.insert(0, str(ROOT / 'scripts'))
import nv13_public as P, rows_ties as T, rows_chairmen as C, member_mentions
csv.field_size_limit(10**9)
PRIVATE = re.compile(r'(a pattern for local paths, a session id and addresses; left out of this copy)')
NAMED_IN_FIGURE = {'CLARK JACK', 'KHAN SAIF', 'MOSKOVITZ DUSTIN', 'MUEHLHAUSER LUKE', 'KARNOFSKY HOLDEN', 'FONTAINE RICHARD', 'CARSON BRAD', 'AMODEI DARIO', 'HUANG JENSEN', 'TUNA CARI',
                   'MAST BRIAN', 'MOOLENAAR JOHN', 'CRAWFORD RICK', 'SACKS DAVID', 'COTTON TOM'}
COPIES = {  # saved originals copied into sources/: official records, or the builder's own captures and readings
    'house-hfac-letter-pr': 'sources/house-foreign-affairs-release-nov5.txt', 'x-chinaselect-letter': 'sources/select-committee-post-nov12.txt',
    'x-chinaselect-letter-image': 'sources/select-committee-letter-nov12.txt',
    'google-political-ads-pfa-20260916': 'sources/google-political-ads-pfa-20260916.csv', 'census-cd119-zcta-20261113': 'sources/census-cd119-zcta-fl21.txt',
    'google-ads-creative-mi2-20261113': 'sources/ads/moolenaar-mi2.txt', 'google-ads-creative-fl21-20261113': 'sources/ads/mast-fl21.txt',
    'google-ads-creative-mi2-v2-20261113': 'sources/ads/moolenaar-mi2-second-version.txt', 'google-ads-creative-fl21-v2-20261113': 'sources/ads/mast-fl21-second-version.txt',
    'google-ads-creative-ar-20261113': 'sources/ads/arkansas-1.txt', 'google-ads-creative-ar2-20261113': 'sources/ads/arkansas-2.txt',
    'google-ads-political-search-nvidia-20261113': 'sources/google-political-ads-search/search.txt',
    'house-hrg-zs00-20250625-clark-statement': 'sources/hearing-20250625-clark-written-statement.txt', 'house-hrg-zs00-20250625-transcript': 'sources/hearing-20250625-transcript.txt',
    'fec-bulk-weball26-20261113': 'sources/fec-candidate-totals-three-chairmen.txt', 'fec-committee-c00583161-20261113': 'sources/fec-committee-C00583161.txt',
    'fec-filings-c30003586-20261114': 'sources/fec-filings-C30003586-public-first-action.txt',
    'art-sia-members': 'sources/trade-groups/sia-members.txt', 'art-iti-members': 'sources/trade-groups/iti-members.txt', 'art-technet-members-all': 'sources/trade-groups/technet-members.txt'}
FEC_REFS = ('fec-bulk-indiv26-employers-20261113', 'fec-sched_a-employer-anthropic-2026', 'fec-sched_a-employer-nvidia-2026')


def scrub(t):
    t = t.replace('research/primary', 'research/primary').replace('audit/round3', 'audit/round3').replace('audit/round2', 'audit/round2').replace('audit/round1', 'audit/round1')
    t = t.replace('lanes', 'lanes').replace('STORE', 'STORE')
    t = t.replace('EVIDENCE_SETS', 'EVIDENCE_SETS').replace('DOWNLOADS', 'DOWNLOADS')
    # (replacements of local paths; left out of this copy)
    # (replacements of local paths; left out of this copy)
    return t


def put(Tg, rel, text):
    f = Tg / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text, encoding='utf-8'); return f


def table(Tg, rel, rows, fields, delimiter=','):
    f = Tg / rel; f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter=delimiter, lineterminator='\n', extrasaction='ignore'); w.writeheader(); w.writerows(rows)


def private_names():
    """Every donor's and lobbyist's name the builder ever read, as (SURNAME, FIRST) pairs: the copy must hold none of them."""
    raw = set()
    for d in ('fec-bulk-indiv26-employers-20261113', 'fec-bulk-indiv26-banks-amended-20261113'):
        it = iter((PRIMARY / d / 'lines.txt').read_text(encoding='utf-8').splitlines()); cols = next(it).split('|')
        raw.update(dict(zip(cols, l.split('|')))['NAME'] for l in it)
    for d in sorted(x.name for x in PRIMARY.glob('fec-sched_a-employer-*') if x.is_dir()):       # every pull of employer lines, the later ones included
        for f in sorted((PRIMARY / d).glob('page-*.json')):
            raw.update((r.get('contributor_name') or '') for r in json.loads(f.read_text()).get('results') or [])
    for path, col in (('congress/research/hard_money.csv', 'payer'), ('congress/research/lobbyist_contributions.csv', 'payer')):
        raw.update(r[col] for r in P._pack(path) if r.get('payer_type') == 'individual')
    for path, col in (('congress/research/revolving_door.csv', 'person'), ('evaluators-deep/research/people_edges.csv', 'person')):
        raw.update(r.get(col) or '' for r in P._pack(path))
    for r in P._pack('congress/research/lobbying.csv'):
        raw.update(x.strip() for x in re.split(r'[;|]', r.get('lobbyists') or ''))
    for d in sorted(PRIMARY.glob('lda-gov-contrib-*')):
        for f in sorted(d.glob('page-*.json')):
            for r in json.loads(f.read_text())['results']:
                lb = r.get('lobbyist') or {}
                raw.add(f"{lb.get('last_name') or ''}, {lb.get('first_name') or ''}"); raw.add(r.get('contact_name') or ''); raw.add((r.get('registrant') or {}).get('contact_name') or '')
                raw.update((it.get('contributor_name') or '') for it in r.get('contribution_items') or [] if lb)
    for d in sorted(PRIMARY.glob('lda-gov-*-20*')):
        if (d / 'body.json').exists() and 'contrib' not in d.name:
            for r in json.loads((d / 'body.json').read_text())['results']:
                raw.add(r.get('posted_by_name') or ''); raw.add((r.get('registrant') or {}).get('contact_name') or '')
                for a_ in r.get('lobbying_activities') or []:
                    raw.update(f"{l['lobbyist'].get('last_name') or ''}, {l['lobbyist'].get('first_name') or ''}" for l in a_.get('lobbyists') or [])
    public = set(NAMED_IN_FIGURE)                      # sitting members and bill sponsors are public officials, named in the public tables
    for fname, col in (('committee_keys.csv', 'member_name'), ('pacs_by_member.csv', 'member'), ('pac_lines.csv', 'member')):
        for r in csv.DictReader(open(R / fname, newline='')):
            w = [x for x in re.sub(r"[^A-Z '-]", ' ', (r[col] or '').upper()).split() if x not in ('JR', 'SR', 'II', 'III', 'IV')]
            if len(w) >= 2:
                public.add(f'{w[-1]} {w[0]}')
    for r in csv.DictReader(open(R / 'chip_bill_backers.csv', newline='')):
        for v in r.values():
            m = re.match(r"(?:Rep|Sen)\. ([A-Za-z' -]+), ([A-Za-z'-]+)", v or '')
            if m:
                public.add(f'{m.group(1).upper()} {m.group(2).upper()}')
    pairs = set(); ORG = re.compile(r'\b(PAC|LLC|LLP|INC|CORP|CORPORATION|COMMITTEE|ASSOCIATION|ASSOCIATES|FUND|GROUP|FEDERAL|COMPANY|PARTNERS|STRATEGIES|SELF|NONE)\b')
    for n in raw:
        if ORG.search(n.upper()):                      # an organisation written where a person's name goes (a firm's PAC as contributor)
            continue
        n = re.sub(r'\b(MR|MS|MRS|DR|JR|SR|II|III|IV|PHD|MD|ESQ|SEN|REP|HON|SENATOR|REPRESENTATIVE|CONGRESSMAN|CONGRESSWOMAN)\b\.?', ' ', n.upper())   # a title is not a first name
        if ',' in n:
            a, b = n.split(',', 1); last = re.sub(r'[^A-Z \'-]', '', a).strip(); first = (re.sub(r'[^A-Z \'-]', '', b).split() or [''])[0]
        else:
            w = re.sub(r'[^A-Z \'-]', '', n).split(); last, first = (w[-1], w[0]) if len(w) >= 2 else ('', '')
        if len(last) >= 2 and len(first) >= 2 and f'{last} {first}' not in public:
            pairs.add((last, first))
    return pairs


def name_hits(Tg, pairs):
    by_last = {}
    for last, first in pairs:
        by_last.setdefault(last, set()).add(first)
    hits = []
    for f in sorted(Tg.rglob('*')):
        if not f.is_file() or '.git' in f.parts or '__pycache__' in f.parts or f.suffix in ('.png', '.jpg'):
            continue
        t = f.read_text(encoding='utf-8', errors='replace').upper(); words = set(re.findall(r"[A-Z'-]{2,}", t))
        for last in words & set(by_last):
            for first in by_last[last] & words:
                if re.search(rf"\b{re.escape(first)}\b[\s.A-Z]{{0,12}}\b{re.escape(last)}\b|\b{re.escape(last)}\b,?\s+{re.escape(first)}\b", t):
                    hits.append((str(f.relative_to(Tg)), f'{first[0]}. {last[0]}.'))
    return hits


def main(target):
    Tg = Path(target).resolve(); Tg.mkdir(parents=True, exist_ok=True)
    assert not str(Tg).startswith(str(ROOT)), 'the public copy must not sit inside the project folder'
    # ---------------------------------------------------------------- scripts that run on the copy
    for name in ('fig_ties.py', 'rows_ties.py', 'rows_chairmen.py', 'nv13_status.py', 'fig_common.py', 'build_nv13.py', 'verify_nv13.py'):
        t = (ROOT / 'scripts' / name).read_text()
        if name == 'fig_common.py':
            a = t.index('"""'); b = t.index('"""', a + 3) + 3
            t = ('"""Shared render and tokens for the figure: warm paper background, spaced-caps kicker, bold title, grey subtitle,\n'
                 'legend chips, footnote under a rule. Row ids ride only in an HTML comment.\n'
                 'The page grows to fit its content; the PNG is cut at the measured height."""') + t[b:]
        if name == 'rows_ties.py':
            t = t.replace('(rows of the\ncongress, lineage, toner and evaluators packs; FEC lines saved for this project; this project\'s bill and lobbying tables)',
                          '(rows of the builder\'s evidence sets; FEC lines; the bill and lobbying tables in research/)')
        t = scrub(t); assert not PRIVATE.search(t), (name, PRIVATE.search(t).group(0)); put(Tg, f'scripts/{name}', t)
    # the scripts as they were run: they need the builder's evidence sets and FEC downloads, so they do not run on this copy
    for name in ('build_member_ties.py', 'build_lobbyist_gifts.py', 'build_lobbyist_gifts_map.py', 'build_chairmen.py', 'lda_contributions.py', 'save_v3_records.py', 'reextract_members.py', 'fec_bulk_employer.py', 'fec_sched_a_employer.py', 'nv13_public.py', 'make_audit_nv13.py',
                 'member_mentions.py', 'release_nv13.py'):
        t = scrub((ROOT / 'scripts' / name).read_text())
        t = re.sub(r"PRIVATE = re\.compile\(.*\n", "PRIVATE = re.compile(r'(a pattern for local paths, a session id and addresses; left out of this copy)')
        t = re.sub(r"(?m)^\s*t = t\.replace\('/mnt.*\n|^\s*t = re\.sub\(r'/home.*\n|^\s*t = re\.sub\(r'Owner: nvidia.*\n", "    # (replacements of local paths; left out of this copy)\n", t)
        m = PRIVATE.search(t); assert not m, (name, t[max(0, m.start() - 60):m.end() + 40])
        put(Tg, f'scripts/as_built/{name}', t)
    # ---------------------------------------------------------------- tables
    gifts = P.public_gifts()
    for g in gifts:
        g['fec_page_url'] = 'https://docquery.fec.gov/cgi-bin/fecimg/?' + g['image_num']; g['amended_fec_page_url'] = ('https://docquery.fec.gov/cgi-bin/fecimg/?' + g['amended_image_num']) if g['amended_image_num'] else ''
    ck = {r['committee_id']: r for r in csv.DictReader(open(R / 'committee_keys.csv', newline=''))}
    for g in gifts:
        g['member_name'] = ck[g['committee_id']]['member_name']; g['party'] = ck[g['committee_id']]['party']
    cols = P.GIFT_COLS[:3] + ['member_name', 'party'] + P.GIFT_COLS[3:] + ['fec_page_url', 'amended_fec_page_url']
    table(Tg, 'research/employee_gifts.csv', gifts, cols)
    ref = lambda s: ('evidence-set:' + s[5:].split('#')[0].split('/')[0] + '/' + Path(s[5:].split('#')[0]).stem + '#' + s.split('#', 1)[1]) if s.startswith('pack:') else (('research/' + s[6:]) if s.startswith('table:') else s)
    for name, rows in (('nv13_ties.csv', C.ties()), ('nv13_key.csv', C.key()), ('nv13_stake.csv', C.stake()), ('nv13_events.csv', C.events()), ('nv13_numbers.csv', list(C.numbers().values()))):
        out = [{**r, 'src': ' || '.join(r['src']), 'q': ' || '.join(r['q'])} for r in rows]          # the checker's own references stay as they are: the copy's tables keep them
        table(Tg, f'research/{name}', out, list(out[0].keys()))
    for name in ('nv13_glance.csv', 'lobbyist_gifts.csv', 'trade_pac_gifts.csv'):
        t = (R / name).read_text(); assert not PRIVATE.search(t), (name, PRIVATE.search(t).group(0)); put(Tg, f'research/{name}', t)
    (Tg / 'research' / 'nv13_frames').mkdir(parents=True, exist_ok=True)
    for f in sorted((R / 'nv13_frames').glob('*.png')):
        shutil.copyfile(f, Tg / 'research' / 'nv13_frames' / f.name)
    for name in ('employee_gift_rates.csv', 'committee_keys.csv', 'nv13_members.csv', 'pacs_by_member.csv', 'pac_base_rates.csv', 'pac_lines.csv', 'chip_bills.csv', 'chip_bill_backers.csv', 'lobbying_bill_reports.csv', 'lobbying_filings.csv'):
        t = (R / name).read_text(); assert not PRIVATE.search(t), (name, PRIVATE.search(t).group(0)); put(Tg, f'research/{name}', t)
    # the grant rows behind the key's totals
    gr = []
    for k in C.key():
        for s_ in k['src']:
            if s_.startswith('pack:') and ('flows_annual' in s_ or 'grants.csv' in s_) and k['id'] != 'op':
                path, key = s_[5:].split('#', 1); r = P.pack_row(path, key)
                gr.append({'link': k['id'], 'source_ref': ref(s_), 'funder': r.get('from_name') or r.get('payer'), 'recipient': r.get('to_name') or r.get('payee'), 'year': (r.get('year') or r['date'])[:4],
                           'date': r['date'], 'amount_usd': r['amount_usd'], 'purpose': r.get('purpose', ''), 'url': r['url']})
    table(Tg, 'research/grants_cited.csv', gr, list(gr[0].keys()))
    # the saved story pages behind "named on N of the 1,086 saved story pages": addresses only
    # (since Nov 15, 2026 member_mentions.count() counts articles, for the companion map figure; this figure prints pages of the first search, count_pages())
    n_pages, hit = member_mentions.count_pages(); sur = {'mast': 'Mast', 'moolenaar': 'Moolenaar', 'crawford': 'Crawford'}
    pages = []
    for pid, _ in member_mentions.pages():
        m = json.loads((PRIMARY / pid / 'meta.json').read_text())
        pages.append({'id': pid, 'url': m['url'], 'saved_utc': m.get('fetched_utc') or m.get('saved_utc') or '', **{'names_' + k: 'yes' if pid in hit[s] else '' for k, s in sur.items()}})
    assert len(pages) == n_pages
    table(Tg, 'research/story_pages.tsv', pages, list(pages[0].keys()), '\t')
    # ---------------------------------------------------------------- sources that can be copied
    for pid, rel in COPIES.items():
        d = PRIMARY / pid
        (Tg / rel).parent.mkdir(parents=True, exist_ok=True)
        if pid.startswith('google-political-ads'):
            shutil.copyfile(d / 'creative-stats.csv', Tg / rel)
        elif pid.startswith('census'):                   # every row of the national table for a zip-code area that touches Florida's 21st district
            ls = (d / 'tab20_cd11920_zcta520_natl.txt').read_text(encoding='utf-8-sig').splitlines()
            z = {l.split('|')[8] for l in ls[1:] if l.split('|')[1] == '1221' and l.split('|')[8]}
            put(Tg, rel, 'SOURCE: U.S. Census Bureau, relationship file of 2020 zip-code tabulation areas by 119th Congress district\n'
                         'URL: https://www2.census.gov/geo/docs/maps-data/data/rel2020/cd-sld/tab20_cd11920_zcta520_natl.txt\n'
                         'ROWS KEPT: every row whose zip-code area has a row in Congressional District 21 of Florida (GEOID 1221)\n\n'
                         + ls[0] + '\n' + '\n'.join(l for l in ls[1:] if l.split('|')[8] in z) + '\n')
        else:
            txt = '\n\n'.join(f.read_text(errors='replace') for f in sorted(d.glob('text*.txt'), key=lambda f: f.name != 'text.reextract.txt'))
            put(Tg, rel, scrub(re.sub(r'ip=[\d.]+', '', txt)))
        if pid.startswith('google-ads-creative'):
            for n_ in ('frames.png', 'page.png'):
                if (d / n_).exists():
                    shutil.copyfile(d / n_, (Tg / rel).with_name(Path(rel).stem + '-' + n_))
        if pid.startswith('google-ads-political-search'):
            for f in sorted(d.glob('search_*.png')):
                shutil.copyfile(f, (Tg / rel).parent / f.name)
    shutil.copyfile(PRIMARY / 'x-chinaselect-letter-image' / 'body.bin', Tg / 'sources' / 'select-committee-letter-nov12.png')
    # ARI's two PACs in the FEC's committee-to-candidate file: the lines behind "115 candidates"
    import zipfile
    PA = PRIMARY / 'fec-bulk-pas226-20261112'
    lines = [l for l in zipfile.ZipFile(PA / 'pas226.zip').read('itpas2.txt').decode('latin-1').splitlines() if l.split('|')[0] in ('C00873356', 'C00893883')]
    put(Tg, 'sources/fec-committee-to-candidate-ari-pacs.txt', (PA / 'pas2_header_file.csv').read_text().strip().replace(',', '|') + '\n' + '\n'.join(lines) + '\n')
    lines = [l for l in zipfile.ZipFile(PA / 'pas226.zip').read('itpas2.txt').decode('latin-1').splitlines() if l.split('|')[0] in ('C00613521', 'C00419036', 'C00328369')]
    put(Tg, 'sources/fec-committee-to-candidate-trade-pacs.txt', (PA / 'pas2_header_file.csv').read_text().strip().replace(',', '|') + '\n' + '\n'.join(lines) + '\n')
    # some of those lines carry no candidate id; the FEC's committee master gives the candidate of the recipient committee (the third audit's finding on TechNet's count)
    cmr = {l.split('|')[0]: l.split('|') for l in zipfile.ZipFile(PA / 'cm26.zip').read('cm.txt').decode('latin-1').splitlines()}
    blank = sorted({l.split('|')[15] for l in lines if not l.split('|')[16]})
    put(Tg, 'sources/fec-committee-master-for-blank-candidate-ids.txt', 'CMTE_ID|CMTE_NM|CAND_ID\n' + '\n'.join(f'{c}|{cmr[c][1]}|{cmr[c][14]}' for c in blank) + '\n')
    # ---------------------------------------------------------------- evidence: one line per cited source
    ev = P.evidence()
    for e in ev:
        raw = e['source_ref']
        if raw in COPIES:
            e['copy_in_repo'] = COPIES[raw]
        elif raw in FEC_REFS:
            e['copy_in_repo'] = 'research/employee_gifts.csv'; e['what'] += ' (the line is in research/employee_gifts.csv by its sub_id, with a link to its FEC page image; the donor is not named)'
        if raw.startswith('evidence-set:congress/hard_money#') and e['kind'] == 'evidence-set row' and e['passage'] == 'BANKS FOR SENATE':
            e['copy_in_repo'] = 'research/employee_gifts.csv'
        if raw.startswith('lda-gov-contrib-'):
            e['copy_in_repo'] = 'research/lobbyist_gifts.csv'; e['url'] = e['passage']
            e['what'] = 'Contribution report (form LD-203) filed with the U.S. Senate; the passage is the report\'s address (the gift is in research/lobbyist_gifts.csv; the lobbyist is not named here)'
        e['url'] = re.sub(r'([?&])api_key=[^&]+&?', r'\1', e['url'])
    table(Tg, 'research/evidence.tsv', ev, list(ev[0].keys()), '\t')
    # ---------------------------------------------------------------- the figure
    for e in ('html', 'png', 'jpg'):
        (Tg / 'figures').mkdir(exist_ok=True); shutil.copyfile(ROOT / 'figures' / f'nv13-three-chairmen.{e}', Tg / 'figures' / f'nv13-three-chairmen.{e}')
    # ---------------------------------------------------------------- the audit
    audit_notes = {}
    for rnd, lane in LANES.items():
        if not (lane / 'out' / 'REPORT.md').exists():
            audit_notes[rnd] = 'not finished when this copy was assembled'; continue
        put(Tg, f'audit/{rnd}/BRIEF.md', scrub((lane / 'PROMPT.md').read_text()))
        if (lane / 'changed_rows.tsv').exists():
            put(Tg, f'audit/{rnd}/changed_rows.tsv', (lane / 'changed_rows.tsv').read_text())
        for name in ('REPORT.md', 'findings.csv', 'figure_findings.csv', 'census.md', 'gaps.csv', 'round1_followup.csv', 'round2_followup.csv', 'errata.csv'):
            if (lane / 'out' / name).exists():
                put(Tg, f'audit/{rnd}/{name}', scrub((lane / 'out' / name).read_text()))
        audit_notes[rnd] = (lane / 'out' / 'REPORT.md').read_text().strip().splitlines()[-1]
    disp = R / 'audits' / 'DISPOSITIONS-audit_nv13.csv'
    if disp.exists():
        put(Tg, 'audit/DISPOSITIONS.csv', disp.read_text())
    put(Tg, '.gitignore', '__pycache__/\n*.pyc\n')
    put(Tg, 'LICENSE.md', P.LICENSE_MD)
    import nv13_readme
    import nv13_status
    put(Tg, 'README.md', nv13_readme.readme(Tg, gifts, ev, audit_notes, scope=nv13_status.SCOPE))
    put(Tg, 'CHANGES.md', nv13_readme.CHANGES)
    # ---------------------------------------------------------------- checks on the copy
    bad = []
    for f in sorted(Tg.rglob('*')):
        if f.is_file() and '.git' not in f.parts and '__pycache__' not in f.parts and f.suffix not in ('.png', '.jpg'):
            m = PRIVATE.search(f.read_text(encoding='utf-8', errors='replace'))
            if m:
                bad.append((str(f.relative_to(Tg)), m.group(0)))
    assert not bad, ('local paths, ids or addresses in the copy', bad[:8])
    pairs = private_names(); hits = name_hits(Tg, pairs)
    assert not hits, ('a donor\'s or lobbyist\'s name is in the copy (file, initials)', Counter(hits).most_common(12))
    env = {**__import__('os').environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    r = subprocess.run([sys.executable, str(Tg / 'scripts' / 'build_nv13.py')], capture_output=True, text=True, env=env); assert r.returncode == 0, r.stderr[-800:]
    same = (Tg / 'figures' / 'nv13-three-chairmen.html').read_bytes() == (ROOT / 'figures' / 'nv13-three-chairmen.html').read_bytes()
    assert same, 'the figure rebuilt inside the copy differs from the project\'s'
    v = subprocess.run(['python3', '-I', '-B', str(Tg / 'scripts' / 'verify_nv13.py')], capture_output=True, text=True)
    print(v.stdout[-2500:]); assert v.returncode == 0, 'the copy\'s own verifier fails'
    files = sorted(str(f.relative_to(Tg)) for f in Tg.rglob('*') if f.is_file() and '.git' not in f.parts and '__pycache__' not in f.parts)
    assert not list(Tg.rglob('__pycache__')), 'bytecode folders in the copy: they hold local paths and must not be committed (.gitignore lists them; remove before committing)'
    print(f'wrote {len(files)} files to {Tg}; names scanned for: {len(pairs):,}; hits 0; figure rebuilt in the copy equals the project\'s: {same}; audit: {audit_notes}')


if __name__ == '__main__':
    main(sys.argv[1])
