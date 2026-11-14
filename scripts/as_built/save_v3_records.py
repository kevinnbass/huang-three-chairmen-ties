"""Move the records gathered for the three-chairmen figure's third version out of a session scratch folder into
research/primary, each under a new id with a meta.json (address, what it is, when it was downloaded, sha256 of every file).

Run: python3 -I scripts/save_v3_records.py <scratch folder>
It never writes into an id that already exists (it stops instead), so a second run does nothing but report.
Download times are the files' own modification times (the moment each download finished); saved_utc is the time of this run.
"""
import hashlib, json, re, shutil, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'research' / 'primary'
S = Path(sys.argv[1])
NOW = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
ADV = 'https://adstransparency.google.com/advertiser/AR09462075813676449793/creative/%s?political=&region=US'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def mtime(p):
    return datetime.fromtimestamp(Path(p).stat().st_mtime, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def save(sid, files, meta, text=None):
    """files: list of (source path, name in the primary folder)."""
    d = P / sid
    if d.exists():
        print(f'{sid}\talready saved; nothing written'); return
    for src, _ in files:
        assert Path(src).exists(), src
    d.mkdir()
    out = {}
    for src, name in files:
        shutil.copy2(src, d / name)
        assert sha(d / name) == sha(src)
        out[name] = sha(d / name)
    if text is not None:
        (d / 'text.txt').write_text(text)
        out['text.txt'] = sha(d / 'text.txt')
    m = {'id': sid, **meta, 'saved_utc': NOW, 'files': out}
    (d / 'meta.json').write_text(json.dumps(m, indent=1))
    print(f'{sid}\tsaved\tfiles={len(out)}\tbytes={sum((d / n).stat().st_size for n in out)}')


# 1. The Jun 25, 2025 hearing of the House select committee on China: Jack Clark's written statement and the transcript.
H = S / 'hearing'
for stem, sid, what, txt in (
        ('HHRG-119-ZS00-Wstate-ClarkJ-20250625', 'house-hrg-zs00-20250625-clark-statement',
         'Written testimony of Jack Clark (Anthropic) to the House Select Committee on the Chinese Communist Party, hearing '
         '"Algorithms and Authoritarians: Why U.S. AI Must Lead", Jun 25, 2025 (7 pages)', 'clark.txt'),
        ('HHRG-119-ZS00-Transcript-20250625', 'house-hrg-zs00-20250625-transcript',
         'Hearing transcript, House Select Committee on the Strategic Competition Between the United States and the Chinese '
         'Communist Party, "Algorithms and Authoritarians: Why U.S. AI Must Lead", Jun 25, 2025 (78 pages, court reporter\'s transcript)',
         'transcript.txt')):
    a, b = H / f'{stem}.pdf', H / f'docs-{stem}.pdf'
    same = sha(a) == sha(b)
    kind = 'witnesses' if 'Wstate' in stem else 'documents'
    save(sid, [(a, 'body.pdf'), (b, 'body.docs-house-gov.pdf')],
         {'url': f'https://www.congress.gov/119/meeting/house/118428/{kind}/{stem}.pdf',
          'url_second_copy': f'https://docs.house.gov/meetings/ZS/ZS00/20250625/118428/{stem}.pdf',
          'what': what, 'status': 200, 'fetched_utc': mtime(a), 'content_type': 'application/pdf', 'bytes': a.stat().st_size,
          'sha256': sha(a), 'two_copies_identical': same,
          'text_note': 'text.txt is the PDF text layer (pdftotext -layout); no OCR',
          'record_status': 'official record'},
         text=(H / txt).read_text(errors='replace'))

# 2. FEC: every candidate's totals for the 2026 cycle (the "all candidates" summary file).
F = S / 'fec3'
COLS = ('CAND_ID CAND_NAME CAND_ICI PTY_CD CAND_PTY_AFFILIATION TTL_RECEIPTS TRANS_FROM_AUTH TTL_DISB TRANS_TO_AUTH COH_BOP COH_COP '
        'CAND_CONTRIB CAND_LOANS OTHER_LOANS CAND_LOAN_REPAY OTHER_LOAN_REPAY DEBTS_OWED_BY TTL_INDIV_CONTRIB CAND_OFFICE_ST '
        'CAND_OFFICE_DISTRICT SPEC_ELECTION PRIM_ELECTION RUN_ELECTION GEN_ELECTION GEN_ELECTION_PRECENT OTHER_POL_CMTE_CONTRIB '
        'POL_PTY_CONTRIB CVG_END_DT INDIV_REFUNDS CMTE_REFUNDS').split()
z = zipfile.ZipFile(F / 'weball26.zip')
raw = z.read('weball26.txt').decode('latin-1')
assert raw == (F / 'weball26.txt').read_text(encoding='latin-1')
lines = raw.splitlines()
assert all(len(l.split('|')) == len(COLS) for l in lines[:50]), 'column count'
want = {'H6FL18097': 'Mast', 'H4MI04126': 'Moolenaar', 'H0AR01083': 'Crawford'}
t = ['URL: https://www.fec.gov/files/bulk-downloads/2026/weball26.zip', f'DOWNLOADED: {mtime(F / "weball26.zip")} (through the shared FEC queue)',
     f'ROWS: {len(lines)} candidates; columns as the FEC documents them for the "all candidates" file:', '|'.join(COLS), '',
     'THE THREE CHAIRMEN (raw lines, then the fields the figure uses):']
for l in lines:
    f = dict(zip(COLS, l.split('|')))
    if f['CAND_ID'] in want:
        t += [l, '  ' + '; '.join(f'{k}={f[k]}' for k in ('CAND_ID', 'CAND_NAME', 'TTL_RECEIPTS', 'TTL_INDIV_CONTRIB', 'OTHER_POL_CMTE_CONTRIB',
                                                        'TRANS_FROM_AUTH', 'CVG_END_DT')), '']
assert sum(1 for x in t if x.startswith('  CAND_ID=')) == 3
save('fec-bulk-weball26-20261113', [(F / 'weball26.zip', 'weball26.zip'), (F / 'weball26.txt', 'weball26.txt')],
     {'url': 'https://www.fec.gov/files/bulk-downloads/2026/weball26.zip', 'what': 'FEC bulk file "all candidates" for the 2026 cycle: one line of totals per candidate',
      'status': 200, 'fetched_utc': mtime(F / 'weball26.zip'), 'sha256': sha(F / 'weball26.zip'), 'bytes': (F / 'weball26.zip').stat().st_size,
      'candidates': len(lines), 'record_status': 'official record'}, text='\n'.join(t) + '\n')

# 3. FEC: the joint fundraising committee that received $17,000 of the gifts counted for Mast.
cj = json.loads((F / 'committee_C00583161.json').read_text()); fj = json.loads((F / 'committee_C00583161_f1.json').read_text())
for p in ('committee_C00583161.json', 'committee_C00583161_f1.json', 'f1_1307133.fec'):
    assert 'api_key' not in (F / p).read_text(errors='replace'), p
c = cj['results'][0]
t = ['URLS: https://api.open.fec.gov/v1/committee/C00583161/ ; https://api.open.fec.gov/v1/committee/C00583161/filings/?form_type=F1&per_page=5&sort=-receipt_date ; '
     'https://docquery.fec.gov/dcdev/posted/1307133.fec', f'DOWNLOADED: {mtime(F / "committee_C00583161.json")} (through the shared FEC queue)', '',
     'COMMITTEE RECORD:'] + [f'  {k}: {c.get(k)}' for k in ('committee_id', 'name', 'designation_full', 'committee_type_full', 'candidate_ids',
                                                           'sponsor_candidate_ids', 'jfc_committee', 'affiliated_committee_name', 'first_file_date', 'last_file_date')]
t += ['', f'STATEMENTS OF ORGANIZATION (Form 1) ON FILE: {fj["pagination"]["count"]}']
for r in fj['results']:
    t.append(f'  received {r.get("receipt_date", "")[:10]}; file number {r.get("file_number")}; amendment indicator {r.get("amendment_indicator")}; {r.get("pdf_url")}')
t += ['', 'NOTE: the electronic copy of file 1307133 holds only the cover line of the Form 1 amendment (752 bytes); the committees that share',
      'in the joint fundraising are not listed in it. They are on the filed pages (the pdf links above), which were not read.']
save('fec-committee-c00583161-20261113',
     [(F / 'committee_C00583161.json', 'committee.json'), (F / 'committee_C00583161_f1.json', 'filings-f1.json'), (F / 'f1_1307133.fec', 'f1-1307133.fec')],
     {'url': 'https://api.open.fec.gov/v1/committee/C00583161/', 'what': 'FEC committee record, list of Form 1 filings and the latest electronic Form 1 of Mast Victory Committee (C00583161)',
      'status': 200, 'fetched_utc': mtime(F / 'committee_C00583161.json'), 'record_status': 'official record'}, text='\n'.join(t) + '\n')

# 4. The second variation of each Public First Action ad entry, and the second Arkansas ad: frames of the video as played.
STATS = {}
import csv
for r in csv.DictReader(open(P / 'google-political-ads-pfa-20260916' / 'creative-stats.csv', newline='')):
    STATS[r['Ad_ID']] = r
WORDS = {
 'mi2v2': ['MADE WITH AMERICAN RESOLVE', 'WEAPON', 'CONGRESSMAN JOHN MOOLENAAR', 'CONGRESSMAN JOHN MOOLENAAR BACKING LEGISLATION TO PUT EXPORT CONTROLS ON ADVANCED CHIPS',
           'TO KEEP THE MOST ADVANCED AI AWAY FROM THEM', 'SO AMERICA KEEPS WINNING.',
           'CALL CONGRESSMAN JOHN MOOLENAAR TELL HIM TO KEEP FIGHTING TO KEEP ADVANCED CHIPS FROM GOING TO OUR ENEMIES. (202) 225-3561',
           'PAID FOR BY PUBLIC FIRST ACTION. WWW.PUBLICFIRSTACTION.US'],
 'flv2': ['MADE WITH AMERICAN RESOLVE', 'WEAPON', 'CONGRESSMAN BRIAN MAST', 'CONGRESSMAN BRIAN MAST BACKING LEGISLATION TO PUT EXPORT CONTROLS ON ADVANCED CHIPS',
          'TO KEEP THE MOST ADVANCED AI AWAY FROM THEM', 'SO AMERICA KEEPS WINNING.',
          'CALL CONGRESSMAN BRIAN MAST TELL HIM TO KEEP FIGHTING TO KEEP ADVANCED CHIPS FROM GOING TO OUR ENEMIES. (202) 225-3026',
          'PAID FOR BY PUBLIC FIRST ACTION. WWW.PUBLICFIRSTACTION.US'],
 'ar2': ["TOM COTTON MAKING SURE AI-POWERING CHIPS DON'T FA[...]", 'TOM COTTON SUPPORTING THE C[...]', 'CALL TOM COTTON',
         'PAID FOR BY PUBLIC FIRST ACTION. WWW.PUBLICFIRSTACTION.US'],
}
for key, sid, cr, which, note in (
        ('mi2v2', 'google-ads-creative-mi2-v2-20261113', 'CR04292619503667249153', 'the second of the two variations Google lists under this ad entry (page label "2 of 2 variations")',
         'The on-screen words are the same as in the first variation (google-ads-creative-mi2-20261113).'),
        ('flv2', 'google-ads-creative-fl21-v2-20261113', 'CR08230337604738875393', 'the second of the two variations Google lists under this ad entry (page label "2 of 2 variations")',
         'The on-screen words are the same as in the first variation (google-ads-creative-fl21-20261113).'),
        ('ar2', 'google-ads-creative-ar2-20261113', 'CR14558268227953098753', 'a second, earlier Arkansas ad entry by the same advertiser',
         'The on-screen words match the other Arkansas entry (google-ads-creative-ar-20261113); it names Sen. Tom Cotton, not one of the three chairmen.')):
    frames = sorted(S.glob(f'play_{key}_*.png'))
    assert len(frames) == 9, (key, len(frames))
    r = STATS[cr]
    t = [f'URL: {ADV % cr}', f'CAPTURED: {mtime(frames[-1])} (opened in a local browser; {which})', '',
         f"Google political-ads report line for this entry: {r['Ad_Type'].lower()} ad by {r['Advertiser_Name']}, {r['Date_Range_Start']} to {r['Date_Range_End']}, "
         f"{r['Impressions']} impressions, ${int(r['Spend_Range_Min_USD']):,} to ${int(r['Spend_Range_Max_USD']):,}. Google reports these ranges for the entry as a whole, not per variation.", '',
         'WORDS ON SCREEN IN THE VIDEO (read by the builder from nine frames captured about every 3.5 seconds while the video played; frames saved here as '
         'frame-00.png to frame-08.png and tiled in frames.png; a reading, not a transcript: the voice-over was not captured):'] + WORDS[key] + ['', note]
    save(sid, [(f, f'frame-{i:02d}.png') for i, f in enumerate(frames)] + [(S / f'sheet_{key}.png', 'frames.png')],
         {'url': ADV % cr, 'what': f'Google Ads Transparency Center: {which}; frames of the video', 'fetched_utc': mtime(frames[-1]), 'creative_id': cr,
          'record_status': "platform page; on-screen words are the builder's reading of saved frames"}, text='\n'.join(t) + '\n')
