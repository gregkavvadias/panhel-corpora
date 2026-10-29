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

# ---- analyses (run only on confirmed labels) ----

WITHIN = ['conc_tok', 'passive_inc']
MIN_N = 5

def _group(books):
    from corpus import is_exam
    return books.map(lambda b: 'exam' if is_exam(b) else 'school')

def composition(labels):
    """Counts of fine label by group, with totals."""
    C = pd.crosstab(labels.fine, _group(labels.book)).reindex(columns=['school', 'exam'], fill_value=0)
    C.loc['total'] = C.sum()
    return C

def fisher(labels):
    """Coarse genre x group: Fisher's exact p and the conditional MLE odds ratio with its exact 95% CI."""
    from scipy.stats import fisher_exact
    from scipy.stats.contingency import odds_ratio
    g = _group(labels.book)
    table = [[int(((labels.coarse == c) & (g == grp)).sum()) for grp in ('school', 'exam')]
             for c in ('narrative', 'non-narrative')]
    o = odds_ratio(table, kind='conditional'); ci = o.confidence_interval(0.95)
    return dict(table=table, p=float(fisher_exact(table)[1]), odds_ratio=float(o.statistic),
                or_lo=float(ci.low), or_hi=float(ci.high))

def _merged(F, labels):
    return F[F.version == 'full'].merge(labels[['book', 'text', 'coarse']], on=['book', 'text'])

def within_genre(F, labels):
    """Non-narrative coursebook vs non-narrative exam texts on conc_tok and passive_inc (BH over the two);
    descriptive only (no p-values) if either side has fewer than 5 texts."""
    import numpy as np
    from statsmodels.stats.multitest import multipletests
    from stats5 import compare
    M = _merged(F, labels); M = M[M.coarse == 'non-narrative']
    g = _group(M.book)
    s, e = M[g == 'school'], M[g == 'exam']
    small = len(s) < MIN_N or len(e) < MIN_N
    W = pd.DataFrame([dict(measure=m, n_school=len(s), n_exam=len(e), descriptive_only=small,
                           **compare(s[m].values, e[m].values)) for m in WITHIN])
    if small:
        W[['p_welch', 'p_mw']] = np.nan
        W['p_welch_BH'] = np.nan
    else:
        W['p_welch_BH'] = multipletests(W.p_welch, method='fdr_bh')[1]
    return W

def regression_check(F, labels):
    """OLS of each within-genre measure on group, without and with coarse genre (full texts; descriptive)."""
    import statsmodels.formula.api as smf
    M = _merged(F, labels).assign(exam=lambda d: (_group(d.book) == 'exam').astype(int),
                                  narrative=lambda d: (d.coarse == 'narrative').astype(int))
    rows = []
    for m in WITHIN:
        u = smf.ols(f'{m} ~ exam', M).fit(); a = smf.ols(f'{m} ~ exam + narrative', M).fit()
        lo, hi = a.conf_int().loc['exam']
        rows.append(dict(measure=m, coef_unadj=u.params['exam'], coef_adj=a.params['exam'], adj_lo=lo, adj_hi=hi,
                         p_adj=a.pvalues['exam'], narrative_coef=a.params['narrative'],
                         pct_change=100 * (a.params['exam'] - u.params['exam']) / u.params['exam']))
    return pd.DataFrame(rows)

def main():
    from corpus import iter_texts
    from stats6 import load_features
    labels = load_labels(Path('data/genre_labels.csv'), {(b, t) for b, t, _ in iter_texts()})
    F = load_features()
    C = composition(labels); C.to_csv('results/genre_composition.csv')
    fi = fisher(labels)
    pd.DataFrame([dict(narrative_school=fi['table'][0][0], narrative_exam=fi['table'][0][1],
                       nonnarrative_school=fi['table'][1][0], nonnarrative_exam=fi['table'][1][1],
                       p=fi['p'], odds_ratio=fi['odds_ratio'], or_lo=fi['or_lo'], or_hi=fi['or_hi'])]
                 ).to_csv('results/genre_fisher.csv', index=False)
    A = pd.read_csv('results/difficulty_comparisons.csv').query("role in ('primary', 'descriptive')")
    A = A[['measure', 'g', 'g_lo', 'g_hi']].rename(columns={'g': 'g_all', 'g_lo': 'g_all_lo', 'g_hi': 'g_all_hi'})
    W = within_genre(F, labels).merge(A, on='measure'); W.to_csv('results/genre_within.csv', index=False)
    R = regression_check(F, labels); R.to_csv('results/genre_regression.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    print(C.to_string()); print(fi)
    print(W.round(4).to_string(index=False)); print(R.round(4).to_string(index=False))

if __name__ == '__main__':
    main()
