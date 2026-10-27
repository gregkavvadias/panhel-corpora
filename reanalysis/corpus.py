# Text loading and the length-matching window shared by the Phase 2+ scripts.
import csv
from pathlib import Path

TEXTS_DIR = Path(__file__).resolve().parent.parent / 'Texts'
DATA = Path(__file__).resolve().parent / 'data'

def _rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))

def load_exclusions(path=DATA / 'excluded_texts.csv'):
    """(book, text) pairs left out of every analysis from Phase 3 part 2 on (see the CSV for reasons)."""
    return {(r['book'], r['text']) for r in _rows(path)} if Path(path).exists() else set()

def iter_texts(base=TEXTS_DIR, exclude=None):
    """Yield (book, text_id, raw_text) sorted by book, then file name; markdown '**' removed."""
    exclude = load_exclusions() if exclude is None else exclude
    for f in sorted(Path(base).glob('*/*.txt'), key=lambda p: (p.parent.name, p.name)):
        if (f.parent.name, f.stem) not in exclude:
            yield f.parent.name, f.stem, f.read_text(encoding='utf-8', errors='replace').replace('**', '')

def load_headings(path=DATA / 'heading_lines.csv'):
    """(book, text) -> set of title/subheading lines that the sentence-based measures skip."""
    out = {}
    for r in _rows(path):
        out.setdefault((r['book'], r['text']), set()).add(r['line'].strip())
    return out

def remove_headings(raw, headings):
    """Drop whole lines whose stripped text is a listed heading; everything else is kept as is."""
    return ''.join(l for l in raw.splitlines(keepends=True) if l.strip() not in headings)

def is_exam(book):
    return book == 'Panhellenics'

def window(doc, n=360):
    """Whole sentences from the start of doc until at least n alphabetic tokens (as features.window)."""
    out = []; c = 0
    for s in doc.sents:
        out.append(s.text); c += sum(t.is_alpha for t in s)
        if c >= n: break
    return ' '.join(out)
