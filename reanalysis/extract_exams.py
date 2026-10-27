# Phase 3: extract the main reading passage of the new exam papers into staging/Panhellenics/.
# Sources: data/exam_sources.csv. PDFs are cached in data/exam_pdfs/ (gitignored).
import csv, datetime, hashlib, re, statistics, urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / 'data' / 'exam_sources.csv'
PDFS = HERE / 'data' / 'exam_pdfs'
UA = 'Mozilla/5.0 (panhel-corpora extract_exams.py)'
STAGING = HERE / 'staging' / 'Panhellenics'
CORRECTIONS = HERE / 'data' / 'exam_corrections.csv'
APPROVALS = HERE / 'data' / 'exam_approvals.csv'

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
        text = ws[0]['text']
        for a, b in zip(ws, ws[1:]):  # words split by a font change (e.g. a U+2010 hyphen) touch: no space
            text += ('' if b['x0'] - a['x1'] < 0.5 else ' ') + b['text']
        out.append(dict(text=text, x0=ws[0]['x0'], x1=max(w['x1'] for w in ws),
                        top=min(w['top'] for w in ws), bottom=max(w['bottom'] for w in ws)))
    return out

DOMAIN = re.compile(r'\b[\w-]+\.(?:com|org|net|gov|edu|co\.uk)\b')

def is_end_marker(line_text):
    s = line_text.strip()
    if s.startswith(('Adapted from', 'http', 'www.', 'ΤΕΛΟΣ')) or 'ΣΕΛΙΔ' in s:  # footer, also when split by columns
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
        main = [dict(w) for w in kept if style(w) == body]
        off = []
        for w in (w for w in kept if style(w) != body):
            host = next((b for b in main if style(w)[0] == body[0] and style(w)[1] < body[1]
                         and abs(w['top'] - b['top']) <= 3 and -1 <= w['x0'] - b['x1'] <= 2), None)
            if host:  # superscript, e.g. the "th" of "10th": attach to its word
                host['text'] += w['text']; host['x1'] = w['x1']
            else:
                off.append(w)
        for l in group_lines(main):
            lines.append(dict(l, col=i))
        dropped += [l['text'] for l in group_lines(off)]
    return lines, dropped

def overlapping_lines(lines):
    """(upper, lower) text of vertically overlapping consecutive lines in a column: one of them is likely hidden."""
    return [(a['text'], b['text']) for a, b in zip(lines, lines[1:])
            if a.get('col') == b.get('col') and b['top'] < a['bottom'] - 1]

def paragraphs(lines, known=None):
    """Join one column's lines into paragraphs; returns (paragraphs, words rejoined at a line-end hyphen).
    With a lexicon, a split compound keeps its hyphen when the joined form is unknown but both parts are known."""
    if not lines:
        return [], []
    right = max(l['x1'] for l in lines); width = right - min(l['x0'] for l in lines)
    gaps = [b['top'] - a['bottom'] for a, b in zip(lines, lines[1:])]
    g = max(statistics.median(gaps), 1.0) if gaps else 1.0
    paras, dehyph, cur = [], [], ''
    for i, l in enumerate(lines):
        t = l['text'].strip()
        if cur and re.search(r'[A-Za-z]-$', cur) and t[:1].islower():
            left, nxt = cur.split()[-1][:-1], t.split()[0]
            a, b = left.lower(), re.sub(r'\W+$', '', nxt).lower()
            if known and (a + b) not in known and a in known and b in known:
                dehyph.append(f'{left}-{nxt}'); cur = cur + t
            else:
                dehyph.append(left + nxt); cur = cur[:-1] + t
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

# ---- corrections, suspects, output ----

def _read_csv(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))

def load_corrections(path=CORRECTIONS):
    return _read_csv(path)

def apply_corrections(text, file, rows):
    for r in rows:
        if r['file'] != file:
            continue
        n = text.count(r['find'])
        if n != 1:
            raise ValueError(f"{file}: correction find {r['find']!r} occurs {n} times (must be 1)")
        text = text.replace(r['find'], r['replace'])
    return text

ALLOWED = set('‘’“”–—…é')

def suspects(text, families, norms):
    """(token, reason) pairs for Greg to check; nothing here is changed automatically."""
    out, seen = [], set()
    for m in re.finditer(r'[A-Za-z]*[a-z]I[a-z]+|[A-Za-z]*[a-z]Is\b', text):
        out.append((m.group(), 'capital-I')); seen.add(m.group())
    for m in re.finditer(r'\b(?![AI]\b)[A-Z] [a-z]{2,}', text):  # "I" and "A" are words
        out.append((m.group(), 'split-letter'))
    for m in re.finditer(r'[A-Za-z]+', text):
        tok = m.group()
        if tok in seen or tok in ('I', 'A', 'a'):
            continue
        initial = re.search(r'(^|[.!?]["”’]?\s+)$', text[:m.start()]) is not None
        if tok[0].isupper() and not initial:
            continue  # a name; proper nouns are reviewed separately
        if tok.lower() not in families and tok.lower() not in norms:
            out.append((tok, 'unknown')); seen.add(tok)
    for ch in sorted({c for c in text if not (32 <= ord(c) < 127) and c not in ALLOWED and c != '\n'}):
        out.append((ch, 'odd-char'))
    return out

def split_headings(paras):
    keep, heads = [], []
    for p in paras:
        (heads if len(p.split()) <= 8 and not re.search(r'[.?!"”’:]$', p) else keep).append(p)
    return keep, heads

def extract(pdf, columns, known=None):
    import pdfplumber
    with pdfplumber.open(pdf) as doc:
        page = doc.pages[1]
        words = page.extract_words(extra_attrs=['fontname', 'size'])
        lines, dropped = passage_lines(words, page.width, columns)
    paras, dehyph = [], []
    for c in sorted({l['col'] for l in lines}):
        ps, dh = paragraphs([l for l in lines if l['col'] == c], known)
        if paras and ps and not re.search(r'[.?!"”’:]$', paras[-1]):
            paras[-1] = f'{paras[-1]} {ps.pop(0)}'   # paragraph continues into the next column
        paras += ps; dehyph += dh
    paras, heads = split_headings([clean(p) for p in paras])
    return dict(paragraphs=paras, dropped_offstyle=dropped, dropped_headings=heads, dehyphenated=dehyph,
                overlapping_lines=overlapping_lines(lines))

def write_text(path, paras):
    Path(path).write_bytes('\r\n\r\n'.join(paras).encode('utf-8'))

def main():
    from lexical import load_families, load_norms
    families = load_families(HERE / 'data' / 'bnc_coca')
    norms = load_norms(HERE / 'data' / 'brysbaert_concreteness.xlsx')
    corrections = load_corrections()
    approved = {r['file'] for r in _read_csv(APPROVALS)}
    STAGING.mkdir(parents=True, exist_ok=True)
    report = ['# Exam passage review', '',
              'Compare each file in `staging/Panhellenics/` with page 2 of its PDF in `data/exam_pdfs/`.',
              'Nothing listed below has been changed automatically.', '']
    sources = ['# Exam paper sources', '', '| File | Page | Download | SHA-256 | Downloaded |', '|---|---|---|---|---|']
    for row in load_sources():
        f = row['file']
        pdf, sha = fetch(row)
        r = extract(pdf, int(row['columns']), set(families) | set(norms))
        text = apply_corrections('\n\n'.join(r['paragraphs']), f, corrections)
        paras = text.split('\n\n')
        write_text(STAGING / f'{f}.txt', paras)
        flagged = suspects(text, families, norms)
        report += [f'## {f}', '',
                   f"- Words: {len(text.split())}; paragraphs: {len(paras)}; columns: {row['columns']}; approved: {'yes' if f in approved else 'no'}",
                   f"- Corrections applied: {sum(c['file'] == f for c in corrections)}",
                   f"- Off-style text excluded: {'; '.join(r['dropped_offstyle']) or 'none'}",
                   f"- **Overlapping lines (one may be hidden text; check the page):** {'; '.join(f'[{a}] / [{b}]' for a, b in r['overlapping_lines']) or 'none'}",
                   f"- Headings dropped: {'; '.join(r['dropped_headings']) or 'none'}",
                   f"- Words rejoined across a line-end hyphen: {', '.join(r['dehyphenated']) or 'none'}",
                   f"- Suspect tokens: {', '.join(f'{t} ({why})' for t, why in flagged) or 'none'}", '']
        day = datetime.date.fromtimestamp(pdf.stat().st_mtime).isoformat()
        sources.append(f"| {f} | {row['page_url']} | {row['url']} | `{sha}` | {day} |")
    (HERE / 'results' / 'exam_review.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    (HERE / 'data' / 'EXAM_SOURCES.md').write_text('\n'.join(sources) + '\n', encoding='utf-8')
    print(f'wrote {len(load_sources())} staging files, results/exam_review.md, data/EXAM_SOURCES.md')

if __name__ == '__main__':
    main()
