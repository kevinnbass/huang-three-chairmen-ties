"""Count the saved articles that name each member of Congress.
Run: python3 -I scripts/member_mentions.py -> research/member_mentions.tsv, research/member_candidates.tsv

Since Nov 15, 2026 the count is of articles, not pages (Kevin: "count them for everyone. don't use duplicates. deduplicate. don't add
the pieces dates 13 and 14."): research/nv8_articles.tsv (scripts/nv8_articles.py) gives each saved page its article, and an article
is counted once however many copies of it are saved, and not at all when every copy is dated after Nov 12. Two sets of pages feed it:
the first census (`pages()` below: every saved page with an address, status 200 and text, except the aggregator pages themselves and
the background pages saved for the run-up, ids starting art-, anthropic-) and the pages saved since (the papers' own articles saved by
hand, and licensed copies of them).
An article names a member when the text of any counted copy holds the member's full name, or a congressional title followed within three
words by the surname ("Sen. Warren", "Chairman Brian Mast", "Minority Leader Hakeem Jeffries").
member_candidates.tsv lists every other surname found after a title on four or more pages, so the rule "every member
named on four or more pages" can be checked against names not yet drawn. It is a list to read, not a finding: it also
catches non-members ("Chairman Xi", "Speaker" of another parliament), which the `is_member` column of the hand list
below settles."""
import csv, json, re, sys
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
FIRST = {'Warren': ['Elizabeth', 'Liz'], 'Coons': ['Chris', 'Christopher'], 'Cramer': ['Kevin'], 'Schumer': ['Chuck', 'Charles', 'Charlie'], 'Banks': ['Jim', 'James'],
         'Cornyn': ['John'], 'Kennedy': ['John'], 'Thune': ['John'], 'Mast': ['Brian'], 'Crawford': ['Rick', 'Eric'], 'Meeks': ['Gregory', 'Greg'],
         'Himes': ['Jim', 'James'], 'Huizenga': ['Bill', 'William'], 'Moolenaar': ['John'], 'Jeffries': ['Hakeem'], 'Magaziner': ['Seth'],
         'Subramanyam': ['Suhas'], 'Bacon': ['Don', 'Donald'],
         'Johnson': ['Mike'], 'Blumenthal': ['Richard', 'Dick'], 'Wyden': ['Ron', 'Ronald'], 'Ricketts': ['Pete', 'Peter'], 'McCaul': ['Michael', 'Mike'], 'Warner': ['Mark'],
         'Cotton': ['Tom', 'Thomas'],
         'Scott': ['Tim', 'Timothy'], 'Neal': ['Richard', 'Richie']}      # drawn since Nov 15, 2026 with Ricketts, on the count of articles (Ricketts was searched before and stood at two pages)                 # drawn in the map since Nov 14, 2026: named for his letter of Oct 2025 on Megaspeed (an act on the matter before these days)
# Since the eleventh reading (Nov 16, 2026) each member's list holds the given name the roster of sitting members gives and its usual short form (James for Himes,
# William for Huizenga and so on); that reading tested these and further forms and found no article they add. Not added: other given names for the Speaker
# ("Michael Johnson" and "James Johnson" are other people's names too; he is matched as "Mike Johnson" or "Speaker Johnson").
# 'Eric' for Crawford (his legal given name; the pages mostly call him Rick): the tenth reading, Nov 16, 2026, found two articles that name him so and
# were not counted. scripts/nv8_member_sweep.py now stops when its wider forms find an article for a drawn member that these names do not.
# Surnames shared with another current member: only the full name counts ("Speaker Johnson" is taken as him, "Sen. Johnson" is not).
FULL_ONLY = {'Johnson': r"(?:Speaker\s+(?:Mike\s+)?|Mike\s+)Johnson", 'Scott': r"\bTim(?:othy)?\s+Scott\b"}        # "Sen. Scott" may be the senator from Florida
# Surnames met after a title that are not members of Congress, or are members named only in passing lists; read by hand.
NOT_MEMBER = set()


# Members named on three or more pages for other things, so not drawn: first names; True = a title then the surname also counts
# (no other member shares it); what the pages name them for (read on Nov 14, 2026).
NOT_DRAWN = {'Jordan': (['Jim'], False, 'his election as House minority leader'), 'Stevens': (['Haley'], False, 'an endorsement and an absence from a vote'),
             'Massie': (['Thomas'], True, 'his bid to impeach the defense secretary'), 'Garcia': (['Robert'], False, 'other inquiries he plans as incoming oversight chair'),
             'Hyde-Smith': (['Cindy'], True, 'losing her Senate race'), 'Sanders': (['Bernie', 'Bernard'], True, 'the Senate leadership contest and his own AI bill'),
             # found by the sweep of all sitting members' names (scripts/nv8_member_sweep.py, Nov 16, 2026)
             'Sullivan': (['Dan', 'Daniel'], False, 'his own Senate race, still being counted, and a candidate of the same name')}
# other words met after a congressional title on three or more pages that are not a searched name: what each is
NOT_A_MEMBER = {'Rep': 'a second title, as in "Chairman Rep." before a member\'s name', 'Jamieson': 'the U.S. trade representative', 'Greer': 'the U.S. trade representative', 'Eric': 'a former member (Swalwell)', 'Swalwell': 'a former member',
                'Anthony': 'a former member (Weiner)', 'Weiner': 'a former member', 'Harvey': "Nvidia's board chair", 'Jones': "Nvidia's board chair",
                'Jensen': 'Huang ("Nvidia Leader ... Jensen Huang")', 'Huang': 'Nvidia\'s chief executive ("Nvidia Leader Before Jensen Huang", "Board Chair After Jensen Huang")', 'Tae-won': 'the chairman of a Korean company'}


def not_drawn_re(s):
    firsts, by_title, _ = NOT_DRAWN[s]
    return re.compile(rf"\b(?:{'|'.join(firsts)})\s+(?:[A-Z]\.\s+)?{s}\b" + (rf"|{TITLE}\s+(?:[A-Z][\w.'’-]*\s+){{0,2}}{s}\b" if by_title else ''))


# The pages of the first census are a closed list (research/nv8_first_census_pages.txt, the 1,086 ids of the released table). Until Nov 16, 2026
# every folder with a 200 page and an id outside the SKIP prefixes counted as one; that day another session saved five pages under new ids
# (a broadcast of Nov 15 and two posts) and they entered the count. A page saved later is counted only if research/nv8_pages_added.tsv lists it.
_fc = R / 'nv8_first_census_pages.txt'
FIRST_CENSUS = frozenset(_fc.read_text().split()) if _fc.exists() else frozenset()


# A page's article taken again from its saved HTML: the fourth extraction (scripts/recover_bodies_2.py) is read before the third
RECOVERED = ('text.recovered2.txt', 'text.recovered.txt')


def added(d):
    """A passage of the page's own piece that the saved HTML holds and the extraction left out (a table, a photo caption): text.added.txt,
    written by scripts/recover_bodies_3.py after each passage was read (Nov 16, 2026). It is read after the page's text, in every count."""
    f = d / 'text.added.txt'
    return '\n' + f.read_text(errors='replace') if f.exists() else ''


def pages(recovered=True):
    """(id, text) of each counted page; an address saved under two ids is counted once (the first id). Where a third extraction of
    the piece's own body exists (text.recovered.txt, scripts/recover_bodies.py, Nov 16, 2026) it is the text read; recovered=False gives
    the text as read until then (the three-chairmen figure's count keeps it)."""
    seen = set()
    for d in sorted(P.iterdir()):
        if d.name.startswith(SKIP) or not (d / 'meta.json').exists() or (FIRST_CENSUS and d.name not in FIRST_CENSUS):
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
            rec = next((d / n for n in RECOVERED if (d / n).exists()), d / RECOVERED[-1])
            yield d.name, (rec.read_text(errors='replace') if recovered and rec.exists() else max(texts, key=len)) + added(d)


def saved_since_text(pid):
    """The text read for a page saved since the first census: the article text its saver cut out (text.article.txt) where there is one;
    otherwise the longer of the first extraction and a second one (a transcript's first extraction held the speaker labels only)."""
    d = P / pid
    for n in RECOVERED + ('text.article.txt',):
        if (d / n).exists():
            return ((d / n).read_text(errors='replace') + added(d)).translate(LIGATURES)
    texts = [f.read_text(errors='replace') for f in (d / 'text.txt', d / 'text.reextract.txt') if f.exists()]
    return (max(texts, key=len) + added(d)).translate(LIGATURES) if texts else ''


# A page saved by hand as a PDF gives some letter pairs as one sign (the ff of "Jeffries", the fi of "officials"). They are written out
# before a page is read, so that a name is found and a copy of an article shares its words with the original (Nov 16, 2026: the minority
# leader's name on three hand-saved pages had not been counted). No page of the first census holds such a sign.
LIGATURES = str.maketrans({'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl', 'ﬅ': 'st', 'ﬆ': 'st'})


def articles():
    """{article id: [(page id, text)]} for every counted article of research/nv8_articles.tsv, in the table's order; only the
    copies that are themselves counted are read."""
    first = dict(pages()); art = {}; seen_first = set()
    for r in csv.DictReader(open(R / 'nv8_articles.tsv', newline=''), delimiter='\t'):
        pid = r['page_id']
        if r['set'] == 'first census':
            assert pid in first, ('research/nv8_articles.tsv lists a first-census page that is no longer counted; rerun scripts/nv8_articles.py', pid)
            seen_first.add(pid); text = first[pid]
        else:
            text = saved_since_text(pid)
        if r['counted'] == 'yes':
            art.setdefault(r['article_id'], []).append((pid, text))
    assert seen_first == set(first), ('a page was saved since research/nv8_articles.tsv was built; rerun scripts/nv8_articles.py', sorted(set(first) - seen_first)[:5])
    return art


def member_re(sur):
    if sur in FULL_ONLY:
        return re.compile(FULL_ONLY[sur])
    firsts = '|'.join(FIRST[sur])
    return re.compile(rf"\b(?:{firsts})\s+(?:[A-Z]\.\s+)?{sur}\b|{TITLE}\s+(?:[A-Z][\w.'’-]*\s+){{0,2}}{sur}\b")


def count():
    """(articles counted, {surname: [article ids]}, {other surname after a title: {article ids}})"""
    res = {s: member_re(s) for s in FIRST}
    hit, other, n = defaultdict(list), defaultdict(set), 0
    for aid, copies in articles().items():
        n += 1
        for s, rx in res.items():
            if any(rx.search(text) for _, text in copies):
                hit[s].append(aid)
        for _, text in copies:
            for m in AFTER.finditer(text):
                for w in m.group(1).split():
                    w = w.strip(".,'’")
                    if w not in FIRST and len(w) > 2:
                        other[w].add(aid)
    return n, hit, other


def count_pages():
    """(pages counted, {surname: [page ids]}) over the pages of the first census alone, as counted until Nov 15, 2026: the three-chairmen
    figure (nv13) prints these ("named on N of the 1,086 saved pages") and keeps them."""
    res = {s: member_re(s) for s in FIRST}; hit, n = defaultdict(list), 0
    for pid, text in pages(recovered=False):
        n += 1
        for s, rx in res.items():
            if rx.search(text):
                hit[s].append(pid)
    return n, hit


def main():
    n, hit, other = count()
    with open(R / 'member_mentions.tsv', 'w') as f:
        f.write(f'# saved articles naming each member; articles counted: {n}\nsurname\tarticles\n')
        for s in FIRST:
            f.write(f'{s}\t{len(hit[s])}\n')
    # page-level list, so each count can be checked page by page (audit1b): drawn members, then the members named that often for other things
    arts = articles()
    with open(R / 'member_mentions_pages.tsv', 'w') as f:
        f.write('# one line per member: the counted articles that name them (ids of research/nv8_articles.tsv)\nsurname\tnamed_on_three_or_more\tarticles\tarticle_ids\n')
        for s in FIRST:
            f.write(f"{s}\t{'yes' if len(hit[s]) >= 3 else 'no'}\t{len(hit[s])}\t{' '.join(hit[s])}\n")
        for s in NOT_DRAWN:
            rx = not_drawn_re(s)
            ids = [aid for aid, copies in arts.items() if any(rx.search(t) for _, t in copies)]
            f.write(f"{s}\tno (named for other things)\t{len(ids)}\t{' '.join(ids)}\n")
    cand = sorted(((len(v), k) for k, v in other.items() if len(v) >= 4), reverse=True)
    with open(R / 'member_candidates.tsv', 'w') as f:
        f.write('# other words found after a congressional title on four or more pages (to read by hand)\nword\tpages\n')
        f.writelines(f'{k}\t{c}\n' for c, k in cand)
    print('articles counted', n)
    print('members:', ', '.join(f'{s} {len(hit[s])}' for s in FIRST))
    print('other words after a title, 4+ pages:', ', '.join(f'{k} {c}' for c, k in cand[:120]))


if __name__ == '__main__':
    main()
