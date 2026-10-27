import pandas as pd
import pytest
import math
from collections import namedtuple
from lexical import classify, load_families, load_norms, load_overrides, profile

LISTS = {
    1: 'HUNGRY 3194\r\n\tHUNGER 1124\r\nGO 1\r\n\tWENT 1\r\nMAY 1\r\n',
    5: 'RAY 1\r\n',
    12: 'HEFT 1\r\n',
    30: 'HEFT 0\r\n',
    31: 'ENGLISH 1\r\nTURKEY 1\r\n',
    32: 'OH 1\r\n',
    34: 'NASA 1\r\n',
    35: 'CAFÉ 0\r\n',
}

@pytest.fixture
def families(tmp_path):
    for n, body in LISTS.items():
        (tmp_path / f'basewrd{n}.txt').write_bytes(body.encode('utf-8'))
    return load_families(tmp_path)

def test_load_families_members_and_lowest_list(families):
    assert families['hunger'] == 1 and families['ray'] == 5
    assert families['heft'] == 12

def test_band_and_supp(families):
    assert classify('ray', 'ray', 'NOUN', families, {}) == ('band', 5, '')
    assert classify('oh', 'oh', 'INTJ', families, {}) == ('supp', 32, '')

def test_propn_tag_on_band_list_is_band(families):
    assert classify('Hungry', 'hungry', 'PROPN', families, {})[0] == 'band'
    assert classify('May', 'May', 'PROPN', families, {})[0] == 'band'

def test_list31_is_propn_regardless_of_tag(families):
    assert classify('English', 'English', 'ADJ', families, {}) == ('propn', None, 'list31')

def test_tagged_propn_offlist_is_propn(families):
    assert classify('Zorba', 'Zorba', 'PROPN', families, {}) == ('propn', None, 'tag')
    assert classify('zorbify', 'zorbify', 'VERB', families, {}) == ('offlist', None, '')

def test_lemma_fallback(families):
    assert classify('hungrier', 'hungry', 'ADJ', families, {})[0] == 'band'
    assert classify('went', 'go', 'VERB', families, {}) == ('band', 1, '')

def test_case_and_accents(families):
    assert classify('NASA', 'NASA', 'PROPN', families, {}) == ('supp', 34, '')
    assert classify('café', 'café', 'NOUN', families, {}) == ('supp', 35, '')

def test_overrides_apply(families):
    assert classify('Ray', 'Ray', 'PROPN', families, {'ray': 'proper'})[0] == 'propn'
    assert classify('turkey', 'turkey', 'NOUN', families, {'turkey': 'common'})[0] == 'offlist'
    assert classify('Zorba', 'Zorba', 'PROPN', families, {'zorba': 'common'})[0] == 'offlist'

def test_overrides_missing_file(tmp_path):
    assert load_overrides(tmp_path / 'none.csv') == {}

def test_overrides_bad_value(tmp_path):
    p = tmp_path / 'o.csv'; p.write_text('type,label\nray,maybe\n')
    with pytest.raises(ValueError, match='ray'):
        load_overrides(p)

def test_load_norms_lowercase_singleword(tmp_path):
    p = tmp_path / 'n.xlsx'
    pd.DataFrame({'Word': ['Apple', 'a cappella', 'idea'], 'Conc.M': [5.0, 3.0, 1.6]}).to_excel(p, index=False)
    assert load_norms(p) == {'apple': 5.0, 'idea': 1.6}

Tok = namedtuple('Tok', 'text lemma_ pos_ is_alpha')
NORMS = {'hunger': 2.0, 'ray': 4.0}

def test_profile_coverage_excludes_propn(families):
    toks = [Tok('hunger', 'hunger', 'NOUN', True), Tok('ray', 'ray', 'NOUN', True),
            Tok('heft', 'heft', 'VERB', True), Tok('oh', 'oh', 'INTJ', True),
            Tok('Zorba', 'Zorba', 'PROPN', True), Tok(',', ',', 'PUNCT', False)]
    row, hits = profile(toks, families, NORMS, {})
    assert row['n_tokens'] == 5 and row['n_propn'] == 1
    assert row['cov1k'] == 50.0            # hunger + oh / 4
    assert row['cov5k'] == 75.0            # + ray
    assert row['cov9k'] == 75.0            # heft is list 12
    assert row['cov5k_base_only'] == 50.0  # hunger + ray
    assert row['cov5k_propn_known'] == 80.0
    assert row['beyond9k_pct'] == 20.0
    assert hits == [('zorba', 'tag')]

def test_concreteness_token_vs_type(families):
    toks = [Tok('hunger', 'hunger', 'NOUN', True)] * 3 + [Tok('ray', 'ray', 'NOUN', True),
            Tok('heft', 'heft', 'VERB', True)]
    row, _ = profile(toks, families, NORMS, {})
    assert row['conc_tok'] == 2.5          # (2+2+2+4)/4
    assert row['conc_type'] == 3.0         # (2+4)/2
    assert row['conc_cov'] == 80.0         # 4 of 5 content tokens matched

def test_concreteness_no_matches_is_nan(families):
    row, _ = profile([Tok('heft', 'heft', 'VERB', True)], families, NORMS, {})
    assert math.isnan(row['conc_tok']) and math.isnan(row['conc_type'])

def test_profile_counts_excluded_tokens_with_letters(families):
    toks = [Tok('ray', 'ray', 'NOUN', True), Tok("n't", 'not', 'PART', False),
            Tok('U.S.', 'U.S.', 'PROPN', False), Tok(',', ',', 'PUNCT', False), Tok('1999', '1999', 'NUM', False)]
    row, _ = profile(toks, families, NORMS, {})
    assert row['n_tokens'] == 1 and row['n_excluded'] == 2
    assert row['excluded_alpha_pct'] == pytest.approx(100 * 2 / 3)

def test_load_families_empty_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match='fetch_resources'):
        load_families(tmp_path)

def test_overrides_utf8_bom(tmp_path):
    p = tmp_path / 'o.csv'; p.write_bytes('type,label\nray,proper\n'.encode('utf-8-sig'))
    assert load_overrides(p) == {'ray': 'proper'}

@pytest.mark.parametrize('body, msg', [
    ('type,label\nray\n', 'line 2'),
    ('type,label\n,proper\n', 'line 2'),
    ('word,label\nray,proper\n', 'type,label'),
    ('type,label\nray,proper\nray,common\n', 'line 3'),
])
def test_overrides_malformed_rows_name_the_line(tmp_path, body, msg):
    p = tmp_path / 'o.csv'; p.write_text(body)
    with pytest.raises(ValueError, match=msg):
        load_overrides(p)
