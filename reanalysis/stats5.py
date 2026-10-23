# Phase 2 comparisons on results/lexical_features.csv (see the Phase 2 design spec).
# Primary: TOST on 5k coverage (margin +-2 points) and Welch test on token-weighted concreteness, full texts.
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from corpus import is_exam
from effects import hedges, boot_ci

MARGIN = 2.0

def _welch(a, b):
    va, vb = np.var(a, ddof=1) / len(a), np.var(b, ddof=1) / len(b)
    se = np.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    return np.mean(b) - np.mean(a), se, df

def tost_welch(a, b, margin):
    """Equivalence of mean(b) - mean(a) within +-margin: two one-sided Welch tests, 90% CI."""
    diff, se, df = _welch(a, b)
    q = stats.t.ppf(.95, df)
    p_lower = stats.t.sf((diff + margin) / se, df)   # H0: diff <= -margin
    p_upper = stats.t.cdf((diff - margin) / se, df)  # H0: diff >= +margin
    lo, hi = diff - q * se, diff + q * se
    return dict(diff=diff, ci90_lo=lo, ci90_hi=hi, df=df, p_lower=p_lower, p_upper=p_upper,
                p_tost=max(p_lower, p_upper), equivalent=bool(-margin < lo and hi < margin))

def compare(a, b):
    """School (a) vs exam (b): means, exam - school difference, Hedges' g with bootstrap CI, Welch and Mann-Whitney p."""
    lo, hi = boot_ci(a, b)
    return dict(school_M=np.mean(a), exam_M=np.mean(b), diff=np.mean(b) - np.mean(a), g=hedges(a, b),
                g_lo=lo, g_hi=hi, p_welch=stats.ttest_ind(b, a, equal_var=False).pvalue,
                p_mw=stats.mannwhitneyu(b, a, alternative='two-sided').pvalue)

def thresholds(F):
    """Group means of cov1k..cov9k on full texts and the first level reaching 95% / 98%."""
    F = F[F.version == 'full'].assign(group=lambda d: np.where(d.book.map(is_exam), 'exam', 'school'))
    cols = [f'cov{k}k' for k in range(1, 10)]
    T = F.groupby('group')[cols].mean().reset_index()
    for th in (95, 98):
        T[f'level_{th}'] = [next((k for k in range(1, 10) if r[f'cov{k}k'] >= th), 'not reached by 9k')
                            for _, r in T.iterrows()]
    return T

def main():
    F = pd.read_csv('results/lexical_features.csv')
    exam = F[F.book.map(is_exam) & (F.version == 'full')]
    school = {v: F[~F.book.map(is_exam) & (F.version == v)] for v in ('full', 'first360')}
    # (measure, school version, role); exam texts are always full (already ~350 words)
    spec = [('cov5k', 'full', 'primary'), ('conc_tok', 'full', 'primary'),
            ('cov5k', 'first360', 'robustness'), ('conc_tok', 'first360', 'robustness'),
            ('cov5k_base_only', 'full', 'robustness'), ('cov5k_propn_known', 'full', 'robustness'),
            ('conc_type', 'full', 'robustness')]
    spec += [(f'cov{k}k', 'full', 'descriptive') for k in range(1, 10) if k != 5]
    rows = []
    for m, v, role in spec:
        r = dict(measure=m, version=v, role=role, **compare(school[v][m].values, exam[m].values))
        if role == 'descriptive':
            r.update(p_welch=np.nan, p_mw=np.nan)
        rows.append(r)
    C = pd.DataFrame(rows)
    prim = C.role == 'primary'
    C['p_welch_BH'] = np.nan
    C.loc[prim, 'p_welch_BH'] = multipletests(C.loc[prim, 'p_welch'], method='fdr_bh')[1]
    C.to_csv('results/lexical_comparisons.csv', index=False)
    T = pd.DataFrame([dict(measure='cov5k', version=v, role=role, margin=MARGIN,
                           **tost_welch(school[v].cov5k.values, exam.cov5k.values, MARGIN))
                      for v, role in (('full', 'primary'), ('first360', 'robustness'))])
    T.to_csv('results/lexical_tost.csv', index=False)
    H = thresholds(F)
    H.to_csv('results/lexical_thresholds.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    for name, D in (('Comparisons', C), ('TOST (exam - school, percentage points)', T), ('Thresholds', H)):
        print(f'\n== {name}'); print(D.round(4).to_string(index=False))
    if T.equivalent.nunique() > 1:
        print('\nDISAGREEMENT: full vs length-matched TOST differ — equivalence must be reported as qualified (spec §5).')

if __name__ == '__main__':
    main()
