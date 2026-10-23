import numpy as np
import pandas as pd
from stats5 import tost_welch, thresholds

def test_tost_equivalent_when_ci_inside_margin():
    a = np.array([90., 91, 92, 90, 91, 92, 90, 91]); b = a + 0.3
    r = tost_welch(a, b, 2.0)
    assert r['equivalent'] and r['p_tost'] < .05 and np.isclose(r['diff'], 0.3)

def test_tost_not_equivalent_when_diff_large():
    a = np.array([90., 91, 92, 90, 91, 92]); b = a + 3
    assert not tost_welch(a, b, 2.0)['equivalent']

def test_tost_ci_matches_welch_90():
    a, b = np.array([1., 2, 3, 4, 5]), np.array([2., 4, 6, 8])
    r = tost_welch(a, b, 10.0)
    from statsmodels.stats.weightstats import CompareMeans, DescrStatsW
    lo, hi = CompareMeans(DescrStatsW(b), DescrStatsW(a)).tconfint_diff(alpha=.10, usevar='unequal')
    assert np.isclose(r['ci90_lo'], lo) and np.isclose(r['ci90_hi'], hi)

def test_thresholds_levels():
    F = pd.DataFrame({'book': ['English 1', 'Panhellenics'], 'version': ['full'] * 2,
                      **{f'cov{k}k': [79 + 2 * k, 85 + 2 * k] for k in range(1, 10)}})
    T = thresholds(F).set_index('group')
    assert T.loc['exam', 'level_95'] == 5 and T.loc['school', 'level_95'] == 8
    assert T.loc['school', 'level_98'] == 'not reached by 9k'
