import math
from collections import namedtuple
import pytest
from difficulty import (load_glasgow, content_tokens, norm_mean, syntax, cwo_adj, semantic_overlap, load_taaco,
                        connectives, readability)

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

@pytest.fixture(scope='module')
def nlp():
    import spacy
    return spacy.load('en_core_web_sm')

def test_clause_count_simple_and_subordinate(nlp):
    s = syntax(nlp('The dog barked because the cat ran. She left.'))
    assert s['n_sents'] == 2 and s['n_clauses'] == 3 and s['mlc'] == pytest.approx(9 / 3)

def test_relative_clause_and_coordinated_clause(nlp):
    assert syntax(nlp('I saw the man who called, and she waved.'))['n_clauses'] == 3

def test_nonfinite_is_not_a_clause(nlp):
    assert syntax(nlp('He wanted to leave early.'))['n_clauses'] == 1

def test_mlc_no_clause_sentence_and_nan(nlp):
    s = syntax(nlp('Yes, Papa. The end.'))
    assert s['n_sents'] == 2 and s['n_clauses'] == 0 and math.isnan(s['mlc'])

def test_passive_and_negation_incidence(nlp):
    s = syntax(nlp('The letter was not written by him.'))
    assert s['passive_inc'] == pytest.approx(1000 / 7) and s['neg_inc'] == pytest.approx(1000 / 7)

def test_cwo_adj_formula():
    A = [Tok('dogs', 'dog', 'NOUN', True), Tok('run', 'run', 'VERB', True)]
    B = [Tok('dog', 'dog', 'NOUN', True), Tok('sleeps', 'sleep', 'VERB', True), Tok('well', 'well', 'ADV', True)]
    C = [Tok('Yes', 'yes', 'INTJ', True)]
    score, skipped = cwo_adj([A, B, C], lambda t: t.pos_ in {'NOUN', 'VERB', 'ADV'})
    assert score == pytest.approx(2 / 5) and skipped == 50.0

def test_semantic_overlap_skips_unvectored():
    import numpy as np
    vecs = {'dog': np.array([1.0, 0]), 'cat': np.array([1.0, 0])}
    A, B, C = [Tok('dog', 'dog', 'NOUN', True)], [Tok('cat', 'cat', 'NOUN', True)], [Tok('zqx', 'zqx', 'NOUN', True)]
    assert semantic_overlap([A, B, C], lambda t: True, vecs.get) == (pytest.approx(1.0), 50.0)

def test_connectives_ngrams_counted_once():
    lists = {'connective': ['in', 'addition', 'however'], 'connective_ngram': ['in addition'], 'basic': ['and'],
             'causal': ['because', 'due to']}
    toks = [Tok(w, w, 'X', True) for w in 'in addition he left and however due to rain because'.split()]
    r = connectives(toks, lists)
    assert r['conn_inc'] == pytest.approx(1000 * 3 / 10)      # in addition, and, however
    assert r['causal_inc'] == pytest.approx(1000 * 2 / 10)    # due to, because

def test_load_taaco_parses_literals(tmp_path):
    p = tmp_path / 't.py'
    p.write_text('\t\tall_causal = "because\\tdue to".split("\\t")\n\t\tall_connective = "and\\tbut".split("\\t")\n'
                 '\t\tall_connective_ngram = "in fact".split("\\t")\n\t\tbasic_connectives = "and\\tor".split("\\t")\n')
    assert load_taaco(p) == {'causal': ['because', 'due to'], 'connective': ['and', 'but'],
                             'connective_ngram': ['in fact'], 'basic': ['and', 'or']}

def test_lexdiv_returns_mtld_and_hdd(nlp):
    from difficulty import lexdiv
    r = lexdiv(nlp('The cat sat on the mat and the dog sat on the log near the cat and the hat. ' * 3))
    assert set(r) == {'mtld', 'hdd'} and r['mtld'] > 0 and 0 < r['hdd'] <= 1

def test_readability_matches_features_formula(nlp):
    r = readability(nlp('The cat sat. It was happy.'))
    assert r['fre'] == pytest.approx(206.835 - 1.015 * 3 - 84.6 * (7 / 6), abs=1e-6)
