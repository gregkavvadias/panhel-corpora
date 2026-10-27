# Phase 3 part 2: the difficulty table (27 coursebook vs 26 exam texts) and validation against Coh-Metrix.
# Primary family (BH on Welch p, full texts): cov5k, conc_tok, mlc, cwo_adj. See the design spec and README.
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from corpus import is_exam
from stats5 import compare, tost_welch, exam_subsets, MARGIN

PRIMARY = ['cov5k', 'conc_tok', 'mlc', 'cwo_adj']
NEW_PRIMARY = ['mlc', 'cwo_adj']
DIMENSION = {
    'cov5k': 'vocabulary', 'conc_tok': 'vocabulary', 'imag': 'vocabulary', 'fam': 'vocabulary',
    'mtld': 'vocabulary', 'hdd': 'vocabulary',
    'mlc': 'syntax', 'clauses_per_sent': 'syntax', 'mean_sent_len': 'syntax', 'passive_inc': 'syntax',
    'np_inc': 'syntax', 'vp_inc': 'syntax', 'adjp_inc': 'syntax', 'pp_inc': 'syntax', 'neg_inc': 'syntax',
    'gerund_inc': 'syntax', 'inf_inc': 'syntax',
    'cwo_adj': 'cohesion', 'sem_overlap': 'cohesion', 'conn_inc': 'cohesion', 'causal_inc': 'cohesion',
    'fre': 'readability', 'fkgl': 'readability'}
VALIDATION = {'conc_tok': 'WRDCNCc', 'imag': 'WRDIMGc', 'hdd': 'LDVOCD', 'mean_sent_len': 'DESSL',
              'passive_inc': 'DRPVAL', 'np_inc': 'DRNP', 'vp_inc': 'DRVP', 'adjp_inc': 'DRAP', 'pp_inc': 'DRPP',
              'neg_inc': 'DRNEG', 'gerund_inc': 'DRGERUND', 'inf_inc': 'DRINF', 'cwo_adj': 'CRFSOa',
              'conn_inc': 'CNCAll', 'causal_inc': 'SMCAUSvp', 'sem_overlap': 'LSASSp', 'fre': 'RDFRE',
              'fkgl': 'RDFKGL'}

def spearman_ci(x, y):
    """Spearman rho with a Fisher-z 95% CI (NaN CI when n < 4)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y)); n = int(ok.sum())
    rho, p = stats.spearmanr(x[ok], y[ok])
    if n < 4 or abs(rho) >= 1:
        lo = hi = np.nan if n < 4 else rho
    else:
        z, se = np.arctanh(rho), 1 / np.sqrt(n - 3)
        lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
    return dict(rho=float(rho), lo=float(lo), hi=float(hi), p=float(p), n=n)

def _split(F, version):
    exam = F[F.book.map(is_exam) & (F.version == 'full')]
    school = F[~F.book.map(is_exam) & (F.version == version)]
    return school, exam

def comparisons(F):
    """Primary (BH over the four), robustness (new primaries) and descriptive (g and CI only) rows."""
    rows = []
    school, exam = _split(F, 'full')
    for m in PRIMARY:
        r = dict(measure=m, dimension=DIMENSION[m], role='primary', version='full', subset='all',
                 **compare(school[m].values, exam[m].values))
        if m == 'cov5k':
            t = tost_welch(school[m].values, exam[m].values, MARGIN)
            r.update(ci90_lo=t['ci90_lo'], ci90_hi=t['ci90_hi'], p_tost=t['p_tost'], equivalent=t['equivalent'])
        rows.append(r)
    s360, _ = _split(F, 'first360')
    subsets = exam_subsets(exam)
    for m in NEW_PRIMARY:
        rows.append(dict(measure=m, dimension=DIMENSION[m], role='robustness', version='first360', subset='all',
                         **compare(s360[m].values, exam[m].values)))
        for name in ('june', 'original13'):
            rows.append(dict(measure=m, dimension=DIMENSION[m], role='robustness', version='full', subset=name,
                             **compare(school[m].values, subsets[name][m].values)))
    for m in (m for m in DIMENSION if m not in PRIMARY and m in F.columns):
        r = dict(measure=m, dimension=DIMENSION[m], role='descriptive', version='full', subset='all',
                 **compare(school[m].values, exam[m].values))
        r.update(p_welch=np.nan, p_mw=np.nan)
        rows.append(r)
    C = pd.DataFrame(rows)
    prim = C.role == 'primary'
    C['p_welch_BH'] = np.nan
    C.loc[prim, 'p_welch_BH'] = multipletests(C.loc[prim, 'p_welch'], method='fdr_bh')[1]
    return C

def validation(F, cm):
    """Spearman rho of each new measure with its Coh-Metrix counterpart: pooled and within each group."""
    M = F[F.version == 'full'].merge(cm, on=['book', 'text'])
    groups = {'pooled': M, 'school': M[~M.book.map(is_exam)], 'exam': M[M.book.map(is_exam)]}
    return pd.DataFrame([dict(measure=m, cohmetrix=c, group=g, **spearman_ci(G[m], G[c]))
                         for m, c in VALIDATION.items() for g, G in groups.items()])

def main():
    keys = ['book', 'text', 'version']
    F = pd.read_csv('results/lexical_features.csv')[keys + ['cov5k', 'conc_tok']].merge(
        pd.read_csv('results/difficulty_features.csv'), on=keys)
    C = comparisons(F); C.to_csv('results/difficulty_comparisons.csv', index=False)
    V = validation(F, pd.read_csv('data/cohmetrix_appA.csv')); V.to_csv('results/difficulty_validation.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    cols = ['measure', 'dimension', 'role', 'version', 'subset', 'school_M', 'exam_M', 'g', 'g_lo', 'g_hi',
            'p_welch', 'p_welch_BH']
    print(C[cols].round(4).to_string(index=False))
    print(V.pivot(index=['measure', 'cohmetrix'], columns='group', values='rho').round(2).to_string())

if __name__ == '__main__':
    main()
