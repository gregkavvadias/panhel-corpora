# Reanalysis (2026)

A reanalysis of the MA thesis data (Kavvadias, 2023, Hellenic Open University), comparing reading texts in the Greek state high-school English coursebooks (*English 1*, *English 2*; n = 28) with the Panhellenic English reading texts. The exam corpus originally held the 13 June papers of 2010–2022. Phase 3 extended it to **26** texts: 17 June papers (2010–2026) and 9 September resit papers (2018–2026).
- **Diaspora (ομογενείς) papers are excluded.** They are a separate exam for a different group of candidates, widely believed to be easier.
- **Coh-Metrix analyses stay at 13 exam texts.** The Phase 1 Coh-Metrix analyses and `features.py`/`stats4.py` still cover the original 13 only; part 2 of Phase 3 replaces them with open measures on all texts.

Run every script from this folder (`cd reanalysis`).

## Data

- `data/cohmetrix_appA.csv`: Coh-Metrix 3.0 values per text, parsed from Appendix A of the thesis (`python3 parse_appA.py <thesis.pdf>`).
  - In Appendix A, CRFSOa and LSASSp are rounded to one decimal place, so results for those two indices are approximate.
  - Appendix A has a WRDPRO (pronoun) column, while Appendices B–D report WRDPOLc (polysemy), so polysemy can't be reproduced from this file.
- `data/bnc_coca/` and `data/brysbaert_concreteness.xlsx`: the BNC/COCA word-family lists (basewords 1.3.0) and the Brysbaert et al. (2014) concreteness norms. Both are downloaded by `python fetch_resources.py` and are not committed. Their sources, versions and citations are in `data/SOURCES.md`.
- `data/exam_sources.csv`: download URL, source page and column layout for each new exam paper.
- `data/EXAM_SOURCES.md`: the same sources with a SHA-256 hash of each PDF. The PDFs themselves are downloaded to `data/exam_pdfs/` and not committed.
- `data/exam_corrections.csv`: Greg's corrections to the extracted passages, applied by `extract_exams.py`.
- `data/exam_approvals.csv`: Greg's approval of each new passage.
- `staging/Panhellenics/`: the extracted passages before promotion; `results/exam_review.md` is the review report Greg checked.
- `data/propn_overrides.csv`: manual corrections to proper-noun detection, from Greg's review of `results/propn_types.csv`. Each listed word is marked `proper` or `common`.

## Scripts

| Script | What it does | Output |
|---|---|---|
| `stats1.py` | School vs exam on all 29 Coh-Metrix indices: Welch and Mann–Whitney tests, Hedges' g with bootstrap 95% CIs, Benjamini–Hochberg and Holm corrections, how much each index depends on text length | `results/group_comparisons.csv` |
| `stats2.py` | Pearson and Spearman correlations of each index with RDL2, within each group, BH-corrected | `results/corr_school.csv`, `results/corr_exam.csv` |
| `stats3.py` | English 1 vs English 2 vs exam (Kruskal–Wallis); minimum detectable effect at 80% power; 90% CI for the RDL2 difference | console |
| `features.py` | Features recomputed from the raw texts with spaCy and wordfreq: sentence length, noun and passive rates, MTLD, Flesch scores (pyphen syllables), content-word frequency, 2k/3k/5k frequency-list coverage. Includes a version of the school texts cut to their first ~360 words to match exam length | `results/own_features.csv` |
| `stats4.py` | Group tests on those features (full and length-matched texts); agreement with Coh-Metrix | console |
| `noun_split.py` | Splits Coh-Metrix WRDNOUN into common vs proper nouns and relates each to RDL2 | `results/nouns_split.csv` |
| `fetch_resources.py` | Downloads the Phase 2 lexical resources into `data/` | `data/bnc_coca/`, `data/brysbaert_concreteness.xlsx` |
| `lexical.py` | Phase 2 profile of each text: BNC/COCA word-family coverage at 1k–9k (proper nouns left out of the count; supplementary lists counted as known) and mean Brysbaert concreteness of content words, for full texts and the length-matched school texts. Also lists every word classed as a proper noun, for manual review | `results/lexical_features.csv`, `results/propn_types.csv` |
| `stats5.py` | Phase 2 comparisons: an equivalence test (TOST) on 5k coverage with a ±2-point margin; Welch and Mann–Whitney tests with Hedges' g and bootstrap CIs; BH correction over the two primary tests; the 95% and 98% coverage thresholds | `results/lexical_comparisons.csv`, `results/lexical_tost.csv`, `results/lexical_thresholds.csv` |

| `extract_exams.py` | Downloads the new exam papers and extracts the main reading passage from page 2. Only the text visible on the page is kept: words in another font, such as a hidden text layer, are excluded and reported. Two-column papers are read left column first. Paragraphs are rebuilt from the layout, and Greg's corrections are applied. Writes the review report | `staging/Panhellenics/`, `results/exam_review.md`, `data/EXAM_SOURCES.md` |
| `promote_exams.py` | Copies approved passages into `Texts/Panhellenics/`. It refuses to overwrite a file that differs | `Texts/Panhellenics/` |

`stats5.py` also writes `results/lexical_subsets.csv` (the primary tests for all 26 exam texts, June-only and the original 13) and `results/lexical_sitting.csv` (June vs resit).

`corpus.py` (text loading, length-matching window) and `effects.py` (Hedges' g, bootstrap CI) are shared helpers. Tests: `python -m pytest tests`.

## Main findings

- **9 of the thesis's 14 significant differences survive BH correction.** Three of those are just text length (paragraph, sentence and word counts). The other six survive: the exam texts are lower in concreteness, imageability and meaningfulness, have fewer passives, longer sentences and fewer causal verbs and particles.
- **The readability formulas (FRE, FKGL, RDL2) show no difference, but the study is underpowered.** With 28 vs 13 texts, the minimum detectable effect is g ≈ 0.96. For RDL2, g = 0.29 with a 95% CI of [−0.34, 1.01], so the data can't show the groups are equivalent either.
- **The coursebooks' higher WRDNOUN comes entirely from proper nouns** (83 vs 27 per 1,000 words). The exam texts actually have slightly more common nouns.
- **The exam texts use more frequent vocabulary** (5k coverage 92.2% vs 90.2%) and this holds after length matching. *Superseded by Phase 2: with BNC/COCA word families, the difference disappears (see below).* Combined with the concreteness results, the exam texts are expository and abstract, while the coursebook texts are narrative.
- **The exam-group correlations in §4.7 reproduce from Appendix A.** Appendix D accidentally prints the school-text table twice.
- **English 1 and English 2 don't differ on any index.**

Caveat: coverage is calculated from wordfreq word-form lists, not BNC/COCA word families, so treat it as indicative. Phase 2 (below) replaces it.

## Phase 2: lexical measures

*The figures in this section are the original pre-specified run on 13 exam texts, as published in commit `ee0280e`. Since Phase 3, `results/lexical_comparisons.csv`, `lexical_tost.csv` and `lexical_thresholds.csv` hold the 26-text results. The 13-text primary figures are reproduced exactly in the `original13` rows of `results/lexical_subsets.csv`.*

The design is in `docs/superpowers/specs/2026-10-23-phase2-lexical-design.md`. The analysis choices were fixed before any results were seen:
- **Primary comparisons:** 5k coverage and token-weighted concreteness, on the full texts.
- **Equivalence margin:** ±2 percentage points of coverage, justified by the gap between the 95% and 98% comprehension thresholds.
- **Robustness checks:** the length-matched texts and the other variants, all uncorrected.

Differences are exam − school.

- **Frequency coverage: the exam and coursebook texts are equivalent within ±2 points at 5k.**
  - Mean 5k coverage is 97.96% for the exam texts and 97.80% for the coursebooks: a difference of +0.16 points, 90% CI [−0.51, 0.83].
  - The equivalence test passes: p = .00001 and .00007, Welch df = 18.8.
  - The difference test finds no difference: g = 0.15, 95% CI [−0.52, 0.98], Welch p = .69, BH-corrected p = .69.
  - The length-matched comparison agrees: +0.35 points, 90% CI [−0.35, 1.04], equivalence p = .0003.
  - So by word frequency, the two groups differ by less than 2 coverage points: at most the exam texts are 0.51 points lower.
  - **How to read this:** the equivalence holds in raw coverage points, the scale on which the margin was set. In standardised terms the picture is less certain. Coverage is near ceiling, with an SD of about 1 point, so the ±2-point margin is about 1.9 pooled SDs. The 95% CI for g, [−0.52, 0.98], cannot rule out a moderate standardised difference. The claim is that any difference is too small to matter for comprehension, not that the groups are identical.
- **This replaces the Phase 1 finding that the exam texts use more frequent vocabulary.** Measured by word families, with proper nouns left out of the count, that difference disappears.
- **Thresholds (mean coverage):** the exam texts reach 95% at the 3k level and 98% at 6k (97.96% at 5k). The coursebook texts reach 95% at 4k and 98% at 6k. These are group means; individual texts vary:
  - At 6k, 9 of 13 exam texts and 20 of 28 coursebook texts reach 98%.
  - At 5k, every coursebook text reaches 95%, and so do 12 of the 13 exam texts. The exception is 2016-06, at 94.4%.
- **Concreteness: the exam texts use more abstract vocabulary.**
  - Mean Brysbaert concreteness of content words is 2.92 for the exam texts and 3.14 for the coursebooks: g = −1.00, 95% CI [−1.75, −0.42], Welch p = .003, BH-corrected p = .005.
  - This confirms the Phase 1 Coh-Metrix concreteness result with a measure anyone can reproduce.
  - The norms cover at least 95% of the content words in every text.
- **The robustness checks all agree:**
  - length-matched concreteness: g = −1.06, p = .001;
  - type-weighted concreteness: g = −1.05, p = .0004;
  - 5k coverage from the band lists only, without the supplementary lists: g = 0.13, p = .71;
  - 5k coverage with proper nouns counted as known: g = 0.04, p = .92.
- **Token accounting (mean % of tokens, exam vs coursebook):**
  - proper nouns: 1.16 vs 6.43;
  - supplementary lists: 0.80 vs 0.78;
  - off-list: 0.33 vs 0.20.
  - Tokens left out of the counts entirely: 1.56 vs 1.21. These are non-alphabetic tokens that contain a letter, such as clitics (*'s*, *n't*), abbreviations like *U.S.*, and a few words the tokenizer glued to punctuation. Numbers and punctuation are excluded as well.
- **Caveats:**
  - **Proper nouns:** they are identified from Nation's proper-noun list (list 31) plus spaCy's PROPN tag. A word on a frequency-band list is never treated as a proper noun.
    - Greg reviewed all 404 detected types. 15 foreign or ordinary words were reclassified as common (`data/propn_overrides.csv`); 24 tokens changed category.
  - **List 35:** accented spellings are counted as known, like the other supplementary lists. This was Claude's call.
  - **Concreteness:** word-level ratings capture only part of what makes the exam texts abstract. Their topics and the way they argue are left for the genre analysis (Phase 4b).
  - **Ceiling effect:** word-family coverage is near the ceiling for every text (5k range 94.4–100%). It correlates only weakly with the Phase 1 word-form coverage (ρ = .35, before the proper-noun review).

**Scope rationale (draft for the paper's methods):** Lexical difficulty was operationalised with two well-established, openly available resources that answer the research question directly. The first is text coverage by BNC/COCA word-family frequency bands (Nation, 2017), which links directly to established comprehension thresholds (Hu & Nation, 2000; Laufer & Ravenhorst-Kalovski, 2010). The second is word concreteness ratings (Brysbaert et al., 2014). Broader multi-index tools (e.g. TAALES) were not used, because with 41 texts, adding many correlated indices would raise the multiple-comparison burden without sharpening the test of the central claim.

## Phase 3: extended exam corpus (26 texts)

The design is in `docs/superpowers/specs/2026-10-27-phase3-corpus-extension-design.md`. Thirteen exam passages were added: June 2023–2026 and the September resits of 2018–2026. Each was extracted from the official paper PDF and checked by Greg against the page before entering the corpus. The Phase 2 settings are unchanged: 5k coverage with a ±2-point equivalence margin, token-weighted concreteness, full texts as primary, and BH correction over the two primary tests. Differences are exam − school.

### Primary results: 28 coursebook vs 26 exam texts

- **5k coverage: equivalent within ±2 points.**
  - Exam 98.21%, coursebooks 97.80%: a difference of +0.41, 90% CI [−0.08, 0.89].
  - Equivalence test: p < .001 for both one-sided tests (Welch df = 48.4).
  - Difference test: g = 0.38, 95% CI [−0.15, 1.05], Welch p = .17, BH-corrected p = .17.
- **The length-matched check agrees on equivalence:** +0.59, 90% CI [0.07, 1.11], equivalence p < .001.
  - Here the CI excludes 0. So once length is matched, the exam texts have slightly *higher* 5k coverage, by under 1.2 points.
- **Concreteness: exam texts are clearly more abstract.**
  - 2.91 vs 3.14; g = −1.18, 95% CI [−1.89, −0.65], Welch p = .00005, BH-corrected p = .0001.
  - The robustness checks agree:
    - length-matched: g = −1.25;
    - type-weighted: g = −1.14;
    - 5k coverage from the band lists only: g = 0.34, p = .22;
    - 5k coverage with proper nouns counted as known: g = 0.27, p = .32.
- **Thresholds (group means):** the exam texts reach 95% coverage at 3k and 98% at 5k. The coursebooks reach 95% at 4k and 98% at 6k.
  - Text by text: at 6k, 18 of 26 exam texts reach 98%. At 5k, 25 of 26 reach 95%; the exception is 2016-06, at 94.4%.

### The same tests on subsets of the exam texts (`results/lexical_subsets.csv`)

| Exam texts | n | 5k diff [90% CI] | Equivalent ±2 | Concreteness g [95% CI] | BH p |
|---|---|---|---|---|---|
| All | 26 | +0.41 [−0.08, 0.89] | yes | −1.18 [−1.89, −0.65] | .0001 |
| June only | 17 | +0.22 [−0.37, 0.80] | yes | −1.09 [−1.82, −0.54] | .0007 |
| Original 13 (June 2010–2022) | 13 | +0.16 [−0.51, 0.83] | yes | −1.00 [−1.75, −0.42] | .005 |

**The conclusions agree across all three subsets.** The original-13 row reproduces the published Phase 2 figures exactly, so the new proper-noun override (*hygge*) did not change them.

### June vs resit (`results/lexical_sitting.csv`; resit − June; descriptive)

- 5k coverage: +0.54 points, g = 0.45, 95% CI [−0.31, 1.24], p = .24.
- Concreteness: g = −0.04 [−0.75, 0.75], p = .91.
- No clear difference between the sittings, but with 9 resit texts the CIs are wide. The June-only results above show that pooling the sittings does not drive any conclusion.

### Token accounting (mean % of tokens, 26 exam vs 28 coursebook texts)

| | Exam | Coursebook |
|---|---|---|
| Proper nouns | 1.12 | 6.43 |
| Supplementary lists | 0.75 | 0.78 |
| Off-list | 0.25 | 0.20 |
| Excluded non-alphabetic tokens containing letters | 1.47 | 1.21 |

### Extraction notes

- **2024-09 hidden text:** the PDF carries a hidden older draft of the last paragraph (about 100 words in a different font). It was excluded; only the visible passage is used.
- **Two-column resits:** 2018-09, 2019-09 and 2020-09 are set in two columns and were read left column first.
- **2025-09 superscript:** the "th" of "10th" is kept.
- **Greg's corrections** (`data/exam_corrections.csv`): 2023-06 "schooIs" → "schools", a typo in the paper; 2019-09 "gallery-going", a spacing artefact.
- **Characters kept as printed:** quotes, dashes and the U+2010 hyphen are kept as in each PDF, because the existing exam files already mix ASCII and typographic forms.
- **Passage length:** the 13 new passages run 335–382 alphabetic tokens; the original 13 June texts are of similar length.
