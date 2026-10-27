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
