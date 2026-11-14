"""Pull every itemised individual contribution whose contributor gave a stated employer, for one two-year cycle, through
the host's shared FEC queue (fec-get), page by page, into a new folder.
Run: python3 -I scripts/fec_sched_a_employer.py <EMPLOYER WORD> <cycle> <done marker file>
     -> research/primary/fec-sched_a-employer-<employer>-<cycle>/page-NNN.json
The FEC matches the employer word as text, so "NVIDIA" also returns "NVIDIA CORPORATION" and the like; the lines keep the
employer exactly as filed. A page already saved is kept and not fetched again; nothing is overwritten. The same call is
used for both companies. The done marker is written only when the last page has been read."""
import json, sys
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fec_get_pull import get, PRIMARY


def main():
    emp, cycle, marker = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    d = PRIMARY / f'fec-sched_a-employer-{emp.lower()}-{cycle}'; d.mkdir(parents=True, exist_ok=True)
    base = (f'https://api.open.fec.gov/v1/schedules/schedule_a/?contributor_employer={quote(emp)}&two_year_transaction_period={cycle}'
            f'&is_individual=true&per_page=100&sort=-contribution_receipt_date')
    url, n, lines, count = base, 0, 0, None
    while True:
        n += 1
        j = get(url, d / f'page-{n:03d}.json')
        res = j.get('results') or []; lines += len(res)
        pg = j.get('pagination') or {}; count = pg.get('count') if count is None else count
        li = pg.get('last_indexes')
        if not res or not li:
            break
        url = base + ''.join(f'&{k}={quote(str(v))}' for k, v in li.items() if v is not None)
        assert n < 400, 'more pages than expected'
    summary = {'employer_word': emp, 'cycle': cycle, 'pages': n, 'lines': lines, 'count_reported_on_first_page': count}
    (d / 'SUMMARY.json').write_text(json.dumps(summary, indent=1) + '\n')
    marker.parent.mkdir(parents=True, exist_ok=True); marker.write_text(json.dumps(summary) + '\n')
    print(summary)


if __name__ == '__main__':
    main()
