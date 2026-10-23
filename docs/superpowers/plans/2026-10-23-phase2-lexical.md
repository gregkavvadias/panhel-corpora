# Phase 2 Lexical Measures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add BNC/COCA word-family coverage (bands 1k–9k) and Brysbaert concreteness to the reanalysis, compare exam vs coursebook texts with an equivalence test on 5k coverage (±2 points) and a difference test on concreteness.

**Architecture:** `fetch_resources.py` downloads the two external resources into a gitignored `data/` area. `lexical.py` profiles each text (one row per text × version) and writes per-type proper-noun records for Greg's manual review. `stats5.py` runs the pre-specified comparisons. Shared helpers live in `corpus.py` (text loading, length-matching window) and `effects.py` (Hedges' g, bootstrap CI). Phase 1 scripts are not modified.

**Tech Stack:** Python 3.13, spaCy `en_core_web_sm`, pandas, numpy, scipy, statsmodels, openpyxl, pytest.

**Spec:** `docs/superpowers/specs/2026-10-23-phase2-lexical-design.md`

## Global Constraints

- All scripts run from `reanalysis/` with paths relative to it; outputs go to `reanalysis/results/`.
- Use `pathlib` for all paths (Windows host; `f.split('/')` is forbidden).
- Downloaded resources are **not committed**: `reanalysis/data/bnc_coca/` and `reanalysis/data/brysbaert_concreteness.xlsx` are gitignored. `reanalysis/data/propn_overrides.csv` **is** committed.
- Word-family lists: BNC/COCA basewords **v1.3.0**, `https://www.laurenceanthony.net/software/wordfamilyfinder/downloads/basewords_130.zip` — files `basewrd1.txt`…`basewrd35.txt`, UTF-8, CRLF; unindented line = headword + frequency, tab-indented line = family member + frequency.
  - Lists 1–30: frequency bands (1k each). List 31: proper nouns. List 32: marginal words. List 33: transparent compounds. List 34: abbreviations. List 35: accented spellings.
  - Supplementary lists counted as known = {32, 33, 34, 35}. (List 35 is treated as supplementary: Claude's call, recorded in README.)
- Concreteness norms: Brysbaert, Warriner & Kuperman (2014), `https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-013-0403-5/MediaObjects/13428_2013_403_MOESM1_ESM.xlsx`, columns `Word`, `Conc.M` (1–5 scale). The old crr.ugent.be URL returns 404.
- Coverage values are **percentages (0–100)**. Equivalence margin = **±2.0 percentage points**; primary band = **5k**; primary text version = **full**.
- Coverage denominator excludes proper nouns; numerator at level K = tokens in base lists 1..K + supplementary-list tokens. Tokens in lists 10–30 or off-list stay in the denominator.
- Token universe = spaCy tokens with `is_alpha` (same as `features.py`); contractions like `n't`/`'s` are therefore excluded.
- Content words for concreteness: `pos_` in {NOUN, VERB, ADJ, ADV}, not classified as proper noun; matched by lower-cased lemma to the norms; multiword norm entries ignored.
- BH correction on **Welch** p-values over exactly two tests: `cov5k` and `conc_tok`, full texts. Everything else is labelled `robustness` and left uncorrected.
- Group difference direction everywhere: **exam − school**.
- Random seed for bootstraps: 1, B = 5000 (as Phase 1).

## Review Focus

1. Sentence-initial or headline-capitalised common words that the small spaCy model tags `PROPN` ("Hungry people…") must be classified by the band list, not dropped as proper nouns. → Task 3 test `test_propn_tag_on_band_list_is_band`.
2. A form missing from the lists whose lemma is present ("hungrier" via lemma "hungry", irregular "went" via "go") must be found via the lemma fallback. → Task 3 test `test_lemma_fallback`.
3. All-caps abbreviations and accented words in the texts ("NASA", "café") must match lists 34/35 case-insensitively. → Task 3 test `test_case_and_accents`.
4. A text with no content word found in the norms must give NaN concreteness, not crash or 0. → Task 4 test `test_concreteness_no_matches_is_nan`.
5. A malformed overrides file (value other than `proper`/`common`) must fail loudly naming the bad row; a missing file must behave as no overrides. → Task 3 tests `test_overrides_missing_file`, `test_overrides_bad_value`.

---

### Task 1: Environment and resource download

**Files:**
- Modify: `reanalysis/requirements.txt` (add `openpyxl`, `pytest`)
- Create: `.gitignore` (repo root)
- Create: `reanalysis/fetch_resources.py`
- Create: `reanalysis/data/SOURCES.md`

**Interfaces:**
- Produces: `reanalysis/data/bnc_coca/basewrd{1..35}.txt`, `reanalysis/data/brysbaert_concreteness.xlsx`.

- [ ] **Step 1: Install environment**

Run (from `reanalysis/`): `pip install -r requirements.txt openpyxl pytest && python -m spacy download en_core_web_sm`
Expected: `python -c "import spacy,openpyxl,pytest; spacy.load('en_core_web_sm')"` exits 0. Then add `openpyxl` and `pytest` to `requirements.txt`.

- [ ] **Step 2: Add `.gitignore`**

```
reanalysis/data/bnc_coca/
reanalysis/data/brysbaert_concreteness.xlsx
__pycache__/
.pytest_cache/
```

- [ ] **Step 3: Implement `fetch_resources.py`**

`main() -> None`: downloads the two URLs from Global Constraints with `urllib.request` (not curl — Windows schannel revocation checks fail on crr/springer hosts), extracts the zip into `data/bnc_coca/` (flat, files directly inside), saves the xlsx to `data/brysbaert_concreteness.xlsx`. Skips a resource that already exists unless `--force`. After download, asserts 35 `basewrd*.txt` files exist and the xlsx has columns `Word` and `Conc.M`, then prints the counts.

- [ ] **Step 4: Run it**

Run: `python fetch_resources.py`
Expected: prints 35 list files and ≈39,950 norm rows; `git status` shows neither resource as untracked.

- [ ] **Step 5: Write `data/SOURCES.md`**

One entry per resource: URL, version (basewords 1.3.0; Brysbaert supplementary S1), download date, full citation (Nation, I. S. P. (2017). *The BNC/COCA Level 6 word family lists* (Version 1.0.0) [Data file], plus Anthony's basewords v1.3.0 distribution; Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. *Behavior Research Methods, 46*(3), 904–911), the list-number→category mapping from Global Constraints, and the `spacy`/`en_core_web_sm` versions installed in Step 1.

- [ ] **Step 6: Commit**

```bash
git add .gitignore reanalysis/requirements.txt reanalysis/fetch_resources.py reanalysis/data/SOURCES.md
git commit -m "Add resource fetcher for BNC/COCA lists and concreteness norms"
```

---

### Task 2: Shared helpers (`corpus.py`, `effects.py`)

**Files:**
- Create: `reanalysis/corpus.py`, `reanalysis/effects.py`
- Create: `reanalysis/conftest.py` (empty; makes pytest put `reanalysis/` on `sys.path` so tests can import the top-level modules)
- Test: `reanalysis/tests/test_helpers.py`

**Interfaces:**
- Produces:
  - `corpus.TEXTS_DIR: Path` (= `Path(__file__).resolve().parent.parent / 'Texts'`)
  - `corpus.iter_texts(base: Path = TEXTS_DIR) -> Iterator[tuple[str, str, str]]` — yields `(book, text_id, raw_text)` sorted by book then file name; `book` is the folder name, `text_id` the stem; read with `encoding='utf-8', errors='replace'`.
  - `corpus.window(doc, n: int = 360) -> str` — identical behaviour to `features.window` (whole sentences until ≥ n alpha tokens).
  - `corpus.is_exam(book: str) -> bool` (`book == 'Panhellenics'`).
  - `effects.hedges(a, b) -> float` — (mean b − mean a)/pooled SD × (1 − 3/(4(na+nb)−9)), as `stats1.hedges`.
  - `effects.boot_ci(a, b, B: int = 5000, seed: int = 1) -> tuple[float, float]` — 2.5/97.5 percentiles of bootstrapped `hedges`.

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np
from corpus import iter_texts, is_exam
from effects import hedges, boot_ci

def test_iter_texts_counts():
    books = [b for b, _, _ in iter_texts()]
    assert books.count('English 1') == 10
    assert books.count('English 2') == 18
    assert books.count('Panhellenics') == 13

def test_is_exam():
    assert is_exam('Panhellenics') and not is_exam('English 1')

def test_hedges_known_value():
    assert np.isclose(hedges(np.array([1., 2, 3]), np.array([2., 3, 4])), 0.8)

def test_boot_ci_brackets_g_and_is_seeded():
    a, b = np.arange(10.), np.arange(10.) + 3
    lo, hi = boot_ci(a, b, B=500)
    assert lo < hedges(a, b) < hi
    assert (lo, hi) == boot_ci(a, b, B=500)
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/test_helpers.py -v` — Expected: FAIL, `ModuleNotFoundError: corpus`.

- [ ] **Step 3: Implement both modules** to the signatures above (`boot_ci` uses its own `np.random.default_rng(seed)`).

- [ ] **Step 4: Run tests** — `pytest tests/test_helpers.py -v` — Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add reanalysis/corpus.py reanalysis/effects.py reanalysis/conftest.py reanalysis/tests/test_helpers.py
git commit -m "Add shared corpus and effect-size helpers"
```

---

### Task 3: Resource loaders and token classification

**Files:**
- Create: `reanalysis/lexical.py`
- Test: `reanalysis/tests/test_lexical.py`

**Interfaces:**
- Produces (in `lexical.py`):
  - constants `BASE = range(1, 31)`, `PROPN_LIST = 31`, `SUPP = {32, 33, 34, 35}`
  - `load_families(dirpath: Path) -> dict[str, int]` — lower-cased form → list number; a form on several lists maps to the **lowest** number (so base lists beat supplementary/proper-noun lists).
  - `load_norms(path: Path) -> dict[str, float]` — lower-cased `Word` → `Conc.M`, single-word entries only.
  - `load_overrides(path: Path) -> dict[str, str]` — CSV columns `type,label`; lower-cased type → `'proper'|'common'`; missing file → `{}`; any other label → `ValueError` whose message contains the offending type.
  - `classify(form: str, lemma: str, pos: str, families: dict, overrides: dict) -> tuple[str, int | None, str]` — returns `(category, list_no, reason)`, category ∈ {`'propn'`, `'band'`, `'supp'`, `'offlist'`}.

Classification algorithm (decides the spec's proper-noun rule; implement as written):

```
f, l = form.lower(), lemma.lower()
ov = overrides.get(f)
if ov == 'proper': return ('propn', None, 'override')
lst = families.get(f) or families.get(l)
if lst == PROPN_LIST:
    return ('offlist', None, 'override') if ov == 'common' else ('propn', None, 'list31')
if lst in BASE: return ('band', lst, '')
if lst in SUPP: return ('supp', lst, '')
if pos == 'PROPN' and ov != 'common': return ('propn', None, 'tag')
return ('offlist', None, '')
```

- [ ] **Step 1: Write the failing tests**

Fixture `families` built by writing tiny files to `tmp_path` and calling `load_families`:
`basewrd1.txt` = `"HUNGRY 3194\r\n\tHUNGER 1124\r\nGO 1\r\n\tWENT 1\r\nMAY 1\r\n"`, `basewrd5.txt` = `"RAY 1\r\n"`, `basewrd12.txt` = `"HEFT 1\r\n"`, `basewrd30.txt` = `"HEFT 0\r\n"`, `basewrd31.txt` = `"ENGLISH 1\r\nTURKEY 1\r\n"`, `basewrd32.txt` = `"OH 1\r\n"`, `basewrd34.txt` = `"NASA 1\r\n"`, `basewrd35.txt` = `"CAFÉ 0\r\n"` (UTF-8).

```python
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
    # build a 3-row xlsx with pandas: Word in ['Apple','a cappella','idea'], Conc.M in [5.0, 3.0, 1.6]
    ...
    assert norms == {'apple': 5.0, 'idea': 1.6}
```

- [ ] **Step 2: Run to verify failure** — `pytest tests/test_lexical.py -v` — Expected: FAIL, `ModuleNotFoundError: lexical`.

- [ ] **Step 3: Implement the four functions and constants** in `lexical.py`. `load_families` reads `basewrd{N}.txt` for each N found, `encoding='utf-8'`, first whitespace-separated token of each non-blank line. Module must not load spaCy or resources at import time (all work under `main()`).

- [ ] **Step 4: Run tests** — Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add reanalysis/lexical.py reanalysis/tests/test_lexical.py
git commit -m "Add BNC/COCA family index, norms loader and token classifier"
```

---

### Task 4: Per-text lexical profile

**Files:**
- Modify: `reanalysis/lexical.py`
- Test: `reanalysis/tests/test_lexical.py`

**Interfaces:**
- Consumes: `classify`, `BASE`, `SUPP` (Task 3).
- Produces: `profile(tokens, families: dict, norms: dict, overrides: dict) -> tuple[dict, list[tuple[str, str]]]`
  - `tokens`: iterable of objects with `.text`, `.lemma_`, `.pos_`, `.is_alpha` (spaCy tokens, or a namedtuple in tests). Non-alpha tokens ignored.
  - Returns `(row, propn_hits)`; `propn_hits` = list of `(lower-cased form, reason)` for every token classified `propn`.
  - `row` keys (exact):
    - `n_tokens`, `n_propn`, `n_supp`, `n_offlist`
    - `cov1k` … `cov9k` — percent, `100 * (band ≤ K + supp) / (n_tokens − n_propn)`
    - `cov5k_base_only` — percent, `100 * (band ≤ 5) / (n_tokens − n_propn)`
    - `cov5k_propn_known` — percent, `100 * (band ≤ 5 + supp + propn) / n_tokens`
    - `propn_pct`, `supp_pct`, `offlist_pct`, `beyond9k_pct` — percent of `n_tokens`
    - `conc_tok` — mean `Conc.M` over matched content tokens; `conc_type` — mean over distinct matched lemmas; `conc_cov` — percent of content tokens matched; content tokens per Global Constraints. NaN when no match.

- [ ] **Step 1: Write the failing tests** (namedtuple `Tok(text, lemma_, pos_, is_alpha)`, reuse the Task 3 `families` fixture, `norms = {'hunger': 2.0, 'ray': 4.0}`)

```python
def test_profile_coverage_excludes_propn():
    toks = [Tok('hunger','hunger','NOUN',True), Tok('ray','ray','NOUN',True),
            Tok('heft','heft','VERB',True), Tok('oh','oh','INTJ',True),
            Tok('Zorba','Zorba','PROPN',True), Tok(',',',','PUNCT',False)]
    row, hits = profile(toks, families, norms, {})
    assert row['n_tokens'] == 5 and row['n_propn'] == 1
    assert row['cov1k'] == 50.0            # hunger + oh / 4
    assert row['cov5k'] == 75.0            # + ray
    assert row['cov9k'] == 75.0            # heft is list 12
    assert row['cov5k_base_only'] == 50.0  # hunger + ray
    assert row['cov5k_propn_known'] == 80.0
    assert row['beyond9k_pct'] == 20.0
    assert hits == [('zorba', 'tag')]

def test_concreteness_token_vs_type():
    toks = [Tok('hunger','hunger','NOUN',True)]*3 + [Tok('ray','ray','NOUN',True),
            Tok('heft','heft','VERB',True)]
    row, _ = profile(toks, families, norms, {})
    assert row['conc_tok'] == 2.5          # (2+2+2+4)/4
    assert row['conc_type'] == 3.0         # (2+4)/2
    assert row['conc_cov'] == 80.0         # 4 of 5 content tokens matched

def test_concreteness_no_matches_is_nan():
    row, _ = profile([Tok('heft','heft','VERB',True)], families, norms, {})
    assert math.isnan(row['conc_tok']) and math.isnan(row['conc_type'])
```

- [ ] **Step 2: Run to verify failure** — Expected: FAIL, `ImportError: cannot import name 'profile'`.
- [ ] **Step 3: Implement `profile`.**
- [ ] **Step 4: Run tests** — `pytest tests -v` — Expected: all pass.
- [ ] **Step 5: Commit** — `git commit -am "Add per-text coverage and concreteness profile"` (with the test file added).

---

### Task 5: Run the profile over the corpus

**Files:**
- Modify: `reanalysis/lexical.py` (add `main()` + `if __name__ == '__main__': main()`)
- Output: `reanalysis/results/lexical_features.csv`, `reanalysis/results/propn_types.csv`

**Interfaces:**
- Consumes: `corpus.iter_texts`, `corpus.window`, `corpus.is_exam`, loaders and `profile`.
- Produces:
  - `results/lexical_features.csv`: columns `book,text,version` + the `profile` row keys; `version` ∈ {`full`, `first360`}; `first360` rows only for coursebook texts → **69 rows** (41 + 28).
  - `results/propn_types.csv`: one row per distinct proper-noun type over the **full** versions; columns `type,reason,n_school,n_exam,also_common_word`, sorted by `n_school + n_exam` descending. `also_common_word` = `reason == 'list31'` **and** the type is a key in `norms`. This flags list-31 words that are also ordinary words (e.g. `turkey`, `china`) for Greg's attention.
  - `main()` reads `data/propn_overrides.csv` via `load_overrides` (absent is fine).

- [ ] **Step 1: Implement `main()`.** spaCy `en_core_web_sm` as in `features.py`; first360 version = `profile(nlp(window(doc)), …)`.
- [ ] **Step 2: Run** — `python lexical.py`
  Expected: writes both CSVs; prints group means of `cov5k`, `conc_tok`, `conc_cov`, `propn_pct` by `book × version`.
- [ ] **Step 3: Sanity checks** (run, read, record numbers in the commit message)
  - `python -c "import pandas as p; d=p.read_csv('results/lexical_features.csv'); print(len(d), d.filter(like='cov').min().min(), d.filter(like='cov').max().max(), d.conc_cov.min())"` — Expected: `69`, all coverage within 0–100, `conc_cov` min ≥ 80. If `conc_cov` < 80 for any text, stop and report it to Greg (spec G5) before continuing.
  - Spearman between new `cov5k` and Phase 1 `own_features.cov5k` (full rows, merged on `book,text`) — print it; expected positive and substantial (ρ > .6). A low value is not a failure but must be reported.
  - Mean `propn_pct` should rank coursebooks > exam (Phase 1: 83 vs 27 per 1k ≈ 8.3% vs 2.7%).
- [ ] **Step 4: Commit**

```bash
git add reanalysis/lexical.py reanalysis/results/lexical_features.csv reanalysis/results/propn_types.csv
git commit -m "Compute lexical profiles for all texts (pre-review)"
```

---

### Task 6: Group comparisons and equivalence test

**Files:**
- Create: `reanalysis/stats5.py`
- Test: `reanalysis/tests/test_stats5.py`
- Output: `reanalysis/results/lexical_comparisons.csv`, `reanalysis/results/lexical_tost.csv`, `reanalysis/results/lexical_thresholds.csv`

**Interfaces:**
- Consumes: `effects.hedges`, `effects.boot_ci`, `results/lexical_features.csv`.
- Produces:
  - `tost_welch(a, b, margin: float) -> dict` with keys `diff` (mean b − mean a), `ci90_lo`, `ci90_hi`, `df`, `p_lower`, `p_upper`, `p_tost` (= max of the two), `equivalent` (bool: `-margin < ci90_lo and ci90_hi < margin`). Welch SE and Welch–Satterthwaite df; `p_lower` tests H0: diff ≤ −margin, `p_upper` tests H0: diff ≥ margin.
  - `compare(a, b) -> dict` with keys `school_M, exam_M, diff, g, g_lo, g_hi, p_welch, p_mw` (a = school, b = exam).
  - `thresholds(F: DataFrame) -> DataFrame` — per group (`school`, `exam`) on full texts: mean `cov1k..cov9k`, plus `level_95`, `level_98` = smallest K whose group mean ≥ threshold, else the string `'not reached by 9k'`.

- [ ] **Step 1: Write the failing tests**

```python
def test_tost_equivalent_when_ci_inside_margin():
    a = np.array([90., 91, 92, 90, 91, 92, 90, 91]); b = a + 0.3
    r = tost_welch(a, b, 2.0)
    assert r['equivalent'] and r['p_tost'] < .05 and np.isclose(r['diff'], 0.3)

def test_tost_not_equivalent_when_diff_large():
    a = np.array([90., 91, 92, 90, 91, 92]); b = a + 3
    assert not tost_welch(a, b, 2.0)['equivalent']

def test_tost_ci_matches_welch_90():
    a, b = np.array([1., 2, 3, 4, 5]), np.array([2., 4, 6, 8])
    r = tost_welch(a, b, 10.0)
    # cross-check against statsmodels
    from statsmodels.stats.weightstats import CompareMeans, DescrStatsW
    lo, hi = CompareMeans(DescrStatsW(b), DescrStatsW(a)).tconfint_diff(alpha=.10, usevar='unequal')
    assert np.isclose(r['ci90_lo'], lo) and np.isclose(r['ci90_hi'], hi)

def test_thresholds_levels():
    F = pd.DataFrame({'book': ['English 1', 'Panhellenics'], 'version': ['full'] * 2,
                      **{f'cov{k}k': [79 + 2 * k, 85 + 2 * k] for k in range(1, 10)}})
    T = thresholds(F).set_index('group')
    assert T.loc['exam', 'level_95'] == 5 and T.loc['school', 'level_95'] == 8
    assert T.loc['school', 'level_98'] == 'not reached by 9k'
```

- [ ] **Step 2: Run to verify failure** — Expected: `ModuleNotFoundError: stats5`.
- [ ] **Step 3: Implement `tost_welch`, `compare`, `thresholds`.**
- [ ] **Step 4: Run tests** — Expected: all pass.
- [ ] **Step 5: Implement `main()`**
  - `lexical_comparisons.csv`, one row per (measure, version) with column `role`:
    - `primary`: `cov5k`, `conc_tok` on `full` → add `p_welch_BH` (statsmodels `fdr_bh` over these two rows only).
    - `robustness`: `cov5k` and `conc_tok` on `first360`; `cov5k_base_only`, `cov5k_propn_known`, `conc_type` on `full`. `p_welch_BH` left empty.
    - `descriptive`: `cov1k..cov9k` (except 5k) on `full`, no p-values.
  - `lexical_tost.csv`: `tost_welch` on `cov5k`, margin 2.0, for `full` (role `primary`) and `first360` (role `robustness`).
  - `lexical_thresholds.csv` from `thresholds`.
  - Console: print the three tables; if the `equivalent` flag differs between `full` and `first360`, print `DISAGREEMENT: full vs length-matched TOST differ — equivalence must be reported as qualified (spec §5).`
- [ ] **Step 6: Run** — `python stats5.py` — Expected: three CSVs written; numbers printed. Do not interpret them yet (proper-noun review pending).
- [ ] **Step 7: Commit** — tests, `stats5.py`, three result CSVs: `git commit -m "Add Phase 2 comparisons and TOST (pre-review)"`.

---

### Task 7: Greg's proper-noun review (human gate)

**Files:**
- Create: `reanalysis/data/propn_overrides.csv` (written from Greg's decisions)

- [ ] **Step 1: Hand over** `results/propn_types.csv` to Greg with a short note: total proper-noun types and tokens by group, and the types flagged `also_common_word`. Ask him to mark misclassified types as `proper` or `common`. **Stop here until he answers.**
- [ ] **Step 2: Write `data/propn_overrides.csv`** (`type,label`) from his answers only.
- [ ] **Step 3: Rerun** — `python lexical.py && python stats5.py` — Expected: completes; print how many tokens changed category per group.
- [ ] **Step 4: Commit**

```bash
git add reanalysis/data/propn_overrides.csv reanalysis/results/
git commit -m "Apply Greg's proper-noun review and rerun Phase 2 lexical analysis"
```

---

### Task 8: Report in README

**Files:**
- Modify: `reanalysis/README.md`

- [ ] **Step 1: Add to the Data section** `fetch_resources.py`, `data/SOURCES.md`, `data/propn_overrides.csv`.
- [ ] **Step 2: Add scripts table rows** for `fetch_resources.py`, `lexical.py`, `stats5.py` (and note `corpus.py`, `effects.py`, `pytest tests`).
- [ ] **Step 3: Add a "Phase 2: lexical measures" findings section** containing, from the result CSVs only:
  - TOST on 5k coverage (full; then length-matched): diff, 90% CI, both one-sided p, verdict; and the disagreement rule outcome.
  - Concreteness: g [95% CI], Welch p, BH-corrected p, `conc_cov` range.
  - Threshold table (levels reaching 95% / 98% per group).
  - Robustness rows in one sentence each, stating whether they agree.
  - Caveat lines: spaCy-based proper-noun detection with manual review; list 35 treated as supplementary (Claude's call); word concreteness captures only part of the topic/argument abstractness (Phase 4b).
  - The scope-rationale paragraph from spec §6.
  - Wording rule: say "equivalent within ±2 points" only if the primary TOST passes **and** the length-matched TOST agrees; otherwise state exactly what was found.
- [ ] **Step 4: Verify** — every number in the new section appears in a `results/lexical_*.csv` file (spot-check each against the CSV).
- [ ] **Step 5: Commit** — `git commit -am "Document Phase 2 lexical findings"`.
