import numpy as np
from corpus import iter_texts, is_exam
from effects import hedges, boot_ci

def test_iter_texts_counts():
    books = [b for b, _, _ in iter_texts()]
    assert books.count('English 1') == 10
    assert books.count('English 2') == 18
    assert books.count('Panhellenics') == 26

def test_is_exam():
    assert is_exam('Panhellenics') and not is_exam('English 1')

def test_hedges_known_value():
    assert np.isclose(hedges(np.array([1., 2, 3]), np.array([2., 3, 4])), 0.8)

def test_boot_ci_brackets_g_and_is_seeded():
    a, b = np.arange(10.), np.arange(10.) + 3
    lo, hi = boot_ci(a, b, B=500)
    assert lo < hedges(a, b) < hi
    assert (lo, hi) == boot_ci(a, b, B=500)
