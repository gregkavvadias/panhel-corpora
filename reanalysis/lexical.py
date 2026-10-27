# Phase 2 lexical profile: BNC/COCA word-family coverage and Brysbaert concreteness per text.
# Resources come from fetch_resources.py; see data/SOURCES.md and the Phase 2 design spec.
import csv
from pathlib import Path
import pandas as pd

BASE = range(1, 31)      # frequency bands, 1k families each
PROPN_LIST = 31          # proper nouns
SUPP = {32, 33, 34, 35}  # marginal words, compounds, abbreviations, accented spellings: counted as known

def load_families(dirpath):
    """Lower-cased form -> list number; a form on several lists keeps the lowest number."""
    index = {}
    for f in Path(dirpath).glob('basewrd*.txt'):
        n = int(f.stem[len('basewrd'):])
        for line in f.read_text(encoding='utf-8').splitlines():
            if line.strip():
                form = line.split()[0].lower()
                index[form] = min(n, index.get(form, n))
    if not index:
        raise FileNotFoundError(f'no basewrd*.txt lists in {dirpath}; run python fetch_resources.py')
    return index

def load_norms(path):
    """Lower-cased single-word lemma -> Brysbaert Conc.M."""
    d = pd.read_excel(path)
    d = d[~d['Word'].astype(str).str.strip().str.contains(' ')]
    return {str(w).strip().lower(): float(c) for w, c in zip(d['Word'], d['Conc.M'])}

def load_overrides(path):
    """Greg's manual proper-noun decisions: lower-cased type -> 'proper' | 'common'."""
    path = Path(path)
    if not path.exists():
        return {}
    out = {}
    with path.open(encoding='utf-8-sig', newline='') as fh:  # -sig: Excel's "CSV UTF-8" adds a BOM
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or not {'type', 'label'} <= set(reader.fieldnames):
            raise ValueError(f'{path}: header must be type,label (got {reader.fieldnames})')
        for line, row in enumerate(reader, start=2):
            t, label = (row['type'] or '').strip().lower(), (row['label'] or '').strip().lower()
            if not t:
                raise ValueError(f'{path} line {line}: empty type')
            if label not in ('proper', 'common'):
                raise ValueError(f'{path} line {line}: label for {t!r} must be proper or common, got {label!r}')
            if out.get(t, label) != label:
                raise ValueError(f'{path} line {line}: {t!r} already labelled {out[t]!r}')
            out[t] = label
    return out

def classify(form, lemma, pos, families, overrides):
    """(category, list_no, reason); category in propn / band / supp / offlist."""
    f, l = form.lower(), lemma.lower()
    ov = overrides.get(f)
    if ov == 'proper':
        return ('propn', None, 'override')
    lst = families.get(f) or families.get(l)
    if lst == PROPN_LIST:
        return ('offlist', None, 'override') if ov == 'common' else ('propn', None, 'list31')
    if lst in BASE:
        return ('band', lst, '')
    if lst in SUPP:
        return ('supp', lst, '')
    if pos == 'PROPN' and ov != 'common':
        return ('propn', None, 'tag')
    return ('offlist', None, '')

CONTENT_POS = {'NOUN', 'VERB', 'ADJ', 'ADV'}

def _pct(num, den):
    return 100 * num / den if den else float('nan')

def profile(tokens, families, norms, overrides):
    """Coverage (percent) and concreteness for one text; also the (form, reason) of every proper-noun token."""
    bands, n_supp, n_propn, n_off, hits, conc, n_content = [], 0, 0, 0, [], [], 0
    n = n_excl = 0
    for t in tokens:
        if not t.is_alpha:
            n_excl += any(c.isalpha() for c in t.text)  # clitics ('s, n't), U.S., words glued to punctuation
            continue
        n += 1
        cat, lst, reason = classify(t.text, t.lemma_, t.pos_, families, overrides)
        if cat == 'propn':
            n_propn += 1; hits.append((t.text.lower(), reason)); continue
        if cat == 'band': bands.append(lst)
        elif cat == 'supp': n_supp += 1
        else: n_off += 1
        if t.pos_ in CONTENT_POS:
            n_content += 1
            lemma = t.lemma_.lower()
            if lemma in norms: conc.append((lemma, norms[lemma]))
    known = n - n_propn
    upto = lambda k: sum(b <= k for b in bands)
    row = dict(n_tokens=n, n_propn=n_propn, n_supp=n_supp, n_offlist=n_off, n_excluded=n_excl,
               excluded_alpha_pct=_pct(n_excl, n + n_excl))
    for k in range(1, 10):
        row[f'cov{k}k'] = _pct(upto(k) + n_supp, known)
    row['cov5k_base_only'] = _pct(upto(5), known)
    row['cov5k_propn_known'] = _pct(upto(5) + n_supp + n_propn, n)
    row.update(propn_pct=_pct(n_propn, n), supp_pct=_pct(n_supp, n), offlist_pct=_pct(n_off, n),
               beyond9k_pct=_pct(len(bands) - upto(9), n))
    types = dict(conc)
    row['conc_tok'] = sum(c for _, c in conc) / len(conc) if conc else float('nan')
    row['conc_type'] = sum(types.values()) / len(types) if types else float('nan')
    row['conc_cov'] = _pct(len(conc), n_content)
    return row, hits

def main():
    import spacy
    from collections import Counter
    from corpus import iter_texts, window, is_exam
    here = Path(__file__).resolve().parent
    families = load_families(here / 'data' / 'bnc_coca')
    norms = load_norms(here / 'data' / 'brysbaert_concreteness.xlsx')
    overrides = load_overrides(here / 'data' / 'propn_overrides.csv')
    nlp = spacy.load('en_core_web_sm')
    rows, counts, reasons = [], {'school': Counter(), 'exam': Counter()}, {}
    for book, text, raw in iter_texts():
        doc = nlp(raw)
        row, hits = profile(doc, families, norms, overrides)
        rows.append(dict(book=book, text=text, version='full', **row))
        grp = 'exam' if is_exam(book) else 'school'
        for form, reason in hits:
            counts[grp][form] += 1; reasons.setdefault(form, reason)
        if not is_exam(book):
            row, _ = profile(nlp(window(doc)), families, norms, overrides)
            rows.append(dict(book=book, text=text, version='first360', **row))
    F = pd.DataFrame(rows)
    F.to_csv(here / 'results' / 'lexical_features.csv', index=False)
    P = pd.DataFrame([dict(type=t, reason=r, n_school=counts['school'][t], n_exam=counts['exam'][t],
                           also_common_word=(r == 'list31' and t in norms)) for t, r in reasons.items()])
    P = P.assign(_n=P.n_school + P.n_exam).sort_values(['_n', 'type'], ascending=[False, True]).drop(columns='_n')
    P.to_csv(here / 'results' / 'propn_types.csv', index=False)
    print(F.groupby(['book', 'version'])[['cov5k', 'conc_tok', 'conc_cov', 'propn_pct']].mean().round(2))

if __name__ == '__main__':
    main()
