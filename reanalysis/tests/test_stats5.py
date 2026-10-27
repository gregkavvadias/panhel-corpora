import numpy as np
import pandas as pd
import pytest
from stats5 import tost_welch, thresholds, sitting, exam_subsets

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

def test_sitting():
    assert sitting('2023-06') == 'june' and sitting('2018-09') == 'resit'
    with pytest.raises(ValueError):
        sitting('unit-2-1')

def test_exam_subsets_sizes():
    ids = [f'{y}-06' for y in range(2010, 2027)] + [f'{y}-09' for y in range(2018, 2027)]
    S = exam_subsets(pd.DataFrame({'text': ids}))
    assert (len(S['all']), len(S['june']), len(S['original13'])) == (26, 17, 13)

def test_sitting_rows_labels_and_direction():
    from stats5 import sitting_rows
    E = pd.DataFrame({'text': ['2020-06', '2021-06', '2022-06', '2020-09', '2021-09', '2022-09'],
                      'cov5k': [97., 98, 99, 98, 99, 100], 'conc_tok': [3., 3, 3.1, 3, 3.1, 3]})
    Z = sitting_rows(E).set_index('measure')
    assert {'june_M', 'resit_M'} <= set(Z.columns) and not {'school_M', 'exam_M'} & set(Z.columns)
    assert Z.loc['cov5k', 'diff'] == 1.0 and Z.loc['cov5k', 'june_M'] == 98.0
