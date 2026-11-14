"""Take from the FEC's bulk file of itemised individual contributions (indivNN.zip, member itcont.txt) every line whose
EMPLOYER field begins with one of the given words, and save those lines unchanged as a source.
Run: python3 -I scripts/fec_bulk_employer.py <path to indivNN.zip> <url it was fetched from> <WORD> [<WORD> ...]
Writes research/primary/fec-bulk-<zip stem>-employers-<YYYYMMDD>/  lines.txt  the file's own lines, pipe-delimited, unchanged
                                                                 meta.json  the zip's sha256, size and date, the rule, counts
The zip itself is not kept in the project (it is several GB and the FEC republishes it weekly); its sha256 is recorded.
Only itcont.txt is read: the zip's by_date files repeat the same lines. One pass, streamed; nothing is unpacked to disk."""
import hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; PRIMARY = ROOT / 'research' / 'primary'
COLS = ['CMTE_ID', 'AMNDT_IND', 'RPT_TP', 'TRANSACTION_PGI', 'IMAGE_NUM', 'TRANSACTION_TP', 'ENTITY_TP', 'NAME', 'CITY', 'STATE', 'ZIP_CODE', 'EMPLOYER', 'OCCUPATION',
        'TRANSACTION_DT', 'TRANSACTION_AMT', 'OTHER_ID', 'TRAN_ID', 'FILE_NUM', 'MEMO_CD', 'MEMO_TEXT', 'SUB_ID']


def main():
    zp, url, words = Path(sys.argv[1]), sys.argv[2], [w.upper() for w in sys.argv[3:]]
    assert words and all(w.isalnum() for w in words), words
    names = subprocess.run(['unzip', '-Z1', str(zp)], capture_output=True, text=True, check=True).stdout.split()
    assert 'itcont.txt' in names, names[:5]
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    d = PRIMARY / f'fec-bulk-{zp.stem}-employers-{today}'; d.mkdir(parents=True, exist_ok=False)
    pat = r'\|(' + '|'.join(words) + ')'
    cmd = f"set -o pipefail; unzip -p '{zp}' itcont.txt | tee >(wc -l > '{d}/total_lines.txt') | LC_ALL=C grep -a -i -E '{pat}' || test $? -eq 1"
    out = subprocess.run(['bash', '-c', cmd], capture_output=True, check=True).stdout.decode('utf-8', 'replace')
    kept, bad = [], 0
    for ln in out.splitlines():
        f = ln.split('|')
        if len(f) != len(COLS):
            bad += 1; continue
        if any(f[11].strip().upper().startswith(w) for w in words):
            kept.append(ln)
    (d / 'lines.txt').write_text('|'.join(COLS) + '\n' + '\n'.join(kept) + '\n', encoding='utf-8')
    os.link(d / 'lines.txt', d / 'text.txt')          # the row checker reads a source folder's text.txt
    h = hashlib.sha256()
    with open(zp, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b''):
            h.update(chunk)
    st = zp.stat()
    meta = {'id': d.name, 'kind': 'FEC bulk file, filtered', 'url': url, 'zip_sha256': h.hexdigest(), 'zip_bytes': st.st_size,
            'zip_saved_utc': datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'member_read': 'itcont.txt',
            'rule': 'lines whose EMPLOYER field begins with one of: ' + ', '.join(words) + ' (letter case ignored)', 'lines_in_itcont': int((d / 'total_lines.txt').read_text().split()[0]),
            'lines_kept': len(kept), 'lines_with_another_field_count': bad, 'by_word': {w: sum(1 for ln in kept if ln.split('|')[11].strip().upper().startswith(w)) for w in words},
            'latest_transaction_date_kept': max((ln.split('|')[13][4:] + '-' + ln.split('|')[13][:2] + '-' + ln.split('|')[13][2:4] for ln in kept if len(ln.split('|')[13]) == 8), default='')}
    (d / 'meta.json').write_text(json.dumps(meta, indent=1) + '\n'); os.remove(d / 'total_lines.txt')
    print(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()
