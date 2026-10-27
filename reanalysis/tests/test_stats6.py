import math
import numpy as np
import pandas as pd
import pytest
from stats6 import spearman_ci, comparisons, validation, PRIMARY, VALIDATION

MEASURES = sorted(set(PRIMARY) | set(VALIDATION) | {'fam', 'mtld', 'clauses_per_sent'})

@pytest.fixture
def F_fixture():
    rng = np.random.default_rng(0)
    rows = []
    for i in range(6):
        for book, text in (('English 1', f'unit-{i}'), ('Panhellenics', f'{2010 + i}-06'), ('Panhellenics', f'{2018 + i}-09')):
            versions = ['full', 'first360'] if book == 'English 1' else ['full']
            for v in versions:
                rows.append(dict(book=book, text=text, version=v, **{m: rng.normal() for m in MEASURES}))
    return pd.DataFrame(rows)

@pytest.fixture
def cm_fixture(F_fixture):
    f = F_fixture[F_fixture.version == 'full']
    rng = np.random.default_rng(1)
    return pd.DataFrame(dict(book=f.book.values, text=f.text.values,
                             **{c: rng.normal(size=len(f)) for c in VALIDATION.values()}))

def test_spearman_ci_perfect_and_small_n():
    r = spearman_ci([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
    assert r['rho'] == pytest.approx(1.0) and r['n'] == 5
    assert math.isnan(spearman_ci([1, 2, 3], [1, 2, 3])['lo'])

def test_primary_family_has_four_and_bh_only_there(F_fixture):
    C = comparisons(F_fixture)
    prim = C[C.role == 'primary']
    assert sorted(prim.measure) == sorted(PRIMARY) and prim.p_welch_BH.notna().all()
    assert C[C.role != 'primary'].p_welch_BH.isna().all()
    assert C[C.role == 'descriptive'].p_welch.isna().all()
    assert prim.set_index('measure').loc['cov5k', 'equivalent'] in (True, False)

def test_robustness_rows_for_new_primaries(F_fixture):
    R = comparisons(F_fixture).query("role == 'robustness'")
    assert set(R.measure) == {'mlc', 'cwo_adj'}
    assert set(zip(R.version, R.subset)) == {('first360', 'all'), ('full', 'june'), ('full', 'original13')}

def test_validation_groups(F_fixture, cm_fixture):
    V = validation(F_fixture, cm_fixture)
    assert set(V.group) == {'pooled', 'school', 'exam'} and len(V) == 3 * len(VALIDATION)
