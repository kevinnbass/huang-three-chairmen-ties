"""Count the saved story pages that name each member of Congress.
Run: python3 -I scripts/member_mentions.py -> research/member_mentions.tsv, research/member_candidates.tsv

Pages counted: every saved page with an address, status 200 and text, except the aggregator pages themselves and the
background pages saved for the run-up (ids starting art-, anthropic-). A reposted wire story on two sites is two pages.
A page names a member when its text holds the member's full name, or a congressional title followed within three
words by the surname ("Sen. Warren", "Chairman Brian Mast", "Minority Leader Hakeem Jeffries").
member_candidates.tsv lists every other surname found after a title on four or more pages, so the rule "every member
named on four or more pages" can be checked against names not yet drawn. It is a list to read, not a finding: it also
catches non-members ("Chairman Xi", "Speaker" of another parliament), which the `is_member` column of the hand list
below settles."""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'research'; P = R / 'primary'
sys.path.insert(0, str(ROOT / 'scripts'))
SKIP = ('techmeme', 'memeorandum', 'mediagazer', 'art-', 'anthropic-',
        'billstatus-', 'lda-', 'lake-', 'fec-',      # official records saved for the tables, not story pages
        'pfa-founding-release', 'abc-anthropic-pentagon-0227',
        'x-chinaselect-letter', 'govinfo-chrg-', 'google-', 'census-', 'house-hrg-')                      # the committees' Nov 12 letter and its image, and a 2023 hearing transcript, saved Nov 13 for the member figures   # originals for two run-up rows (2025 and Feb 2026), saved after audit1b
TITLE = r"(?:Sens?\.|Senators?|Reps?\.|Representatives?|Congress(?:man|woman)|(?:Majority|Minority|Democratic|Republican)\s+Leader|Leader|Whip|Speaker|Chair(?:man|woman)?|Ranking\s+Member)"
AFTER = re.compile(TITLE + r"\s+((?:[A-Z][\w.'’-]*\s+){0,2}[A-Z][\w'’-]+)")
# first names as the pages give them; a member is named by "First Last" or by a title then the surname
FIRST = {'Warren': ['Elizabeth'], 'Coons': ['Chris', 'Christopher'], 'Cramer': ['Kevin'], 'Schumer': ['Chuck', 'Charles'], 'Banks': ['Jim'],
         'Cornyn': ['John'], 'Kennedy': ['John'], 'Thune': ['John'], 'Mast': ['Brian'], 'Crawford': ['Rick'], 'Meeks': ['Gregory', 'Greg'],
         'Himes': ['Jim'], 'Huizenga': ['Bill'], 'Moolenaar': ['John'], 'Jeffries': ['Hakeem'], 'Magaziner': ['Seth'],
         'Subramanyam': ['Suhas'], 'Bacon': ['Don'],
         'Johnson': ['Mike'], 'Blumenthal': ['Richard', 'Dick'], 'Wyden': ['Ron'], 'Ricketts': ['Pete'], 'McCaul': ['Michael', 'Mike'], 'Warner': ['Mark'],
         'Cotton': ['Tom']}                 # drawn in the map since Nov 14, 2026: named for his letter of Oct 2025 on Megaspeed (an act on the matter before these days)
# Surnames shared with another current member: only the full name counts ("Speaker Johnson" is taken as him, "Sen. Johnson" is not).
FULL_ONLY = {'Johnson': r"(?:Speaker\s+(?:Mike\s+)?|Mike\s+)Johnson"}
# Surnames met after a title that are not members of Congress, or are members named only in passing lists; read by hand.
NOT_MEMBER = set()


# Members named on three or more pages for other things, so not drawn: first names; True = a title then the surname also counts
# (no other member shares it); what the pages name them for (read on Nov 14, 2026).
NOT_DRAWN = {'Jordan': (['Jim'], False, 'his election as House minority leader'), 'Stevens': (['Haley'], False, 'an endorsement and an absence from a vote'),
             'Massie': (['Thomas'], True, 'his bid to impeach the defense secretary'), 'Garcia': (['Robert'], False, 'other inquiries he plans as incoming oversight chair'),
             'Hyde-Smith': (['Cindy'], True, 'losing her Senate race'), 'Sanders': (['Bernie', 'Bernard'], True, 'the Senate leadership contest and his own AI bill')}
# other words met after a congressional title on three or more pages that are not a searched name: what each is
NOT_A_MEMBER = {'Jamieson': 'the U.S. trade representative', 'Greer': 'the U.S. trade representative', 'Eric': 'a former member (Swalwell)', 'Swalwell': 'a former member',
                'Anthony': 'a former member (Weiner)', 'Weiner': 'a former member', 'Harvey': "Nvidia's board chair", 'Jones': "Nvidia's board chair",
                'Jensen': 'Huang ("Nvidia Leader ... Jensen Huang")', 'Tae-won': 'the chairman of a Korean company'}


def not_drawn_re(s):
    firsts, by_title, _ = NOT_DRAWN[s]
    return re.compile(rf"\b(?:{'|'.join(firsts)})\s+(?:[A-Z]\.\s+)?{s}\b" + (rf"|{TITLE}\s+(?:[A-Z][\w.'’-]*\s+){{0,2}}{s}\b" if by_title else ''))


def pages():
    """(id, text) of each counted page; an address saved under two ids is counted once (the first id)."""
    seen = set()
    for d in sorted(P.iterdir()):
        if d.name.startswith(SKIP) or not (d / 'meta.json').exists():
            continue
        try:
            m = json.loads((d / 'meta.json').read_text())
        except Exception:
            continue
        if not isinstance(m, dict) or not m.get('url') or m.get('status') != 200:
            continue
        key = re.sub(r'^https?://(www\.)?', '', m['url'].split('?')[0].split('#')[0]).rstrip('/').lower()
        if key in seen:
            continue
        texts = [f.read_text(errors='replace') for f in (d / 'text.txt', d / 'text.reextract.txt') if f.exists()]
        if texts:
            seen.add(key)
            yield d.name, max(texts, key=len)


def member_re(sur):
    if sur in FULL_ONLY:
        return re.compile(FULL_ONLY[sur])
    firsts = '|'.join(FIRST[sur])
    return re.compile(rf"\b(?:{firsts})\s+(?:[A-Z]\.\s+)?{sur}\b|{TITLE}\s+(?:[A-Z][\w.'’-]*\s+){{0,2}}{sur}\b")


def count():
    """(pages counted, {surname: [page ids]}, {other surname after a title: [page ids]})"""
    res = {s: member_re(s) for s in FIRST}
    hit, other, n = defaultdict(list), defaultdict(set), 0
    for pid, text in pages():
        n += 1
        for s, rx in res.items():
            if rx.search(text):
                hit[s].append(pid)
        for m in AFTER.finditer(text):
            for w in m.group(1).split():
                w = w.strip(".,'’")
                if w not in FIRST and len(w) > 2:
                    other[w].add(pid)
    return n, hit, other


def main():
    n, hit, other = count()
    with open(R / 'member_mentions.tsv', 'w') as f:
        f.write(f'# saved story pages naming each member; pages counted: {n}\nsurname\tpages\n')
        for s in FIRST:
            f.write(f'{s}\t{len(hit[s])}\n')
    # page-level list, so each count can be checked page by page (audit1b): drawn members, then the members named that often for other things
    texts = list(pages())
    with open(R / 'member_mentions_pages.tsv', 'w') as f:
        f.write('# one line per member: the saved pages that name them (ids under research/primary)\nsurname\tdrawn\tpages\tpage_ids\n')
        for s in FIRST:
            f.write(f"{s}\t{'yes' if len(hit[s]) >= 3 else 'no'}\t{len(hit[s])}\t{' '.join(hit[s])}\n")
        for s in NOT_DRAWN:
            rx = not_drawn_re(s)
            ids = [pid for pid, t in texts if rx.search(t)]
            f.write(f"{s}\tno (named for other things)\t{len(ids)}\t{' '.join(ids)}\n")
    cand = sorted(((len(v), k) for k, v in other.items() if len(v) >= 4), reverse=True)
    with open(R / 'member_candidates.tsv', 'w') as f:
        f.write('# other words found after a congressional title on four or more pages (to read by hand)\nword\tpages\n')
        f.writelines(f'{k}\t{c}\n' for c, k in cand)
    print('pages counted', n)
    print('members:', ', '.join(f'{s} {len(hit[s])}' for s in FIRST))
    print('other words after a title, 4+ pages:', ', '.join(f'{k} {c}' for c, k in cand[:120]))


if __name__ == '__main__':
    main()
