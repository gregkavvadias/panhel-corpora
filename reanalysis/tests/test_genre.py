import math
import numpy as np
import pandas as pd
import pytest
from genre import load_labels, composition, fisher, within_genre, regression_check

@pytest.fixture
def lab8():
    rows = [dict(book='English 1', text=f'u{i}', fine='fiction' if i < 4 else 'informational',
                 coarse='narrative' if i < 4 else 'non-narrative', reason='x', status='confirmed') for i in range(8)]
    rows += [dict(book='Panhellenics', text=f'{2010 + i}-06', fine='informational', coarse='non-narrative',
                  reason='x', status='confirmed') for i in range(8)]
    return pd.DataFrame(rows)

@pytest.fixture
def F8(lab8):
    rng = np.random.default_rng(0)
    F = lab8[['book', 'text']].assign(version='full')
    exam = F.book.eq('Panhellenics').to_numpy()
    return F.assign(conc_tok=rng.normal(size=len(F)) - 0.5 * exam, passive_inc=rng.normal(size=len(F)) - exam)

def test_composition_counts(lab8):
    C = composition(lab8)
    assert C.loc['fiction', 'school'] == 4 and C.loc['informational', 'exam'] == 8

def test_fisher_table_and_or(lab8):
    r = fisher(lab8)
    assert r['table'] == [[4, 0], [4, 8]] and 0 <= r['p'] <= 1

def test_fisher_zero_cell(lab8):
    assert math.isfinite(fisher(lab8)['or_lo'])

def test_within_genre_filters_both_sides(F8, lab8):
    W = within_genre(F8, lab8).set_index('measure')
    assert W.loc['conc_tok', 'n_school'] == 4 and W.loc['conc_tok', 'n_exam'] == 8

def test_within_genre_small_group_descriptive(F8, lab8):
    W = within_genre(F8, lab8)
    assert W.descriptive_only.all() and W.p_welch.isna().all() and W.g.notna().all()

def test_within_genre_tested_when_large_enough(F8, lab8):
    lab = lab8.copy(); lab.loc[lab.text.isin(['u0', 'u1', 'u2']), ['fine', 'coarse']] = ['informational', 'non-narrative']
    W = within_genre(F8, lab)
    assert not W.descriptive_only.any() and W.p_welch_BH.notna().all()

def test_regression_check_columns(F8, lab8):
    R = regression_check(F8, lab8)
    assert set(R.measure) == {'conc_tok', 'passive_inc'} and {'coef_unadj', 'coef_adj', 'pct_change'} <= set(R.columns)

TEXTS = {('English 1', 'u1'), ('Panhellenics', '2010-06')}
HEAD = 'book,text,fine,coarse,reason,status\n'

def test_load_labels_ok(tmp_path):
    p = tmp_path / 'g.csv'
    p.write_text(HEAD + 'English 1,u1,fiction,narrative,a story,confirmed\n'
                        'Panhellenics,2010-06,informational,non-narrative,explains a study,confirmed\n')
    assert len(load_labels(p, TEXTS)) == 2

@pytest.mark.parametrize('rows, msg', [
    ('English 1,u1,poem,narrative,x,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,fiction,non-narrative,x,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,other,,x,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,fiction,narrative,,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,fiction,narrative,x,confirmed\n', '2010-06'),
])
def test_load_labels_validation_errors(tmp_path, rows, msg):
    p = tmp_path / 'g.csv'; p.write_text(HEAD + rows)
    with pytest.raises(ValueError, match=msg):
        load_labels(p, TEXTS)

def test_load_labels_requires_confirmed(tmp_path):
    p = tmp_path / 'g.csv'
    p.write_text(HEAD + 'English 1,u1,fiction,narrative,x,proposed\n'
                        'Panhellenics,2010-06,informational,non-narrative,x,confirmed\n')
    with pytest.raises(ValueError, match='u1'):
        load_labels(p, TEXTS)
    assert len(load_labels(p, TEXTS, require_confirmed=False)) == 2
