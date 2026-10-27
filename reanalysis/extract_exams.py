# Phase 3: extract the main reading passage of the new exam papers into staging/Panhellenics/.
# Sources: data/exam_sources.csv. PDFs are cached in data/exam_pdfs/ (gitignored).
import csv, hashlib, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / 'data' / 'exam_sources.csv'
PDFS = HERE / 'data' / 'exam_pdfs'
UA = 'Mozilla/5.0 (panhel-corpora extract_exams.py)'

def load_sources(path=SOURCES):
    with Path(path).open(encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))

def fetch(row, dest=PDFS):
    """Download row['url'] to dest/<file>.pdf unless cached; return (path, sha256)."""
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{row['file']}.pdf"
    if not path.exists():
        req = urllib.request.Request(row['url'], headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if not data.startswith(b'%PDF-'):
            raise ValueError(f"{row['file']}: download is not a PDF ({row['url']})")
        path.write_bytes(data)
    data = path.read_bytes()
    if not data.startswith(b'%PDF-'):
        raise ValueError(f"{row['file']}: cached file is not a PDF ({path})")
    return path, hashlib.sha256(data).hexdigest()

if __name__ == '__main__':
    for row in load_sources():
        path, sha = fetch(row)
        print(row['file'], sha[:12], path.stat().st_size)
