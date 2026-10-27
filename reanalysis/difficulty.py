# Phase 3 part 2: open measures of text difficulty (vocabulary, syntax, cohesion, readability).
# Definitions are written in README.md ("Phase 3 part 2: definitions"); see the design spec.
import csv
from pathlib import Path
from lexical import classify

CONTENT_POS = {'NOUN', 'VERB', 'ADJ', 'ADV'}
NAN = float('nan')

# ---- vocabulary ----

def load_glasgow(path):
    """Glasgow Norms (Scott et al., 2019): lower-cased word -> {'imag', 'fam'} means.
    Sense-tagged ('bank (money)') and multiword entries are skipped; the first entry wins."""
    with Path(path).open(encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.reader(fh))
    head = rows[0]
    col = {name: head.index(name) for name in ('IMAG', 'FAM')}  # each scale's M column is under its name
    out = {}
    for r in rows[2:]:
        w = r[0].strip().lower()
        if not w or '(' in w or ' ' in w or w in out:
            continue
        out[w] = {'imag': float(r[col['IMAG']]), 'fam': float(r[col['FAM']])}
    return out

def content_tokens(tokens, families, overrides):
    """Alphabetic NOUN/VERB/ADJ/ADV tokens that lexical.classify does not mark as proper nouns."""
    return [t for t in tokens if t.is_alpha and t.pos_ in CONTENT_POS
            and classify(t.text, t.lemma_, t.pos_, families, overrides)[0] != 'propn']

def norm_mean(tokens, norms, key):
    """(token-weighted mean of norms[lemma][key] over matched tokens, percent of tokens matched)."""
    if not tokens:
        return NAN, NAN
    vals = [norms[t.lemma_.lower()][key] for t in tokens if t.lemma_.lower() in norms]
    return (sum(vals) / len(vals) if vals else NAN), 100 * len(vals) / len(tokens)

def lexdiv(tokens):
    """MTLD and HD-D on lower-cased alphabetic tokens (lexical-diversity package)."""
    from lexical_diversity import lex_div as ld
    words = [t.text.lower() for t in tokens if t.is_alpha]
    return {'mtld': ld.mtld(words), 'hdd': ld.hdd(words)}

# ---- syntax ----

FINITE = {'VBD', 'VBP', 'VBZ', 'MD'}
CLAUSE_DEPS = {'ROOT', 'ccomp', 'advcl', 'relcl', 'csubj', 'acl'}

def is_clause_head(tok):
    """Head of a finite clause (after Lu's L2SCA): a clausal dependency, or a coordinated verb with its own subject,
    whose verb or one of its auxiliaries is finite; an imperative ROOT verb (tag VB) also counts."""
    deps = [c.dep_ for c in tok.children]
    clausal = tok.dep_ in CLAUSE_DEPS or (tok.dep_ == 'conj' and ('nsubj' in deps or 'nsubjpass' in deps))
    if not clausal or tok.pos_ not in ('VERB', 'AUX'):
        return False
    finite = tok.tag_ in FINITE or any(c.dep_ in ('aux', 'auxpass') and c.tag_ in FINITE for c in tok.children)
    imperative = tok.dep_ == 'ROOT' and tok.tag_ == 'VB'
    return finite or imperative

def syntax(doc):
    """Clause, sentence and phrase measures for one parsed text; incidences are per 1,000 alphabetic tokens."""
    alpha = [t for t in doc if t.is_alpha]
    n = len(alpha)
    n_sents = sum(1 for s in doc.sents if any(t.is_alpha for t in s))
    n_clauses = sum(1 for t in doc if is_clause_head(t))
    inc = lambda k: 1000 * k / n if n else NAN
    return dict(
        n_sents=n_sents, n_clauses=n_clauses,
        mlc=n / n_clauses if n_clauses else NAN,
        clauses_per_sent=n_clauses / n_sents if n_sents else NAN,
        mean_sent_len=n / n_sents if n_sents else NAN,
        passive_inc=inc(sum(t.dep_ == 'auxpass' for t in doc)),
        np_inc=inc(sum(1 for _ in doc.noun_chunks)),
        vp_inc=inc(sum(t.pos_ == 'VERB' for t in doc)),
        adjp_inc=inc(sum(t.pos_ == 'ADJ' for t in doc)),
        pp_inc=inc(sum(t.dep_ == 'prep' for t in doc)),
        neg_inc=inc(sum(t.dep_ == 'neg' for t in doc)),
        gerund_inc=inc(sum(t.tag_ == 'VBG' and not any(c.dep_ == 'aux' for c in t.children) for t in doc)),
        inf_inc=inc(sum(t.tag_ == 'TO' and t.head.tag_ == 'VB' for t in doc)))

# ---- cohesion ----

def _pairs(sents, score):
    """Mean of score(a, b) over adjacent sentence pairs, skipping pairs scored None; (mean, percent skipped)."""
    pairs = list(zip(sents, sents[1:]))
    vals = [v for v in (score(a, b) for a, b in pairs) if v is not None]
    skipped = 100 * (len(pairs) - len(vals)) / len(pairs) if pairs else NAN
    return (sum(vals) / len(vals) if vals else NAN), skipped

def cwo_adj(sents, is_content):
    """Content-word overlap of adjacent sentences: content tokens of A and B whose lower-cased lemma occurs in
    both sentences, divided by all content tokens of A and B. Pairs with an empty side are skipped."""
    def score(a, b):
        ca, cb = [t for t in a if is_content(t)], [t for t in b if is_content(t)]
        if not ca or not cb:
            return None
        shared = {t.lemma_.lower() for t in ca} & {t.lemma_.lower() for t in cb}
        return sum(t.lemma_.lower() in shared for t in ca + cb) / (len(ca) + len(cb))
    return _pairs(sents, score)

def semantic_overlap(sents, is_content, vec):
    """Cosine between the mean word vectors of adjacent sentences' content lemmas (vec(lemma) -> array or None)."""
    import numpy as np
    def mean_vec(s):
        vs = [v for v in (vec(t.lemma_.lower()) for t in s if is_content(t)) if v is not None]
        return np.mean(vs, axis=0) if vs else None
    means = [mean_vec(s) for s in sents]
    def score(a, b):
        if a is None or b is None:
            return None
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        return float(a @ b / (na * nb)) if na and nb else None
    return _pairs(means, score)

TAACO_NAMES = {'causal': 'all_causal', 'connective': 'all_connective',
               'connective_ngram': 'all_connective_ngram', 'basic': 'basic_connectives'}

def load_taaco(path):
    """Connective word lists from TAACO's source (string literals split on tabs); the code itself is not run."""
    import re
    src = Path(path).read_text(encoding='utf-8')
    out = {}
    for key, name in TAACO_NAMES.items():
        m = re.search(rf'^\s*{name} = "([^"]*)"\.split\(', src, re.M)
        if not m:
            raise ValueError(f'{name} not found in {path}')
        out[key] = [w for w in m.group(1).replace('\\t', '\t').split('\t') if w]
    return out

def _count(words, items):
    """Occurrences of list items in the word sequence; multiword items first (longest, non-overlapping)."""
    used, n = [False] * len(words), 0
    for item in sorted({tuple(i.split()) for i in items}, key=len, reverse=True):
        k = len(item)
        for i in range(len(words) - k + 1):
            if not any(used[i:i + k]) and tuple(words[i:i + k]) == item:
                used[i:i + k] = [True] * k; n += 1
    return n

def connectives(tokens, lists):
    """All and causal connectives per 1,000 alphabetic tokens (TAACO lists; caveat lists not counted)."""
    words = [t.text.lower() for t in tokens if t.is_alpha]
    if not words:
        return {'conn_inc': NAN, 'causal_inc': NAN}
    conn = _count(words, lists['connective_ngram'] + lists['connective'] + lists['basic'])
    return {'conn_inc': 1000 * conn / len(words), 'causal_inc': 1000 * _count(words, lists['causal']) / len(words)}

# ---- readability (same formulas and syllable counter as features.py) ----

def readability(doc):
    import pyphen
    dic = pyphen.Pyphen(lang='en_US')
    words = [t.text.lower() for t in doc if t.is_alpha]
    n_sents = sum(1 for s in doc.sents if any(t.is_alpha for t in s))
    if not words or not n_sents:
        return {'fre': NAN, 'fkgl': NAN}
    wps = len(words) / n_sents
    spw = sum(max(1, len(dic.positions(w)) + 1) for w in words) / len(words)
    return {'fre': 206.835 - 1.015 * wps - 84.6 * spw, 'fkgl': 0.39 * wps + 11.8 * spw - 15.59}

# ---- corpus run ----

def measures(doc_full, doc_hf, families, overrides, glasgow, lists, vec):
    """All difficulty measures for one text: vocabulary from doc_full, the rest from the heading-free doc_hf."""
    is_content = lambda t: t.is_alpha and t.pos_ in CONTENT_POS and \
        classify(t.text, t.lemma_, t.pos_, families, overrides)[0] != 'propn'
    content = content_tokens(doc_full, families, overrides)
    imag, imag_cov = norm_mean(content, glasgow, 'imag')
    fam, fam_cov = norm_mean(content, glasgow, 'fam')
    sents = [list(s) for s in doc_hf.sents if any(t.is_alpha for t in s)]
    cwo, cwo_skipped = cwo_adj(sents, is_content)
    sem, sem_skipped = semantic_overlap(sents, is_content, vec)
    return dict(imag=imag, imag_cov=imag_cov, fam=fam, fam_cov=fam_cov, **lexdiv(doc_full), **syntax(doc_hf),
                cwo_adj=cwo, cwo_skipped=cwo_skipped, sem_overlap=sem, sem_skipped=sem_skipped,
                **connectives(doc_hf, lists), **readability(doc_hf))

def main():
    import spacy, pandas as pd
    from lexical import load_families, load_overrides
    from corpus import iter_texts, load_headings, remove_headings, window, is_exam
    here = Path(__file__).resolve().parent
    families = load_families(here / 'data' / 'bnc_coca')
    overrides = load_overrides(here / 'data' / 'propn_overrides.csv')
    glasgow = load_glasgow(here / 'data' / 'glasgow_norms.csv')
    lists = load_taaco(here / 'data' / 'taaco' / 'TAACOnoGUI.py')
    nlp, md = spacy.load('en_core_web_sm'), spacy.load('en_core_web_md')
    vec = lambda w: md.vocab[w].vector if md.vocab.has_vector(w) else None
    headings = load_headings()
    rows = []
    for book, text, raw in iter_texts():
        doc = nlp(raw)
        doc_hf = nlp(remove_headings(raw, headings.get((book, text), set())))
        rows.append(dict(book=book, text=text, version='full',
                         **measures(doc, doc_hf, families, overrides, glasgow, lists, vec)))
        if not is_exam(book):
            d = nlp(window(doc_hf))
            rows.append(dict(book=book, text=text, version='first360',
                             **measures(d, d, families, overrides, glasgow, lists, vec)))
    F = pd.DataFrame(rows)
    F.to_csv(here / 'results' / 'difficulty_features.csv', index=False)
    show = ['mlc', 'cwo_adj', 'mean_sent_len', 'imag', 'imag_cov', 'sem_overlap', 'conn_inc', 'fre']
    print(F.assign(group=F.book.map(lambda b: 'exam' if is_exam(b) else 'school'))
           .groupby(['group', 'version'])[show].mean().round(3).T)

if __name__ == '__main__':
    main()
