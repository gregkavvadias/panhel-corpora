# Phase 4 RQ2 (b): does genre account for the difference between exam and coursebook texts?
# Labels: data/genre_labels.csv (Claude proposes with a reason; Greg confirms). See the Phase 4 spec.
from pathlib import Path
import pandas as pd

COARSE = {'fiction': 'narrative', 'personal': 'narrative', 'biography': 'narrative',
          'informational': 'non-narrative', 'argumentative': 'non-narrative', 'speech': 'non-narrative',
          'review': 'non-narrative'}
FINE = set(COARSE) | {'other'}

def load_labels(path, texts, require_confirmed=True):
    """Validated labels for exactly the given (book, text) pairs; errors name the offending text."""
    L = pd.read_csv(path, dtype=str, keep_default_na=False)
    for r in L.itertuples():
        where = f'{r.book}/{r.text}'
        if r.fine not in FINE:
            raise ValueError(f'{where}: unknown fine label {r.fine!r}')
        if r.fine == 'other':
            if r.coarse not in ('narrative', 'non-narrative'):
                raise ValueError(f'{where}: label "other" needs coarse narrative or non-narrative')
        elif r.coarse != COARSE[r.fine]:
            raise ValueError(f'{where}: coarse {r.coarse!r} does not match fine {r.fine!r}')
        if not r.reason.strip():
            raise ValueError(f'{where}: empty reason')
        if require_confirmed and r.status != 'confirmed':
            raise ValueError(f'{where}: label not confirmed (status {r.status!r})')
    keys = set(zip(L.book, L.text))
    for b, t in sorted(set(texts) - keys):
        raise ValueError(f'{b}/{t}: no genre label')
    for b, t in sorted(keys - set(texts)):
        raise ValueError(f'{b}/{t}: labelled but not in the corpus')
    return L
