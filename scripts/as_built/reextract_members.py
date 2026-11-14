"""Read the member lists of three trade associations out of their saved pages, where the members are logos (the name is in an
image's alt text or a link's title, which a plain text extraction drops). Writes text.reextract.txt beside each saved page.
Run: python3 -I scripts/reextract_members.py       (it refuses to write over an existing reading)"""
import json, re
from pathlib import Path
P = Path(__file__).resolve().parents[1] / 'research' / 'primary'
PAGES = {'art-sia-members': ('Semiconductor Industry Association', r'<div class="sponsor">\s*<a href="[^"]*"[^>]*>\s*<div class="sponsor-inner">\s*<img [^>]*alt="([^"]+)"'),
         'art-iti-members': ('Information Technology Industry Council', r'<a href="[^"]*" class="[^"]*" title="([^"]+)" target="_blank">\s*<div class="svg-wrapper member-company__logo"'),
         'art-technet-members': ('TechNet', r'itemid="https://www\.technet\.org/membership/[^"]+/" content="([^"]+)"')}
for pid, (group, pat) in PAGES.items():
    d = P / pid; m = json.loads((d / 'meta.json').read_text()); assert m['status'] == 200
    names = []
    for n in re.findall(pat, (d / 'body.html').read_text(errors='replace')):
        n = re.sub(r'\s+', ' ', n.replace('&amp;', '&').replace('&#038;', '&').replace('&#8217;', "'")).strip()
        if n and n not in names:
            names.append(n)
    assert len(names) >= 20, (pid, len(names))
    has = {c: any(re.search(rf'\b{c}\b', n, re.I) for n in names) for c in ('Nvidia', 'Anthropic')}
    t = (f'URL: {m["url"]}\nFETCHED: {m["fetched_utc"]}\n\nMEMBERS OF {group.upper()} AS LISTED ON THE SAVED PAGE ({len(names)} names; each is the alt text or title of a member\'s logo, '
         f'read from the saved HTML by script):\n' + '\n'.join(names) + f'\n\nNvidia is {"listed" if has["Nvidia"] else "not listed"}. Anthropic is {"listed" if has["Anthropic"] else "not listed"}.\n'
         'A page of this kind shows the members on the day it was saved; it does not say when a company joined.\n')
    f = d / 'text.reextract.txt'
    if f.exists():
        print(pid, 'already read; nothing written')
    else:
        f.write_text(t)
    print(pid, len(names), has)
