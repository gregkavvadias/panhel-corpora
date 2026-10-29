# Blind second coder for the genre labels: draws the sample, prepares the coder pack, computes Cohen's kappa.
# See docs/superpowers/specs/2026-10-29-paper-design.md (second genre coder).
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
from corpus import is_exam

HERE = Path(__file__).resolve().parent
PACK = HERE.parent / 'paper' / 'second-coder'

def draw_sample(labels, n=20, seed=1):
    """One text per fine label in use, then filled in proportion to group size; seeded random order."""
    rng = np.random.default_rng(seed)
    L = labels.reset_index(drop=True)
    picked = [int(rng.choice(L.index[L.fine == f])) for f in sorted(L.fine.unique())]
    exam = L.book.map(is_exam)
    for grp in (True, False):
        target = round(n * (exam == grp).mean())
        have = sum(exam[i] == grp for i in picked)
        pool = [i for i in L.index[exam == grp] if i not in picked]
        k = max(0, min(target - have, n - len(picked), len(pool)))
        picked += [int(i) for i in rng.choice(pool, size=k, replace=False)]
    rest = [i for i in L.index if i not in picked]
    picked += [int(i) for i in rng.choice(rest, size=n - len(picked), replace=False)] if len(picked) < n else []
    order = rng.permutation(picked)
    return L.loc[order, ['book', 'text']].reset_index(drop=True)

def kappa(a, b, column):
    """Cohen's kappa on `column` for two raters' label tables aligned on book/text."""
    from sklearn.metrics import cohen_kappa_score
    ka, kb = set(zip(a.book, a.text)), set(zip(b.book, b.text))
    if ka != kb:
        diff = sorted(t for _, t in ka ^ kb)
        raise ValueError(f'rater files cover different texts: {", ".join(diff)}')
    m = a.merge(b, on=['book', 'text'], suffixes=('_a', '_b'))
    return float(cohen_kappa_score(m[f'{column}_a'], m[f'{column}_b']))

def main():
    from corpus import TEXTS_DIR
    labels = pd.read_csv(HERE / 'data' / 'genre_labels.csv', dtype=str, keep_default_na=False)
    S = draw_sample(labels)
    (PACK / 'texts').mkdir(parents=True, exist_ok=True)
    key = []
    for i, r in enumerate(S.itertuples(), start=1):
        nn = f'{i:02d}'
        shutil.copyfile(TEXTS_DIR / r.book / f'{r.text}.txt', PACK / 'texts' / f'{nn}.txt')
        key.append(dict(NN=nn, book=r.book, text=r.text))
    pd.DataFrame(key)[['NN']].to_csv(PACK / 'sample.csv', index=False)
    pd.DataFrame(key).to_csv(PACK / 'key.csv', index=False)
    print(f'wrote {len(key)} texts to {PACK / "texts"}; key in key.csv (do not send to the coder)')

if __name__ == '__main__':
    main()
