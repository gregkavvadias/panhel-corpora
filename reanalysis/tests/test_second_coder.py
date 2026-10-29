import pandas as pd
import pytest
from second_coder import draw_sample, kappa

@pytest.fixture
def labels53():
    return pd.read_csv('data/genre_labels.csv', dtype=str, keep_default_na=False)

def test_sample_stratified_and_blind(labels53):
    S = draw_sample(labels53)
    m = labels53.merge(S, on=['book', 'text'])
    assert len(S) == 20 and set(m.fine) == set(labels53.fine)
    assert S.book.eq('Panhellenics').any() and (~S.book.eq('Panhellenics')).any()
    assert list(S.columns) == ['book', 'text'] and S.equals(draw_sample(labels53))

def test_kappa_handles_unused_label_and_rejects_mismatch():
    a = pd.DataFrame({'book': ['b'] * 4, 'text': list('wxyz'),
                      'coarse': ['narrative', 'narrative', 'non-narrative', 'non-narrative']})
    b = a.assign(coarse=['narrative', 'non-narrative', 'non-narrative', 'non-narrative'])
    assert 0 < kappa(a, b, 'coarse') < 1
    with pytest.raises(ValueError, match='z'):
        kappa(a, b[b.text != 'z'], 'coarse')
