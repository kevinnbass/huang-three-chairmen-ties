"""The two companies' federal lobbying reports, 2025-26, from the Senate lobbying-disclosure API.
Run: python3 -I scripts/build_lobbying.py
Reads  research/primary/lda-gov-<company>-<year>[-p2]/body.json (the API's answer to client_name=<company>&filing_year=<year>)
Writes research/lobbying_filings.csv (one row per report as filed, keyed by the filing's own UUID) and
       research/lobbying_bill_reports.csv (one row per company, bill and reporting slot).
A report and its later amendment share registrant, client, year and quarter: the one posted last is the current version and
the only one counted (`current` = yes). In-house reports give `expenses`, which already include what the company paid its
outside firms; outside firms give `income`. The two are never added. Registrations (RR) carry no amount.
Bill numbers are read from the reports' own activity descriptions; a bill counts once per report however often it is named.

Since Nov 17, 2026 a third table, research/lobbying_family_reports.csv, counts the reports that name each of the five chip-export
measures (one row per company and measure), on three bases that are kept apart and never merged into the per-bill table:
  bill number        the text gives the number of one of the measure's bills (the only basis counted until then);
  amendment number   the text gives no such number and gives the number of a Senate amendment whose official text carries the
                     measure (AMENDMENTS below: each with the saved page that prints its text); the filings table says
                     for each such report whether it also gives the measure's name;
  name               the text gives neither and gives the measure's short or long name.
One rule for both companies. Before it, a report that named a measure only as an amendment to the defense bill, or only by name,
was in no count: two reports of Anthropic's and two of Nvidia's on the GAIN AI Act (found by the builder on Nov 17, 2026).
The window is in the code (YEARS): folders of other years, saved later for other tables, are not read."""
import csv, glob, json, re, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'research'
SIDES = {'nvidia': 'NVIDIA', 'anthropic': 'ANTHROPIC'}
QUARTER = {'first_quarter': 'Q1', 'second_quarter': 'Q2', 'third_quarter': 'Q3', 'fourth_quarter': 'Q4', 'mid_year': 'H1', 'year_end': 'H2'}
BILL = re.compile(r'\b(H\.\s?R\.|S\.)\s?(\d{3,5})\b')
YEARS = ('2025', '2026')
# the five measures by name: the short title and the long title of the bill records (research/chip_bills.csv, billstatus-119-*)
FAMILY_NAMES = {
 'AI OVERWATCH Act': r'\bAI\s+OVERWATCH\b|Artificial\s+Intelligence\s+Oversight\s+of\s+Verified\s+Exports',
 'GAIN AI Act': r'\bGAIN\s+AI\b|Guaranteeing\s+Access\s+and\s+Innovation\s+for\s+National\s+Artificial\s+Intelligence',
 'Chip Security Act': r'\bChips?\s+Security\s+Act\b',
 'MATCH Act': r'\bMATCH\s+Act\b|\(MATCH\)|Multilateral\s+Alignment\s+of\s+Technology\s+Controls',
 'Remote Access Security Act': r'\bRemote\s+Access\s+Security\s+Act\b',
}
# Senate amendments named in either company's reports. Senate amendments are numbered in one series through a Congress, so the number alone identifies one.
# number: (measure, the bill it amends, the saved page that prints the amendment's text, words of that text, the official record of the bill, sponsor and day as that record gives them,
#          the sponsor's id in that record, the bill in plain words, the page's own line on sponsor and day)
AMENDMENTS = {
 '3505': ('GAIN AI Act', 'S. 2296', 'lda-ref-samdt-119-3505-text-wayback', "or the ``GAIN AI Act of 2025''", 'billstatus-119-s2296', 'Sen. Banks, Jim [R-IN]', '2025-08-01',
          'B001299', 'the defense authorization bill for fiscal 2026', 'Sponsor: Sen. Banks, Jim [R-IN] (Submitted 08/01/2025)'),
}
# named in a report and looked up: its text, in the Congressional Record, carries none of the five measures (number: the bill it amends, the saved page of the Record, its heading there)
AMENDMENTS_NOT_PLACED = {'6561': ('S. 4784', 'lda-ref-samdt-119-6561-crec', 'COLLABORATION ON ADVERSARIAL THREATS AND AI SECURITY RISKS')}
SAMDT = re.compile(r'\b(?:S\.?\s?Amdt\.?|S\.\s?A\.|Senate\s+Amendment)\s*(?:No\.?\s*)?(\d{3,4})\b', re.I)
ANY_AMDT = re.compile(r'Amdt|\bS\.\s?A\.\s?\d|\bH\.\s?A\.\s?\d|amendment\s+(?:no\.?\s*|#\s*)?\d', re.I)
BASES = ('bill number', 'amendment number', 'name')


def bills_in(text):
    return sorted({('H.R. ' if m.group(1).startswith('H') else 'S. ') + m.group(2) for m in BILL.finditer(text)}, key=lambda b: (b[0], int(b.split()[-1])))


def side_words(r):
    """How one company's reports name a measure without a bill number, from its row of lobbying_family_reports.csv."""
    am, wn, nm = int(r['by_senate_amendment_number']), int(r['of_them_also_giving_the_name']), int(r['by_name_only']); parts = []
    if wn: parts.append(f"the amendment with the act's name ({wn})")
    if am - wn: parts.append(f"the amendment's number alone ({am - wn})")
    if nm: parts.append(f"the name alone ({nm})")
    return ' and '.join(parts)


def families_in(text, fam_bills):
    """{measure: basis} for one report's text. A bill number of the measure wins; then an amendment that carries it; then its name."""
    text = ' '.join(text.split()); nums = set(bills_in(text)); amd = {m.group(1) for m in SAMDT.finditer(text)}
    assert len(ANY_AMDT.findall(text)) == len(SAMDT.findall(text)), ('an amendment is written in a form the pattern does not read', [text[max(0, m.start() - 40): m.end() + 40] for m in ANY_AMDT.finditer(text)][:3])
    assert amd <= set(AMENDMENTS) | set(AMENDMENTS_NOT_PLACED), ('a Senate amendment that has not been looked up', sorted(amd - set(AMENDMENTS) - set(AMENDMENTS_NOT_PLACED)))
    out = {}
    for fam, pat in FAMILY_NAMES.items():
        by_amd = sorted(a for a in amd if a in AMENDMENTS and AMENDMENTS[a][0] == fam); named = bool(re.search(pat, text, re.I))
        if nums & set(fam_bills[fam]):
            out[fam] = 'bill number'
        elif by_amd:
            out[fam] = 'amendment number' + (' (Senate amendment ' + ', '.join(by_amd) + (', with the name)' if named else ', without the name)'))
        elif named:
            out[fam] = 'name'
    return out


def main():
    rows, seen = [], set()
    fam_bills = defaultdict(list)
    for b in csv.DictReader(open(R / 'chip_bills.csv', newline='')):
        fam_bills[b['family']].append(b['bill'])
    assert set(fam_bills) == set(FAMILY_NAMES), set(fam_bills) ^ set(FAMILY_NAMES)
    for num, (fam, bill, page, words, record, sponsor, day, sponsor_id, plain, line) in AMENDMENTS.items():       # the amendment's own text carries the measure's name, and the bill's record lists the amendment
        t = ' '.join((R / 'primary' / page / 'text.txt').read_text().split()); assert words in t and line in t and f'S.Amdt.{num} to {bill.replace(" ", "")}' in t and 'for Fiscal Year ' + plain[-4:] in t, (num, page)
        rec = (R / 'primary' / record / 'body.html').read_text(errors='replace')
        a = [m.group(1) for m in re.finditer(r'<amendment>(.*?)</amendment>', rec, re.S) if re.search(rf'<number>{num}</number>', m.group(1))]
        assert len(a) == 1 and sponsor in a[0] and f'<bioguideId>{sponsor_id}</bioguideId>' in a[0] and f'<submittedDate>{day}' in a[0], (num, record)
    import html as _html
    for num, (bill, page, heading) in AMENDMENTS_NOT_PLACED.items():      # the amendment's own text: its heading is there, and no name of a measure, nor the words export, integrated circuit or semiconductor
        t = ' '.join(_html.unescape(re.sub(r'<[^>]+>', ' ', (R / 'primary' / page / 'body.html').read_text(errors='replace'))).split())
        assert f'SA {num}.' in t and bill in t and heading in t and not any(re.search(p_, t, re.I) for p_ in FAMILY_NAMES.values()) and not re.search(r'export|integrated circuit|semiconductor', t, re.I), (num, page)
    for side, word in SIDES.items():
        for d in sorted(x for y in YEARS for x in glob.glob(str(R / 'primary' / f'lda-gov-{side}-{y}*'))):
            for f in sorted(glob.glob(d + '/body.*')):
                for r in json.load(open(f))['results']:
                    assert r['filing_uuid'] not in seen, r['filing_uuid']; seen.add(r['filing_uuid'])
                    reg, cli = r['registrant']['name'], r['client']['name']
                    assert word in cli.upper(), cli
                    assert str(r['filing_year']) in YEARS, (r['filing_uuid'], r['filing_year'])
                    text = ' '.join((a.get('description') or '') for a in (r.get('lobbying_activities') or []))
                    fams = families_in(text, fam_bills)
                    rows.append(dict(uuid=r['filing_uuid'], side=side, registrant=reg, client=cli, year=str(r['filing_year']), quarter=QUARTER.get(r['filing_period'], r['filing_period']),
                                     type=r['filing_type'], type_display=r.get('filing_type_display') or '', income=r.get('income') or '', expenses=r.get('expenses') or '',
                                     posted=(r.get('dt_posted') or '')[:19], in_house='yes' if reg.upper().startswith(word) else 'no',
                                     bills='; '.join(bills_in(text)), chip_measures='; '.join(f'{f} [{b}]' for f, b in fams.items()), print_url=r.get('filing_document_url') or '', source=Path(d).name))
    slot = defaultdict(list)
    for r in rows:
        if r['type'] != 'RR':
            slot[(r['side'], r['registrant'], r['client'], r['year'], r['quarter'])].append(r)
    for v in slot.values():
        last = max(v, key=lambda r: r['posted'])
        for r in v:
            r['current'] = 'yes' if r is last else 'no'
    for r in rows:
        r.setdefault('current', '')
    rows.sort(key=lambda r: (r['side'], r['year'], r['quarter'], r['in_house'] != 'yes', r['registrant'], r['posted']))
    cols = ['uuid', 'side', 'registrant', 'client', 'year', 'quarter', 'type', 'type_display', 'income', 'expenses', 'posted', 'in_house', 'current', 'bills', 'chip_measures', 'print_url', 'source']
    with open(R / 'lobbying_filings.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    by = defaultdict(list)
    for r in rows:
        if r['current'] == 'yes':
            for b in filter(None, r['bills'].split('; ')):
                by[(r['side'], b)].append(r)
    with open(R / 'lobbying_bill_reports.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['key', 'side', 'bill', 'reports', 'in_house_reports', 'outside_firm_reports', 'first_quarter', 'last_quarter', 'uuids'])
        for (side, b), v in sorted(by.items()):
            qs = sorted(r['year'] + ' ' + r['quarter'] for r in v)
            w.writerow([f'{side}:{b}', side, b, len(v), sum(r['in_house'] == 'yes' for r in v), sum(r['in_house'] != 'yes' for r in v), qs[0], qs[-1], ' '.join(r['uuid'] for r in v)])
    # ---- the five measures, both companies, three bases kept apart
    fam = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r['current'] == 'yes':
            for x in filter(None, r['chip_measures'].split('; ')):
                f_, b_ = re.match(r'(.+?) \[(.+)\]$', x).groups(); fam[(r['side'], f_)][b_.split(' (')[0]].append(r)
    with open(R / 'lobbying_family_reports.csv', 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['key', 'side', 'measure', 'reports', 'by_bill_number', 'by_senate_amendment_number', 'of_them_also_giving_the_name', 'by_name_only', 'in_house_reports', 'outside_firm_reports', 'first_quarter', 'last_quarter',
                    'uuids_by_bill_number', 'uuids_by_senate_amendment_number', 'uuids_by_name_only', 'amendments', 'in_words'])
        for side in sorted(SIDES):
            for f_ in FAMILY_NAMES:
                v = fam[(side, f_)]; allr = [r for b in BASES for r in v[b]]; qs = sorted(r['year'] + ' ' + r['quarter'] for r in allr)
                assert len({r['uuid'] for r in allr}) == len(allr)
                assert {r['uuid'] for r in v['bill number']} == {u for b in fam_bills[f_] for r in by[(side, b)] for u in [r['uuid']]}, (side, f_)      # the same reports as the per-bill table
                w.writerow([f'{side}:{f_}', side, f_, len(allr), len(v['bill number']), len(v['amendment number']), sum(f'{f_} [amendment number (' in r['chip_measures'] and ', with the name)]' in r['chip_measures'].split(f_ + ' [')[1].split(']')[0] + ']' for r in v['amendment number']), len(v['name']), sum(r['in_house'] == 'yes' for r in allr), sum(r['in_house'] != 'yes' for r in allr),
                            qs[0] if qs else '', qs[-1] if qs else '', *(' '.join(r['uuid'] for r in v[b]) for b in BASES),
                            '; '.join(f'Senate amendment {n} to {a[1]}, submitted by {a[5]} on {a[6]}' for n, a in AMENDMENTS.items() if a[0] == f_),
                            # one cell that states the row, so that a line citing this row can quote it whole (a passage is checked against one cell here and against the file's text in the public copy)
                            f'all {len(allr)}; by bill number {len(v["bill number"])}; by a Senate amendment\'s number and no bill number {len(v["amendment number"])} (also giving the name: {sum(", with the name)" in r["chip_measures"] for r in v["amendment number"])}); by name only {len(v["name"])}'])
                print(f'{side:10} {f_:28} all {len(allr):2} | bill number {len(v["bill number"]):2} | Senate amendment number, no bill number {len(v["amendment number"])} | name only {len(v["name"])}')
    print('reports', len(rows), '| current', sum(r['current'] == 'yes' for r in rows), '| replaced by an amendment', sum(r['current'] == 'no' for r in rows), '| registrations', sum(r['type'] == 'RR' for r in rows))
    for side in SIDES:
        print(side, 'in-house expenses by quarter:', {f"{r['year']} {r['quarter']}": r['expenses'] for r in rows if r['side'] == side and r['in_house'] == 'yes' and r['current'] == 'yes'})
        for y in ('2025', '2026'):
            print('  ', y, 'total', sum(float(r['expenses'] or 0) for r in rows if r['side'] == side and r['in_house'] == 'yes' and r['current'] == 'yes' and r['year'] == y),
                  '| outside firms reporting:', len({r['registrant'] for r in rows if r['side'] == side and r['in_house'] == 'no' and r['year'] == y}))
    for b in ['H.R. 6875', 'S. 4456', 'H.R. 5885', 'S. 3150', 'H.R. 3447', 'S. 1705', 'H.R. 8170', 'S. 4281', 'H.R. 2683', 'S. 3519']:
        print(f'{b:10}', {s: (len(by[(s, b)]), sorted({r["year"] + r["quarter"] for r in by[(s, b)]})) for s in SIDES})


if __name__ == '__main__':
    main()
