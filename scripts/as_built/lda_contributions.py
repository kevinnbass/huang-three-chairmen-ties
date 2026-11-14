"""Save every lobbyist contribution report (form LD-203) that names a given honoree, from the Senate's lobbying API (lda.gov).
Run: python3 -I scripts/lda_contributions.py <HONOREE WORD> <year> [<year> ...]
Writes research/primary/lda-gov-contrib-<word>-<year>/page-NNN.json (the API's pages, unchanged) and meta.json when a year is
complete. Saved pages are reused. One request every 5 seconds (the API allows 15 a minute without a key).
The reports hold lobbyists' names: they stay in research/primary and are never copied into a figure, a table or a release."""
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parents[1]; PRIMARY = ROOT / 'research' / 'primary'
UA = {'User-Agent': 'research-script (lobbying disclosure reader)', 'Accept': 'application/json'}


def main(word, years):
    for y in years:
        d = PRIMARY / f'lda-gov-contrib-{word.lower()}-{y}'; d.mkdir(exist_ok=True)
        if (d / 'meta.json').exists():
            print(word, y, 'already complete'); continue
        url = f'https://lda.gov/api/v1/contributions/?contribution_honoree={word}&filing_year={y}&page_size=25'; n = 0; count = None
        while url:
            n += 1; f = d / f'page-{n:03d}.json'
            if f.exists():
                j = json.loads(f.read_text())
            else:
                for attempt in range(6):
                    r = requests.get(url, headers=UA, timeout=60)
                    if r.status_code == 200:
                        break
                    time.sleep(20 * (attempt + 1))                # a refusal is waited out, never hurried
                else:
                    raise SystemExit(f'{word} {y} page {n}: HTTP {r.status_code}')
                f.write_text(r.text, encoding='utf-8'); j = r.json(); time.sleep(5)
            count = j.get('count', count); url = j.get('next')
        (d / 'meta.json').write_text(json.dumps({'id': d.name, 'url': f'https://lda.gov/api/v1/contributions/?contribution_honoree={word}&filing_year={y}&page_size=25', 'what': f'U.S. Senate lobbying records: lobbyists\' contribution reports (LD-203) naming an honoree matching "{word}", filing year {y}',
                                                   'pages': n, 'reports': count, 'fetched_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'status': 'official record; holds lobbyists\' names'}, indent=1))
        print(word, y, 'pages', n, 'reports', count)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
