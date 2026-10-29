import numpy as np
import pandas as pd
import pytest
from separation import FEATURES, design, nested_cv, final_fit, permutation_p

def separable(n=20, p=5, seed=0):
    rng = np.random.default_rng(seed)
    y = np.r_[np.zeros(n), np.ones(n)]
    X = rng.normal(size=(2 * n, p)); X[:, 0] += 3 * y      # only feature 0 carries signal
    return X, y

def test_nested_cv_separable_data():
    X, y = separable()
    r = nested_cv(X, y)
    assert r['auc'] > 0.9 and r['accuracy'] > 0.8 and len(r['prob']) == 40
    assert r['selected'].shape == (40, 5) and r['selected'][:, 0].mean() >= 0.8

def test_nested_cv_no_leakage_constant_in_fold():
    X, y = separable(); X[0, 1] = 50.0
    r = nested_cv(X, y)
    assert np.isfinite(r['prob']).all()

def test_final_fit_sign():
    X, y = separable()
    assert final_fit(X, y)['coef'][0] > 0

def test_design_uses_version_and_labels():
    F = pd.DataFrame({'book': ['English 1', 'English 1', 'Panhellenics'], 'text': ['u1', 'u1', '2010-06'],
                      'version': ['full', 'first360', 'full'], **{f: [1.0, 2.0, 3.0] for f in FEATURES}})
    X, y, ids = design(F, 'first360')
    assert X.shape == (2, 21) and list(y) == [0, 1] and X[0, 0] == 2.0

def test_permutation_p_small_on_signal_and_bounds():
    X, y = separable(n=10)
    r = permutation_p(X, y, nested_cv(X, y)['auc'], n_perm=9, n_jobs=1)
    assert r['p'] == pytest.approx(1 / 10) and len(r['null_aucs']) == 9
