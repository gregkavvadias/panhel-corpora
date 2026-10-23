# Text loading and the length-matching window shared by the Phase 2 scripts.
from pathlib import Path

TEXTS_DIR = Path(__file__).resolve().parent.parent / 'Texts'

def iter_texts(base=TEXTS_DIR):
    """Yield (book, text_id, raw_text) sorted by book, then file name."""
    for f in sorted(Path(base).glob('*/*.txt'), key=lambda p: (p.parent.name, p.name)):
        yield f.parent.name, f.stem, f.read_text(encoding='utf-8', errors='replace')

def is_exam(book):
    return book == 'Panhellenics'

def window(doc, n=360):
    """Whole sentences from the start of doc until at least n alphabetic tokens (as features.window)."""
    out = []; c = 0
    for s in doc.sents:
        out.append(s.text); c += sum(t.is_alpha for t in s)
        if c >= n: break
    return ' '.join(out)
