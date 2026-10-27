# Phase 3 Open Measures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compute open, reproducible text-difficulty measures (vocabulary, syntax, cohesion, readability) on 27 coursebook vs 26 exam texts, test four pre-specified primaries in one BH family, and validate the new measures against the thesis Coh-Metrix values.

**Architecture:** `corpus.py` gains text exclusion, heading-line removal and `**` stripping. `difficulty.py` holds pure, unit-tested measure functions plus a `main()` writing `results/difficulty_features.csv`. `stats6.py` runs the primary family, the robustness checks, the descriptive rows and the validation. External resources (Glasgow Norms, TAACO lists, `en_core_web_md` vectors) are fetched at run time.

**Tech Stack:** Python 3.13, spaCy 3.8 (`en_core_web_sm` 3.8.0 for parsing; `en_core_web_md` 3.8.0 for vectors only), pandas, scipy, statsmodels, lexical-diversity, pytest.

**Spec:** `docs/superpowers/specs/2026-10-27-phase3-open-measures-design.md`

## Global Constraints

- Run from `reanalysis/`; `pathlib`; outputs in `results/`; resource URLs, versions and citations in `data/SOURCES.md`.
- Corpus: `data/excluded_texts.csv` (`book,text,reason`) lists `English 2,unit-4-1,formatting exercise ("Format the text"; spaces and punctuation removed), not a reading passage — Greg 2026-10-27`. `corpus.iter_texts` skips listed texts → 27 coursebook + 26 exam.
- `**` is removed from every text in `corpus.iter_texts`.
- Heading lines: `data/heading_lines.csv` (`book,text,line`), exact line text, for English 1 unit-5-2 ("Farm Animals Need Our Help", "Factory Farms", "Chickens"); English 2 unit-3-3 ("Sandro Botticelli"), unit-3-4 ("Raphael"), unit-3-5 ("Andrea del Verrocchio"), unit-6-1 ("I Have A Dream", "Nelson Mandela"), unit-6-2 ("I am prepared to die", "Nelson Mandela"), unit-8-2 ("Plot", "Characters", "Themes in the Story" — after `**` removal), unit-8-3 ("100 Percent Pure German Sweat"), unit-8-5 ("The Memorial"), unit-8-6 ("Victims"). Copy the exact lines from the files.
- **Which text each measure sees** (ruling on spec §6, which names only some measures): vocabulary measures (Glasgow, MTLD, HD-D) use the full text; **all syntax, cohesion and readability measures** use the heading-free text, because headings parse as sentences and as noun phrases.
- Content tokens: alphabetic, `pos_` in {NOUN, VERB, ADJ, ADV}, and `lexical.classify(...)[0] != 'propn'` with the Phase 2 families and `propn_overrides.csv`.
- Primary family (BH on Welch p, full texts): `cov5k`, `conc_tok`, `mlc`, `cwo_adj`. TOST on `cov5k` (±2.0) outside the family. Seed 1, B = 5000. Direction exam − school.
- **Definition freeze:** Tasks 2–4 define and test every measure on hand-made sentences, and write the README definitions, before Task 5 runs anything on the corpus. After the freeze, a rule changes only to fix a bug (code ≠ written definition); each such change is listed in the README with before/after primary values.
- Resources:
  - Glasgow Norms: `https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-018-1099-3/MediaObjects/13428_2018_1099_MOESM2_ESM.csv` (CC BY 4.0; two header rows; columns `Words`, then `M,SD,N` triples for AROU, VAL, DOM, CNC, IMAG, FAM, AOA, SIZE, GEND). Saved to `data/glasgow_norms.csv` (gitignored).
  - TAACO lists: `https://raw.githubusercontent.com/LCR-ADS-Lab/TAACO/ae5340c5385be849095f840004d70509d4732749/TAACOnoGUI.py` (no licence stated: download only, never commit), saved to `data/taaco/TAACOnoGUI.py` (gitignored); parse the tab-separated string literals `all_connective`, `all_connective_ngram`, `basic_connectives`, `all_causal`.
  - Vectors: `python -m spacy download en_core_web_md` (3.8.0), used only via `nlp_md.vocab[word].vector`.

## Review Focus

1. A sentence with no finite clause (dialogue "Yes, Papa.", a list item) must count as a sentence but add no clause, and a text with zero clauses gives NaN `mlc`, not a crash or ∞. → Task 3 `test_mlc_no_clause_sentence_and_nan`.
2. A heading line that also occurs elsewhere in the body (e.g. "Nelson Mandela" as a sentence) — removal must drop only whole lines equal to the listed text. → Task 1 `test_remove_headings_whole_lines_only`.
3. Glasgow entries with sense tags ("bank (money)") or duplicates must not crash loading; tagged entries are skipped, the first untagged entry wins. → Task 2 `test_load_glasgow_skips_sense_tags`.
4. Multiword connectives ("in addition", "due to") must be counted once as phrases and not double-counted via their single words. → Task 4 `test_connectives_ngrams_counted_once`.
5. A content word with no vector in `en_core_web_md` must be skipped, and a pair where either sentence has no vectored content word is skipped and counted, not scored 0. → Task 4 `test_semantic_overlap_skips_unvectored`.

---

### Task 1: Corpus exclusion, `**` stripping and heading removal

**Files:**
- Create: `reanalysis/data/excluded_texts.csv`, `reanalysis/data/heading_lines.csv`
- Modify: `reanalysis/corpus.py`, `reanalysis/tests/test_helpers.py`

**Interfaces:**
- Produces:
  - `corpus.load_exclusions(path: Path = DATA/'excluded_texts.csv') -> set[tuple[str, str]]`
  - `corpus.iter_texts(base=TEXTS_DIR, exclude=None)` — `exclude` defaults to `load_exclusions()`; skips `(book, text)` pairs in it; yields texts with `**` removed.
  - `corpus.load_headings(path: Path = DATA/'heading_lines.csv') -> dict[tuple[str, str], set[str]]`
  - `corpus.remove_headings(raw: str, headings: set[str]) -> str` — drops lines whose stripped text equals a listed heading; keeps everything else, including line breaks.

- [ ] **Step 1: Write the failing tests**

```python
def test_iter_texts_counts():                     # replaces the existing test
    books = [b for b, _, _ in iter_texts()]
    assert books.count('English 1') == 10
    assert books.count('English 2') == 17
    assert books.count('Panhellenics') == 26

def test_unit_4_1_excluded_and_stars_stripped():
    t = {(b, x): r for b, x, r in iter_texts()}
    assert ('English 2', 'unit-4-1') not in t and '**' not in t[('English 2', 'unit-8-2')]

def test_remove_headings_whole_lines_only():
    raw = 'Nelson Mandela\r\n\r\nI met Nelson Mandela.\r\nNelson Mandela\r\nEnd.'
    assert remove_headings(raw, {'Nelson Mandela'}) == '\r\n\r\nI met Nelson Mandela.\r\nEnd.'

def test_heading_lines_all_present_in_files():
    t = {(b, x): r for b, x, r in iter_texts()}
    for key, lines in load_headings().items():
        file_lines = {l.strip() for l in t[key].splitlines()}
        assert lines <= file_lines, key
```

- [ ] **Step 2: Run** `python -m pytest tests/test_helpers.py -q` — Expected: FAIL (`ImportError: remove_headings`).
- [ ] **Step 3: Write the two CSVs** (Global Constraints) **and implement** the four functions.
- [ ] **Step 4: Run** the full suite — Expected: all pass.
- [ ] **Step 5: Commit** — "Exclude unit-4-1, strip markdown emphasis, list heading lines".

---

### Task 2: Vocabulary measures

**Files:**
- Create: `reanalysis/difficulty.py`, `reanalysis/tests/test_difficulty.py`
- Modify: `reanalysis/fetch_resources.py` (add Glasgow, TAACO, `en_core_web_md` check), `.gitignore` (`reanalysis/data/glasgow_norms.csv`, `reanalysis/data/taaco/`), `reanalysis/data/SOURCES.md`

**Interfaces:**
- Produces (in `difficulty.py`):
  - `load_glasgow(path: Path) -> dict[str, dict[str, float]]` — lower-cased word → `{'imag': IMAG M, 'fam': FAM M}`; entries containing `(` or a space are skipped; first occurrence wins.
  - `content_tokens(tokens, families: dict, overrides: dict) -> list` — tokens per Global Constraints.
  - `norm_mean(tokens, norms: dict, key: str) -> tuple[float, float]` — `(token-weighted mean of norms[lemma.lower()][key] over matched content tokens, percent of content tokens matched)`; `(nan, nan)` if no content tokens, `(nan, 0.0)` if none matched.
  - `lexdiv(tokens) -> dict` — `{'mtld': ..., 'hdd': ...}` from `lexical_diversity.lex_div` on lower-cased alphabetic tokens (`ld.mtld`, `ld.hdd`).

- [ ] **Step 1: Write the failing tests** (namedtuple `Tok(text, lemma_, pos_, is_alpha)`; small `families` dict, e.g. `{'dog': 1, 'run': 1, 'idea': 1}`)

```python
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
```

- [ ] **Step 2: Run** — Expected: FAIL (`ModuleNotFoundError: difficulty`).
- [ ] **Step 3: Implement**; extend `fetch_resources.py` to download Glasgow and TAACO (same urllib + User-Agent helper) and to print the installed `en_core_web_md` version (instruct to run `python -m spacy download en_core_web_md` if absent). Run `python -m spacy download en_core_web_md`, then `python fetch_resources.py`. Add both resources and the model to `SOURCES.md`.
- [ ] **Step 4: Run tests** — Expected: pass.
- [ ] **Step 5: Commit** — "Add vocabulary difficulty measures and resources".

---

### Task 3: Syntax measures

**Files:** Modify `reanalysis/difficulty.py`, `reanalysis/tests/test_difficulty.py`

**Interfaces:**
- Produces:
  - `is_clause_head(tok) -> bool` — True if `tok.dep_` in {`ROOT`, `ccomp`, `advcl`, `relcl`, `csubj`, `acl`} **or** (`tok.dep_ == 'conj'` and `tok` has a child with dep `nsubj`/`nsubjpass`), **and** the head is finite: `tok.tag_` in {VBD, VBP, VBZ, MD}, or `tok` has a child with dep `aux`/`auxpass` whose tag is in {VBD, VBP, VBZ, MD}. (A `ROOT` with `pos_` VERB/AUX and tag VB, i.e. an imperative, also counts.)
  - `syntax(doc) -> dict` with keys (per 1,000 alphabetic tokens unless stated): `n_sents` (sentences with ≥ 1 alphabetic token), `n_clauses`, `mlc` (alpha tokens ÷ clauses; NaN if 0 clauses), `clauses_per_sent`, `mean_sent_len`, `passive_inc` (`auxpass` count), `np_inc` (`doc.noun_chunks`), `vp_inc` (`pos_ == 'VERB'`), `adjp_inc` (`pos_ == 'ADJ'`), `pp_inc` (`dep_ == 'prep'`), `neg_inc` (`dep_ == 'neg'`), `gerund_inc` (`tag_ == 'VBG'` and no `aux` child), `inf_inc` (`tag_ == 'TO'` whose head has `tag_ == 'VB'`).
- Tests use the real `en_core_web_sm` (module-level fixture `nlp`).

- [ ] **Step 1: Write the failing tests**

```python
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
```

(If a parse of these exact sentences by `en_core_web_sm` 3.8.0 contradicts an expectation, check the parse first: the test may need a sentence the model parses as intended. Record any such change in the ledger; never loosen the rule to fit.)

- [ ] **Step 2: Run** — Expected: FAIL (`ImportError: syntax`).
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run tests** — Expected: pass.
- [ ] **Step 5: Commit** — "Add syntax difficulty measures".

---

### Task 4: Cohesion and readability measures; definition freeze

**Files:** Modify `reanalysis/difficulty.py`, `reanalysis/tests/test_difficulty.py`, `reanalysis/README.md` (new "Phase 3 part 2: definitions" section)

**Interfaces:**
- Produces:
  - `cwo_adj(sents: list[list], is_content) -> tuple[float, float]` — `sents` = list of token lists; `is_content(tok) -> bool`. Returns `(mean pair score, percent of adjacent pairs skipped)`. Pair score per spec §6: content tokens of A and B whose lower-cased lemma occurs in both, ÷ total content tokens of A and B. Skip a pair if either sentence has no content token. NaN if no pair scored.
  - `semantic_overlap(sents, is_content, vec) -> tuple[float, float]` — `vec(lemma) -> numpy array | None`; per sentence, mean vector of vectored content lemmas; pair score = cosine; skip pairs lacking a vector on either side; returns `(mean, percent skipped)`.
  - `load_taaco(path: Path) -> dict[str, list[str]]` — keys `connective`, `connective_ngram`, `basic`, `causal`, parsed from the `name = "a\tb\t…".split("\t")` literals.
  - `connectives(tokens, lists: dict) -> dict` — `{'conn_inc', 'causal_inc'}` per 1,000 alphabetic tokens. Match on lower-cased token sequence: multiword items first (longest match, non-overlapping; matched tokens are consumed), then single words in `connective ∪ basic` (for `conn_inc`) and single-word `causal` items. The TAACO caveat lists (`since`, `after`, `before`, …) are not counted. *(Documented simplification.)*
  - `readability(doc) -> dict` — `{'fre', 'fkgl'}` with the `features.py` formulas and `pyphen` syllable counter.
- README definitions section: one line per measure in `difficulty_features.csv` (exact rule, unit, text version used, source). This is the freeze.

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run** — Expected: FAIL (`ImportError`).
- [ ] **Step 3: Implement**; write the README definitions section.
- [ ] **Step 4: Run tests** — Expected: pass. Also check the real TAACO file loads: `python -c "from difficulty import load_taaco; d=load_taaco('data/taaco/TAACOnoGUI.py'); print({k: len(v) for k, v in d.items()})"` — Expected: four non-empty lists.
- [ ] **Step 5: Commit** — "Add cohesion and readability measures; freeze definitions". **This commit is the freeze.**

---

### Task 5: Compute features on the corpus

**Files:** Modify `reanalysis/difficulty.py` (add `main()`); output `reanalysis/results/difficulty_features.csv`

**Interfaces:**
- Consumes: Tasks 1–4; `lexical.load_families`, `load_overrides`, `classify`; `corpus.iter_texts`, `load_headings`, `remove_headings`, `window`, `is_exam`.
- Produces: `results/difficulty_features.csv` — columns `book,text,version` + `imag, imag_cov, fam, fam_cov, mtld, hdd` (full text) + `syntax()` keys + `cwo_adj, cwo_skipped, sem_overlap, sem_skipped, conn_inc, causal_inc, fre, fkgl` (heading-free text). Versions: `full` for all 53 texts; `first360` for the 27 coursebook texts (`window()` of the heading-free text, all measures from that window). **80 rows.**

- [ ] **Step 1: Implement `main()`.**
- [ ] **Step 2: Run** `python difficulty.py` — Expected: 80 rows; prints group means of the primary and a few descriptive measures.
- [ ] **Step 3: Sanity checks** (record in commit message): no NaN in `mlc`, `cwo_adj` for full texts; `imag_cov`, `fam_cov` ranges (report; Glasgow is small, ~5.5k words, so coverage will be well below the Brysbaert 95%); `cwo_skipped` range.
- [ ] **Step 4: Rerun** `python lexical.py` (picks up the exclusion and `**` stripping) — Expected: `lexical_features.csv` has 80 rows (53 + 27).
- [ ] **Step 5: Commit** — "Compute open difficulty measures on 27 + 26 texts".

---

### Task 6: Comparisons, robustness and validation

**Files:**
- Create: `reanalysis/stats6.py`, `reanalysis/tests/test_stats6.py`
- Outputs: `results/difficulty_comparisons.csv`, `results/difficulty_validation.csv`

**Interfaces:**
- Consumes: `stats5.compare`, `stats5.tost_welch`, `stats5.exam_subsets`, `stats5.MARGIN`; both feature CSVs.
- Produces:
  - `PRIMARY = ['cov5k', 'conc_tok', 'mlc', 'cwo_adj']`
  - `VALIDATION = {'conc_tok': 'WRDCNCc', 'imag': 'WRDIMGc', 'hdd': 'LDVOCD', 'mean_sent_len': 'DESSL', 'passive_inc': 'DRPVAL', 'np_inc': 'DRNP', 'vp_inc': 'DRVP', 'adjp_inc': 'DRAP', 'pp_inc': 'DRPP', 'neg_inc': 'DRNEG', 'gerund_inc': 'DRGERUND', 'inf_inc': 'DRINF', 'cwo_adj': 'CRFSOa', 'conn_inc': 'CNCAll', 'causal_inc': 'SMCAUSvp', 'sem_overlap': 'LSASSp', 'fre': 'RDFRE', 'fkgl': 'RDFKGL'}`
  - `spearman_ci(x, y) -> dict` — `rho, lo, hi, p, n` (Fisher z CI, `se = 1/sqrt(n-3)`; NaN CI if n < 4).
  - `comparisons(F: DataFrame) -> DataFrame` — rows with `measure, dimension, role, version, subset` + `compare` keys; `role` ∈ {primary, robustness, descriptive}:
    - primary: the four, full texts, subset `all`; `p_welch_BH` over exactly these four; `cov5k` row also carries the TOST columns.
    - robustness: `mlc`, `cwo_adj` on `first360` and on subsets `june`, `original13` (full).
    - descriptive: every other measure (full, `all`), with `p_welch`/`p_mw` set to NaN.
  - `validation(F: DataFrame, cm: DataFrame) -> DataFrame` — per `VALIDATION` pair: `spearman_ci` pooled (40 texts) and within `school` (27) and `exam` (13); columns `measure, cohmetrix, group, rho, lo, hi, p, n`.
  - `main()` merges `lexical_features.csv` and `difficulty_features.csv` on `book,text,version`, writes both outputs, prints them.

- [ ] **Step 1: Write the failing tests**

```python
def test_spearman_ci_perfect_and_small_n():
    r = spearman_ci([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
    assert r['rho'] == pytest.approx(1.0) and r['n'] == 5
    assert math.isnan(spearman_ci([1, 2, 3], [1, 2, 3])['lo'])

def test_primary_family_has_four_and_bh_only_there(F_fixture):   # synthetic F: 6 school + 6 exam rows, all columns
    C = comparisons(F_fixture)
    prim = C[C.role == 'primary']
    assert sorted(prim.measure) == sorted(PRIMARY) and prim.p_welch_BH.notna().all()
    assert C[C.role != 'primary'].p_welch_BH.isna().all()
    assert C[C.role == 'descriptive'].p_welch.isna().all()

def test_validation_groups(F_fixture, cm_fixture):
    V = validation(F_fixture, cm_fixture)
    assert set(V.group) == {'pooled', 'school', 'exam'}
```

(Fixtures: build `F` with `book` in {English 1, Panhellenics}, `text` ids `unit-i` / `20yy-06`, `version='full'`, and random values for every measure column used; `cm` with matching `book,text` and the Coh-Metrix columns.)

- [ ] **Step 2: Run** — Expected: FAIL (`ModuleNotFoundError: stats6`).
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run tests** — Expected: pass.
- [ ] **Step 5: Run** `python stats6.py` — Expected: both CSVs written; 4 primary rows with BH p; validation table with 18 measures × 3 groups.
- [ ] **Step 6: Commit** — "Add difficulty comparisons and Coh-Metrix validation".

---

### Task 7: README and handoff

**Files:** Modify `reanalysis/README.md`, `HANDOFF.md` (status line)

- [ ] **Step 1:** Data/scripts sections: `excluded_texts.csv`, `heading_lines.csv`, Glasgow, TAACO, `en_core_web_md`; `difficulty.py`, `stats6.py`.
- [ ] **Step 2:** New section "Phase 3 part 2: the difficulty table", built only from the result CSVs:
  - the difficulty table by dimension (school mean, exam mean, g [95% CI], p and BH p for the four primaries; descriptives with g [CI] only);
  - the TOST on `cov5k` (now 27 vs 26);
  - robustness rows for `mlc` and `cwo_adj`;
  - the validation table (pooled and within-group ρ [CI]), with a sentence on any measure with pooled ρ < .5;
  - dropped indices with reasons (spec §2);
  - the corpus change: unit-4-1 excluded (27 coursebook texts); published 28-text numbers remain in git history (`ee0280e` for Phase 2, Phase 3 part 1 PR); Phase 1 Coh-Metrix analyses unchanged;
  - post-freeze changes (or "none");
  - an updated scope paragraph for the paper.
- [ ] **Step 3: Verify** every number against the CSVs.
- [ ] **Step 4: Commit** — "Document the open difficulty measures".
