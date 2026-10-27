import math
from collections import namedtuple
import pytest
from difficulty import load_glasgow, content_tokens, norm_mean

Tok = namedtuple('Tok', 'text lemma_ pos_ is_alpha')

def test_load_glasgow_skips_sense_tags(tmp_path):
    p = tmp_path / 'g.csv'
    p.write_text('Words,Length,AROU,,,VAL,,,DOM,,,CNC,,,IMAG,,,FAM,,,AOA,,,SIZE,,,GEND,,\n'
                 ',,M,SD,N,M,SD,N,M,SD,N,M,SD,N,M,SD,N,M,SD,N,M,SD,N,M,SD,N,M,SD,N\n'
                 'dog,3,1,1,1,1,1,1,1,1,1,1,1,1,6.5,1,1,6.0,1,1,1,1,1,1,1,1,1,1,1\n'
                 'bank (money),4,1,1,1,1,1,1,1,1,1,1,1,1,4.0,1,1,5.0,1,1,1,1,1,1,1,1,1,1,1\n')
    assert load_glasgow(p) == {'dog': {'imag': 6.5, 'fam': 6.0}}

def test_content_tokens_exclude_propn_and_function_words():
    toks = [Tok('Dogs', 'dog', 'NOUN', True), Tok('the', 'the', 'DET', True), Tok('Zorba', 'Zorba', 'PROPN', True)]
    assert [t.text for t in content_tokens(toks, {'dog': 1}, {})] == ['Dogs']

def test_norm_mean_and_coverage():
    toks = [Tok('dog', 'dog', 'NOUN', True)] * 2 + [Tok('idea', 'idea', 'NOUN', True)]
    assert norm_mean(toks, {'dog': {'imag': 6.0}}, 'imag') == (6.0, pytest.approx(200 / 3))

def test_norm_mean_empty_and_unmatched():
    assert all(math.isnan(v) for v in norm_mean([], {}, 'imag'))
    m, cov = norm_mean([Tok('idea', 'idea', 'NOUN', True)], {}, 'imag')
    assert math.isnan(m) and cov == 0.0
