import pandas as pd
import pytest
from lexical import classify, load_families, load_norms, load_overrides

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
