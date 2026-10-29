from pathlib import Path
from check_numbers import unmatched
from wordcount import count
from numbers_build import build

ROOT = Path(__file__).resolve().parents[2]

def test_check_numbers_normalises_formats():
    nums = "- g = −1.15 [−1.85, −0.62]; p = .0001; BH p = .0004; coverage 97.86%"
    draft = "concreteness g = -1.15 (95% CI [-1.85, -0.62]), p = 0.0001, coverage 97.86"
    assert unmatched(draft, nums) == []

def test_check_numbers_flags_unknown_value():
    assert unmatched("g = 0.73", "- g = 0.72") == ["0.73"]

def test_check_numbers_ignores_years_and_small_integers():
    assert unmatched("In 2010, 27 texts and 26 exam texts; Nation (2006); n = 53", "") == []

def test_wordcount_excludes_tables_comments_headings():
    md = ("# Title\n\nOne two three.\n\n| a | b |\n|---|---|\n| x | y |\n\n<!-- note -->\n[CHECK: content]\n\n"
          "## References\n\nSmith (2020).")
    assert count(md) == 3

def test_numbers_build_contains_primary_rows():
    text = build(ROOT / 'reanalysis' / 'results')
    assert all(m in text for m in ('cov5k', 'conc_tok', 'mlc', 'cwo_adj'))
