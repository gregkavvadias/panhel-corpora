# Phase 3 Corpus Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the 13 new exam reading passages (June 2023–2026, resits 2018–2026) into a staging area, get Greg's approval, promote them into the corpus, and rerun the Phase 2 lexical analysis on 28 vs 26 texts with June-only and original-13 comparisons.

**Architecture:** `extract_exams.py` downloads the PDFs listed in `data/exam_sources.csv`, extracts page 2's passage from pdfplumber words (body-style filter, optional two-column split, layout-based paragraphs), applies Greg's recorded corrections, and writes `staging/Panhellenics/*.txt` plus a review report. `promote_exams.py` copies only approved files into `Texts/Panhellenics/`. `stats5.py` gains subset and sitting comparisons.

**Tech Stack:** Python 3.13, pdfplumber, pandas, scipy, pytest (all installed).

**Spec:** `docs/superpowers/specs/2026-10-27-phase3-corpus-extension-design.md`

## Global Constraints

- Run all scripts from `reanalysis/`; use `pathlib`; outputs go to `results/`.
- New files: `2023-06 … 2026-06` and `2018-09 … 2026-09` (13 files). Format: UTF-8, CRLF line endings, one paragraph per line, a blank line between paragraphs, no trailing blank line. No title, source line, URL, instructions or page furniture.
- Target text = the text **visible on the rendered page**. Off-style text (a font family or size other than the passage body style) is excluded and **reported**.
- Mechanical changes only: joining lines within a paragraph, dehyphenating a word broken across a line (and listing it), replacing ligatures (ﬁ→fi, ﬂ→fl), removing soft hyphens (U+00AD), collapsing runs of spaces. **No quote or dash normalisation:** the existing exam files mix ASCII and typographic forms, so the PDF's characters are kept (Claude's ruling, recorded in README). Everything else is flagged, not changed.
- PDFs go to `reanalysis/data/exam_pdfs/` (gitignored). Staging is `reanalysis/staging/Panhellenics/` (committed). Corrections: `reanalysis/data/exam_corrections.csv` (`file,find,replace,note`). Approvals: `reanalysis/data/exam_approvals.csv` (`file,approved_by,date`).
- No new file enters `Texts/` without a row in `exam_approvals.csv` that Greg asked for.
- Phase 2 settings are unchanged: primary = `cov5k` (TOST ±2.0) and `conc_tok`, full texts, BH over those two; seed 1, B = 5000.
- Exam subsets: `all` (26), `june` (17: text ids ending `-06`), `original13` (June, year ≤ 2022). Sitting: `-06` = june, `-09` = resit.
- Download: Drive ids via `https://drive.google.com/uc?export=download&id=<id>`; urllib with header `User-Agent: Mozilla/5.0 (panhel-corpora extract_exams.py)`; a downloaded file must start with `%PDF-`.

## Review Focus

1. A body-text line that happens to contain a domain (e.g. "…posted on google.com every day…") must not end the passage; only short lines (≤ 8 words) match the domain rule. → Task 2 `test_end_marker_ignores_long_body_line_with_domain`.
2. A paragraph whose last line nearly reaches the right margin (ends ≥ 85% across) must still break if followed by a clear vertical gap. → Task 2 `test_paragraph_break_on_vertical_gap`.
3. A line ending in a hyphen that is a real compound across lines ("well-" / "known") must be joined **keeping** the hyphen when the joined form isn't a known word but the hyphenated form is plausible; since that can't be decided mechanically, every dehyphenation is listed for Greg. → Task 2 `test_dehyphenation_is_recorded`.
4. A correction whose `find` text occurs zero times or more than once must stop the run, naming the file and row. → Task 3 `test_correction_must_match_exactly_once`.
5. Promoting an approved file whose `Texts/` copy already exists with different content must refuse, not overwrite. → Task 5 `test_promote_refuses_to_overwrite_different_file`.

---

### Task 1: Sources list and PDF download

**Files:**
- Create: `reanalysis/data/exam_sources.csv`, `reanalysis/extract_exams.py` (download part only)
- Modify: `.gitignore` (add `reanalysis/data/exam_pdfs/`)

**Interfaces:**
- Produces:
  - `data/exam_sources.csv` columns `file,url,page_url,columns`; `columns` is `2` for 2018-09, 2019-09 and 2020-09, else `1`. `url` is the direct download URL (Drive `uc?export=download&id=…` or the site PDF). Values from spec §6. `page_url` is the panellinies.net year page.
  - `extract_exams.load_sources(path: Path) -> list[dict]`
  - `extract_exams.fetch(row: dict, dest: Path) -> tuple[Path, str]` — downloads to `dest/<file>.pdf` if absent; returns `(path, sha256_hex)`; raises `ValueError` naming the file if the bytes don't start with `%PDF-`.

- [ ] **Step 1: Write `exam_sources.csv`** with the 13 rows (page URLs: `https://www.panellinies.net/agglika-2024/` etc., or the percent-encoded Greek URLs for 2018-09 … 2020-09 and 2023-06, copied from the site index).
- [ ] **Step 2: Implement `load_sources`, `fetch`** and a `__main__` that, for now, fetches all rows and prints `file sha256[:12] size`.
- [ ] **Step 3: Run** `python extract_exams.py` — Expected: 13 lines, no error; `git status` does not list `data/exam_pdfs/`.
- [ ] **Step 4: Commit** `.gitignore`, `data/exam_sources.csv`, `extract_exams.py` — "Add exam paper sources and downloader".

---

### Task 2: Passage extraction core

**Files:**
- Modify: `reanalysis/extract_exams.py`
- Test: `reanalysis/tests/test_extract_exams.py`

**Interfaces:**
- Works on pdfplumber word dicts with keys `text, x0, x1, top, bottom, fontname, size` (from `page.extract_words(extra_attrs=['fontname', 'size'])`).
- Produces:
  - `style(w: dict) -> tuple[str, float]` — `(family, size)`: family = fontname after any `XXXXXX+` subset prefix, cut at the first `-` or `,`, with a trailing `MT` removed (`GCNONE+ArialMT`→`Arial`, `Arial-BoldMT`→`Arial`, `Arial,Bold`→`Arial`, `Helvetica-Bold`→`Helvetica`); size rounded to the nearest 0.5.
  - `body_style(words: list[dict]) -> tuple[str, float]` — style with the most characters.
  - `group_lines(words: list[dict]) -> list[dict]` — words with `top` within 2.0 pt form a line; line dict `text, x0, x1, top, bottom`; words joined by single spaces in x order; lines sorted by `top`.
  - `is_end_marker(line_text: str) -> bool` — True if the line starts with `Adapted from`, `http`, `www.` or `ΤΕΛΟΣ`; or is only a year in brackets/`(June 2023)`; or has ≤ 8 words and contains a domain matching `\b[\w-]+\.(com|org|net|gov|edu|co\.uk)\b` (allow an internal space as in `bbc focus.co.uk`).
  - `passage_lines(words: list[dict], page_width: float, columns: int) -> tuple[list[dict], list[str]]` — returns `(lines in reading order, dropped_offstyle_texts)`. Steps: compute `body_style`; drop words whose style ≠ body (collect their text, grouped into lines, as dropped); find the line containing `Read the text below`; keep lines whose `top` > that line's `bottom`; if `columns == 2`, split kept words at `page_width / 2` (by word centre), process left column then right; in each column, stop at the first line where `is_end_marker` is true.
  - `paragraphs(lines: list[dict]) -> tuple[list[str], list[str]]` — returns `(paragraphs, dehyphenated_words)`. Per column (call it once per column and concatenate): `right = max(x1)`, `width = right - min(x0)`; median inter-line gap `g` = median of `top[i+1] - bottom[i]`. Line i ends a paragraph if `x1 < right - 0.15 * width` or the next gap > `1.8 * g`. Join lines with a space, except when a line ends with `-` preceded by a letter and the next starts with a lowercase letter: join without space and drop the hyphen, recording the joined word.
  - `clean(text: str) -> str` — ligatures, soft hyphens, whitespace collapse (Global Constraints).

- [ ] **Step 1: Write the failing tests** (helper `W(text, x0, top, font='GCNONE+ArialMT', size=10.0)` builds a word with `x1 = x0 + 6*len(text)`, `bottom = top + 10`)

```python
def test_style_family_and_size():
    assert style(W('a', 0, 0, 'GCNONE+ArialMT', 10.04)) == ('Arial', 10.0)
    assert style(W('a', 0, 0, 'Arial,Bold', 11)) == ('Arial', 11.0)
    assert style(W('a', 0, 0, 'ABCDEF+Helvetica-Bold', 11)) == ('Helvetica', 11.0)

def test_offstyle_words_are_dropped_and_reported():
    ws = [W('Read the text below', 50, 100), W('Visible', 50, 120), W('words', 100, 120),
          W('hidden', 50, 140, font='GCNOLO+Calibri', size=11)]
    lines, dropped = passage_lines(ws, 600, 1)
    assert [l['text'] for l in lines] == ['Visible words'] and dropped == ['hidden']

def test_two_columns_read_left_then_right():
    ws = [W('Read the text below', 50, 100),
          W('left1', 50, 120), W('right1', 320, 120), W('left2', 50, 135), W('right2', 320, 135)]
    lines, _ = passage_lines(ws, 600, 2)
    assert [l['text'] for l in lines] == ['left1', 'left2', 'right1', 'right2']

def test_end_markers():
    for s in ['Adapted from', 'https://www.bbc.com (2022)', 'bbc.com', 'https://www.bbc focus.co.uk',
              '(2018)', '(June 2023)', 'ΤΕΛΟΣ 2ΗΣ ΑΠΟ 6 ΣΕΛΙΔΕΣ', 'Adapted from https://www.scientificamerican.com']:
        assert is_end_marker(s), s
    assert not is_end_marker('Pet care and self-care are linked. When')

def test_end_marker_ignores_long_body_line_with_domain():
    assert not is_end_marker('people now post their diaries on blogger.com and read them every day')

def test_paragraph_break_on_short_line():
    ls = [L('aaaa aaaa aaaa aaaa', 50, 450, 100), L('end.', 50, 120, 112), L('next para', 50, 450, 124)]
    ps, _ = paragraphs(ls)
    assert ps == ['aaaa aaaa aaaa aaaa end.', 'next para']

def test_paragraph_break_on_vertical_gap():
    ls = [L('one', 50, 440, 100), L('two', 50, 445, 112), L('three.', 50, 442, 124), L('new', 50, 450, 152)]
    assert paragraphs(ls)[0] == ['one two three.', 'new']

def test_dehyphenation_is_recorded():
    ls = [L('the class-', 50, 450, 100), L('room was', 50, 450, 112)]
    ps, dh = paragraphs(ls)
    assert ps == ['the classroom was'] and dh == ['classroom']

def test_clean_ligatures_and_soft_hyphen():
    assert clean('ﬁne  ﬂow co­operate') == 'fine flow cooperate'
```

(`L(text, x0, x1, top)` builds a line dict with `bottom = top + 10`.)

- [ ] **Step 2: Run** `python -m pytest tests/test_extract_exams.py -q` — Expected: FAIL, `ImportError` for `style`.
- [ ] **Step 3: Implement** the functions above.
- [ ] **Step 4: Run** — Expected: all pass; full suite `python -m pytest tests -q` passes.
- [ ] **Step 5: Commit** — "Add exam passage extraction core".

---

### Task 3: Corrections, suspects, review report, staging output

**Files:**
- Modify: `reanalysis/extract_exams.py`
- Create: `reanalysis/data/exam_corrections.csv` (header only), `reanalysis/staging/Panhellenics/*.txt`, `reanalysis/results/exam_review.md`, `reanalysis/data/EXAM_SOURCES.md`
- Test: `reanalysis/tests/test_extract_exams.py`

**Interfaces:**
- Consumes: Task 1 `load_sources`, `fetch`; Task 2 functions; `lexical.load_families`, `lexical.load_norms`.
- Produces:
  - `load_corrections(path: Path) -> list[dict]` (`file, find, replace, note`; missing file → `[]`)
  - `apply_corrections(text: str, file: str, rows: list[dict]) -> str` — applies rows for `file` in order; raises `ValueError` naming file, `find` and the count if a `find` occurs ≠ 1 time.
  - `suspects(text: str, families: dict, norms: dict) -> list[tuple[str, str]]` — `(token, reason)` with reasons: `unknown` (alphabetic token, lower-cased, not in families and not in norms, and not capitalised mid-sentence — capitalised tokens are names and are skipped), `capital-I` (regex `[a-z]I[a-z]|[a-z]Is\b`), `split-letter` (regex `\b[A-Z] [a-z]{2,}`), `odd-char` (any char outside ASCII printable and `‘’“”–—…é`).
  - `apply_corrections` error message format: `f"{file}: correction find {find!r} occurs {n} times (must be 1)"`.
  - `split_headings(paragraphs: list[str]) -> tuple[list[str], list[str]]` — a paragraph of ≤ 8 words that does not end in `. ? ! " ” ’ :` is a heading: removed and returned in the second list (spec §5).
  - `extract(pdf: Path, columns: int) -> dict` with keys `paragraphs, dropped_offstyle, dropped_headings, dehyphenated` (page index 1); applies `split_headings` after `paragraphs`. The review report lists `dropped_headings`.
  - `write_text(path: Path, paragraphs: list[str]) -> None` — `'\r\n\r\n'.join(paragraphs)` encoded UTF-8, no BOM, no trailing newline (check against an existing file, e.g. `Texts/Panhellenics/2022-06.txt`, whether it ends with CRLF; match it).
  - `main()` — for each source: fetch, extract, `clean` each paragraph, apply corrections, write `staging/Panhellenics/<file>.txt`; write `results/exam_review.md` (per file: words, paragraphs, sha256, dropped off-style text, dehyphenated words, suspects, approved yes/no from `exam_approvals.csv`) and `data/EXAM_SOURCES.md` (file, page URL, download URL, sha256, download date).

- [ ] **Step 1: Write the failing tests**

```python
def test_correction_applies_once():
    rows = [{'file': '2023-06', 'find': 'schooIs', 'replace': 'schools', 'note': ''}]
    assert apply_corrections('in schooIs or', '2023-06', rows) == 'in schools or'
    assert apply_corrections('in schooIs or', '2024-06', rows) == 'in schooIs or'

def test_correction_must_match_exactly_once():
    rows = [{'file': 'x', 'find': 'a', 'replace': 'b', 'note': ''}]
    with pytest.raises(ValueError, match="x.*'a'.*2"):
        apply_corrections('a a', 'x', rows)
    with pytest.raises(ValueError, match="x.*'a'.*0"):
        apply_corrections('zzz', 'x', rows)

def test_suspects():
    fam = {'school': 1, 'cat': 1, 'the': 1, 'had': 1, 'a': 1, 'how': 1, 'odd': 1}
    s = dict(suspects('The schooIs had a cat. H ow odd zqxv.', fam, {}))
    assert s['schooIs'] == 'capital-I' and s['zqxv'] == 'unknown' and s['H ow'] == 'split-letter'

def test_split_headings():
    ps, hs = split_headings(['Pet care and self-care', 'Pet care and self-care are linked.', 'A short one.'])
    assert hs == ['Pet care and self-care'] and ps == ['Pet care and self-care are linked.', 'A short one.']

def test_write_text_crlf_paragraphs(tmp_path):
    p = tmp_path / 't.txt'; write_text(p, ['One.', 'Two.'])
    assert p.read_bytes().startswith(b'One.\r\n\r\nTwo.')
```

Integration tests on the real PDFs (mark `@pytest.mark.skipif` when `data/exam_pdfs/2024-09.pdf` is absent):

```python
def test_real_2024_09_excludes_hidden_layer():
    r = extract(PDFS / '2024-09.pdf', 1); text = ' '.join(r['paragraphs'])
    assert text.startswith('How can we protect children') and 'burdening' not in text
    assert 340 <= len(text.split()) <= 400 and r['dropped_offstyle']

def test_real_2018_09_columns_in_order():
    text = ' '.join(extract(PDFS / '2018-09.pdf', 2)['paragraphs'])
    assert text.startswith('Many people would find long dark nights and bitter cold pretty depressing.')

def test_real_2020_09_keeps_pet_care_sentence_in_paragraph():
    ps = extract(PDFS / '2020-09.pdf', 2)['paragraphs']
    assert any(p.startswith('Pet care and self-care are linked.') for p in ps)
    assert not any(p == 'Pet care and self-care' for p in ps)

def test_real_all_word_counts_plausible():
    for row in load_sources(SOURCES):
        n = len(' '.join(extract(PDFS / f"{row['file']}.pdf", int(row['columns']))['paragraphs']).split())
        assert 300 <= n <= 420, (row['file'], n)
```

- [ ] **Step 2: Run** — Expected: FAIL (`ImportError`).
- [ ] **Step 3: Implement** the functions and `main()`.
- [ ] **Step 4: Run tests** — Expected: all pass. If a real-PDF test fails, debug the heuristics (systematic-debugging), not the test's expectations; the expectations come from the rendered pages.
- [ ] **Step 5: Run** `python extract_exams.py` — Expected: 13 staging files, `results/exam_review.md`, `data/EXAM_SOURCES.md`; review report lists `schooIs` under 2023-06 and off-style text under 2024-09.
- [ ] **Step 6: Commit** script, tests, staging files, review report, sources, empty corrections file — "Extract 13 new exam passages to staging (unreviewed)".

---

### Task 4: Greg's text review (human gate)

- [ ] **Step 1: Hand over** `results/exam_review.md` and the staging folder, with the PDFs' location. Ask Greg to compare each file with its PDF page 2 and reply per file: approved, or corrections (find → replace). Point out the flagged items first. **Stop until he answers.**
- [ ] **Step 2: Record** his corrections in `data/exam_corrections.csv` and approvals in `data/exam_approvals.csv` (`approved_by=Greg Kavvadias`, today's date) — only what he said.
- [ ] **Step 3: Rerun** `python extract_exams.py` — Expected: no error; corrections applied; review report shows approvals.
- [ ] **Step 4: Commit** — "Record Greg's review of new exam passages".

---

### Task 5: Promote approved texts into the corpus

**Files:**
- Create: `reanalysis/promote_exams.py`
- Modify: `reanalysis/tests/test_helpers.py` (Panhellenics count 13 → 26)
- Test: `reanalysis/tests/test_promote_exams.py`

**Interfaces:**
- Produces: `promote(staging: Path, target: Path, approvals: Path) -> list[str]` — copies `staging/<file>.txt` to `target/<file>.txt` for every approved file; returns the files copied (identical existing targets are skipped silently, not returned); raises `FileExistsError` naming the file if a target exists with different bytes; raises `FileNotFoundError` if an approved file is missing from staging. Unapproved staging files are never copied.

- [ ] **Step 1: Write the failing tests**

```python
def test_promote_only_approved(tmp_path):
    s, t = tmp_path / 's', tmp_path / 't'; s.mkdir(); t.mkdir()
    (s / 'a.txt').write_text('A'); (s / 'b.txt').write_text('B')
    ap = tmp_path / 'ap.csv'; ap.write_text('file,approved_by,date\na,Greg,2026-10-27\n')
    assert promote(s, t, ap) == ['a'] and not (t / 'b.txt').exists()

def test_promote_refuses_to_overwrite_different_file(tmp_path):
    ...  # target a.txt exists with 'OLD' → FileExistsError match 'a'

def test_promote_identical_target_is_noop(tmp_path):
    ...  # target a.txt == staging → returns []

def test_promote_missing_staging_file(tmp_path):
    ...  # approvals lists 'c' absent from staging → FileNotFoundError match 'c'
```

- [ ] **Step 2: Run** — Expected: FAIL (`ModuleNotFoundError`).
- [ ] **Step 3: Implement** `promote` and `__main__` (`promote(Path('staging/Panhellenics'), Path('../Texts/Panhellenics'), Path('data/exam_approvals.csv'))`, prints the list).
- [ ] **Step 4: Run tests** — Expected: pass.
- [ ] **Step 5: Run** `python promote_exams.py` — Expected: prints the approved files (13 if all approved). Change `test_iter_texts_counts` to expect 26 Panhellenics; run full suite — Expected: pass. If Greg approved fewer than 13, stop and report instead of changing the count.
- [ ] **Step 6: Commit** — "Promote approved exam passages into the corpus".

---

### Task 6: Subset and sitting comparisons

**Files:**
- Modify: `reanalysis/stats5.py`
- Test: `reanalysis/tests/test_stats5.py`

**Interfaces:**
- Consumes: existing `compare`, `tost_welch`, `MARGIN`.
- Produces:
  - `sitting(text_id: str) -> str` — `'june'` for `-06`, `'resit'` for `-09`, else `ValueError`.
  - `exam_subsets(exam: DataFrame) -> dict[str, DataFrame]` — keys `all`, `june`, `original13` (Global Constraints).
  - `main()` additionally writes:
    - `results/lexical_subsets.csv` — for each subset × (`cov5k`, `conc_tok`) on full texts: `subset, measure, n_exam` + `compare` keys; for `cov5k` also `ci90_lo, ci90_hi, p_tost, equivalent` from `tost_welch`. Within each subset, `p_welch_BH` over its two rows.
    - `results/lexical_sitting.csv` — `compare(june, resit)` for `cov5k` and `conc_tok` (diff = resit − june), plus `n_june, n_resit`. Descriptive, no BH.
  - Existing outputs keep their meaning (they are the `all` subset).

- [ ] **Step 1: Write the failing tests**

```python
def test_sitting():
    assert sitting('2023-06') == 'june' and sitting('2018-09') == 'resit'
    with pytest.raises(ValueError): sitting('unit-2-1')

def test_exam_subsets_sizes():
    ids = [f'{y}-06' for y in range(2010, 2027)] + [f'{y}-09' for y in range(2018, 2027)]
    E = pd.DataFrame({'text': ids})
    S = exam_subsets(E)
    assert (len(S['all']), len(S['june']), len(S['original13'])) == (26, 17, 13)
```

- [ ] **Step 2: Run** — Expected: FAIL (`ImportError`).
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run tests** — Expected: pass.
- [ ] **Step 5: Commit** — "Add exam subset and sitting comparisons".

---

### Task 7: Rerun Phase 2 and proper-noun review of new types (human gate)

- [ ] **Step 1: Run** `python lexical.py` — Expected: `results/lexical_features.csv` has 82 rows (54 full + 28 first360).
- [ ] **Step 2: Hand over** to Greg the proper-noun types that occur **only** in the new texts (compare `propn_types.csv` with the version in commit `ee0280e`), with the same summary as Phase 2 (tag-only types, `also_common_word` types, suggested `common` list). **Stop until he answers.**
- [ ] **Step 3: Append** his decisions to `data/propn_overrides.csv`; rerun `python lexical.py && python stats5.py` — Expected: all outputs written.
- [ ] **Step 4: Check** the `original13` row of `lexical_subsets.csv` against the published Phase 2 numbers (`lexical_comparisons.csv` / `lexical_tost.csv` at `ee0280e`); record whether any 13-text figure moved, and why (new overrides).
- [ ] **Step 5: Commit** overrides and all results — "Rerun Phase 2 on 26 exam texts".

---

### Task 8: README

**Files:** Modify `reanalysis/README.md`, `HANDOFF.md` (Phase 3 status line only)

- [ ] **Step 1:** Data section: `data/exam_sources.csv`, `data/EXAM_SOURCES.md`, `exam_corrections.csv`, `exam_approvals.csv`, `staging/`; scripts table: `extract_exams.py`, `promote_exams.py`; update the corpus description (13 → 26 exam texts: 17 June 2010–2026, 9 resit 2018–2026; diaspora papers excluded and why).
- [ ] **Step 2:** New section "Phase 3: extended exam corpus" from the result CSVs only: 26-text primary results (TOST, concreteness g, BH p); June-only and original-13 rows; sitting check (g [CI] for both measures); a sentence on whether conclusions agree across subsets; extraction notes (hidden layer in 2024-09, two-column resits, quotes/dashes kept as in PDF, every correction listed in `exam_corrections.csv`); note that Phase 1 Coh-Metrix and `features.py`/`stats4.py` results remain on the original 13 exam texts until part 2.
- [ ] **Step 3: Verify** every number against the CSVs.
- [ ] **Step 4: Commit** — "Document Phase 3 corpus extension".
