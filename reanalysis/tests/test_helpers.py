import numpy as np
from corpus import iter_texts, is_exam, remove_headings, load_headings
from effects import hedges, boot_ci

def test_iter_texts_counts():
    books = [b for b, _, _ in iter_texts()]
    assert books.count('English 1') == 10
    assert books.count('English 2') == 17
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

def test_unit_4_1_excluded_and_stars_stripped():
    t = {(b, x): r for b, x, r in iter_texts()}
    assert ('English 2', 'unit-4-1') not in t and '**' not in t[('English 2', 'unit-8-2')]

def test_remove_headings_whole_lines_only():
    raw = 'Nelson Mandela\r\n\r\nI met Nelson Mandela.\r\nNelson Mandela\r\nEnd.'
    assert remove_headings(raw, {'Nelson Mandela'}) == '\r\nI met Nelson Mandela.\r\nEnd.'

def test_heading_lines_all_present_in_files():
    t = {(b, x): r for b, x, r in iter_texts()}
    hs = load_headings()
    assert sum(len(v) for v in hs.values()) == 16
    for key, lines in hs.items():
        file_lines = {l.strip() for l in t[key].splitlines()}
        assert lines <= file_lines, key
