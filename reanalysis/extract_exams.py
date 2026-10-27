# Phase 3: extract the main reading passage of the new exam papers into staging/Panhellenics/.
# Sources: data/exam_sources.csv. PDFs are cached in data/exam_pdfs/ (gitignored).
import csv, hashlib, re, statistics, urllib.request
from collections import Counter
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

# ---- passage extraction from pdfplumber words (text, x0, x1, top, bottom, fontname, size) ----

def style(w):
    """(font family, size to 0.5pt): 'GCNONE+Arial-BoldMT' -> 'Arial'."""
    name = w['fontname'].split('+', 1)[-1]
    family = re.split(r'[-,]', name)[0]
    if family.endswith('MT'):
        family = family[:-2]
    return family, round(w['size'] * 2) / 2

def body_style(words):
    c = Counter()
    for w in words:
        c[style(w)] += len(w['text'])
    return c.most_common(1)[0][0]

def group_lines(words):
    lines = []
    for w in sorted(words, key=lambda w: (w['top'], w['x0'])):
        if lines and abs(w['top'] - lines[-1]['top']) <= 2.0:
            lines[-1]['words'].append(w)
        else:
            lines.append(dict(top=w['top'], words=[w]))
    out = []
    for l in lines:
        ws = sorted(l['words'], key=lambda w: w['x0'])
        out.append(dict(text=' '.join(w['text'] for w in ws), x0=ws[0]['x0'], x1=max(w['x1'] for w in ws),
                        top=min(w['top'] for w in ws), bottom=max(w['bottom'] for w in ws)))
    return out

DOMAIN = re.compile(r'\b[\w-]+\.(?:com|org|net|gov|edu|co\.uk)\b')

def is_end_marker(line_text):
    s = line_text.strip()
    if s.startswith(('Adapted from', 'http', 'www.', 'ΤΕΛΟΣ')):
        return True
    if re.fullmatch(r'\(?(?:[A-Z][a-z]+ )?\d{4}\)?', s):
        return True
    return len(s.split()) <= 8 and bool(DOMAIN.search(s))

def passage_lines(words, page_width, columns):
    """Body-style lines of the passage in reading order (each line has 'col'), plus dropped off-style line texts."""
    start = next((l for l in group_lines(words) if 'Read the text below' in l['text']), None)
    if start is None:
        raise ValueError('no "Read the text below" line on the page')
    region = [w for w in words if w['top'] > start['bottom']]
    cols = [region] if columns == 1 else [
        [w for w in region if (w['x0'] + w['x1']) / 2 < page_width / 2],
        [w for w in region if (w['x0'] + w['x1']) / 2 >= page_width / 2]]
    body = body_style(region)
    lines, dropped = [], []
    for i, col in enumerate(cols):
        end = next((l['top'] for l in group_lines(col) if is_end_marker(l['text'])), float('inf'))
        kept = [w for w in col if w['top'] < end - 1]
        for l in group_lines([w for w in kept if style(w) == body]):
            lines.append(dict(l, col=i))
        dropped += [l['text'] for l in group_lines([w for w in kept if style(w) != body])]
    return lines, dropped

def paragraphs(lines):
    """Join one column's lines into paragraphs; returns (paragraphs, dehyphenated words)."""
    if not lines:
        return [], []
    right = max(l['x1'] for l in lines); width = right - min(l['x0'] for l in lines)
    gaps = [b['top'] - a['bottom'] for a, b in zip(lines, lines[1:])]
    g = max(statistics.median(gaps), 1.0) if gaps else 1.0
    paras, dehyph, cur = [], [], ''
    for i, l in enumerate(lines):
        t = l['text'].strip()
        if cur and re.search(r'[A-Za-z]-$', cur) and t[:1].islower():
            joined = cur.split()[-1][:-1] + t.split()[0]
            dehyph.append(joined); cur = cur[:-1] + t
        else:
            cur = f'{cur} {t}' if cur else t
        short = l['x1'] < right - 0.15 * width
        gap = i < len(gaps) and gaps[i] > 1.8 * g
        if short or gap or i == len(lines) - 1:
            paras.append(cur); cur = ''
    return paras, dehyph

LIGATURES = {'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl', '­': ''}

def clean(text):
    for a, b in LIGATURES.items():
        text = text.replace(a, b)
    return re.sub(r'\s+', ' ', text).strip()

if __name__ == '__main__':
    for row in load_sources():
        path, sha = fetch(row)
        print(row['file'], sha[:12], path.stat().st_size)
