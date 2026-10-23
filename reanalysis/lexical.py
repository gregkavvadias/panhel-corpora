# Phase 2 lexical profile: BNC/COCA word-family coverage and Brysbaert concreteness per text.
# Resources come from fetch_resources.py; see data/SOURCES.md and the Phase 2 design spec.
import csv
from pathlib import Path
import pandas as pd

BASE = range(1, 31)      # frequency bands, 1k families each
PROPN_LIST = 31          # proper nouns
SUPP = {32, 33, 34, 35}  # marginal words, compounds, abbreviations, accented spellings: counted as known

def load_families(dirpath):
    """Lower-cased form -> list number; a form on several lists keeps the lowest number."""
    index = {}
    for f in Path(dirpath).glob('basewrd*.txt'):
        n = int(f.stem[len('basewrd'):])
        for line in f.read_text(encoding='utf-8').splitlines():
            if line.strip():
                form = line.split()[0].lower()
                index[form] = min(n, index.get(form, n))
    return index

def load_norms(path):
    """Lower-cased single-word lemma -> Brysbaert Conc.M."""
    d = pd.read_excel(path)
    d = d[~d['Word'].astype(str).str.strip().str.contains(' ')]
    return {str(w).strip().lower(): float(c) for w, c in zip(d['Word'], d['Conc.M'])}

def load_overrides(path):
    """Greg's manual proper-noun decisions: lower-cased type -> 'proper' | 'common'."""
    path = Path(path)
    if not path.exists():
        return {}
    out = {}
    with path.open(encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            t, label = row['type'].strip().lower(), row['label'].strip().lower()
            if label not in ('proper', 'common'):
                raise ValueError(f'propn override for {t!r}: label must be proper or common, got {label!r}')
            out[t] = label
    return out

def classify(form, lemma, pos, families, overrides):
    """(category, list_no, reason); category in propn / band / supp / offlist."""
    f, l = form.lower(), lemma.lower()
    ov = overrides.get(f)
    if ov == 'proper':
        return ('propn', None, 'override')
    lst = families.get(f) or families.get(l)
    if lst == PROPN_LIST:
        return ('offlist', None, 'override') if ov == 'common' else ('propn', None, 'list31')
    if lst in BASE:
        return ('band', lst, '')
    if lst in SUPP:
        return ('supp', lst, '')
    if pos == 'PROPN' and ov != 'common':
        return ('propn', None, 'tag')
    return ('offlist', None, '')
