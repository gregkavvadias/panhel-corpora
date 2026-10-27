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
