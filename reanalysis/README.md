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
- `data/exam_approvals.csv`: Greg's approval of each new passage, with the SHA-256 hash of the approved content. `promote_exams.py` refuses any file that has changed since approval.
- `staging/Panhellenics/`: the extracted passages before promotion; `results/exam_review.md` is the review report Greg checked.
- `data/genre_labels.csv`: the genre of each text, with a fine label, a coarse narrative/non-narrative group and a reason. Claude proposed each label; Greg confirmed or changed it (frozen in commit 4ce01fc).
- `data/excluded_texts.csv`: texts left out of every analysis from Phase 3 part 2 on. Currently English 2 unit-4-1, a formatting exercise.
- `data/heading_lines.csv`: the title and subheading lines that the sentence-based measures skip.
- `data/glasgow_norms.csv`, `data/taaco/`: the Glasgow Norms and TAACO's connective lists, downloaded by `fetch_resources.py` and not committed. Word vectors come from spaCy's `en_core_web_md` 3.8.0.
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

| `extract_exams.py` | Downloads the new exam papers and extracts the main reading passage from page 2. Only the text visible on the page is kept. Words in another font, such as a hidden text layer, are excluded and reported. Lines that overlap vertically, a sign of hidden text in the body font, are also reported for removal by correction. Two-column papers are read left column first. Paragraphs are rebuilt from the layout, and Greg's corrections are applied. Writes the review report | `staging/Panhellenics/`, `results/exam_review.md`, `data/EXAM_SOURCES.md` |
| `promote_exams.py` | Copies approved passages into `Texts/Panhellenics/`. It refuses to overwrite a file that differs | `Texts/Panhellenics/` |

`stats5.py` also writes `results/lexical_subsets.csv` (the primary tests for all 26 exam texts, June-only and the original 13) and `results/lexical_sitting.csv` (June vs resit).

| `difficulty.py` | Phase 3 part 2: open difficulty measures for each text (vocabulary, syntax, cohesion, readability; definitions below) | `results/difficulty_features.csv` |
| `stats6.py` | The difficulty table: four primary tests in one BH family, robustness checks, descriptive effect sizes, and validation against the thesis Coh-Metrix values | `results/difficulty_comparisons.csv`, `results/difficulty_validation.csv` |

| `separation.py` | Phase 4 RQ2 (a): elastic-net logistic regression separating exam from coursebook texts on 21 open measures; nested leave-one-out CV and a 200-run permutation test (scikit-learn 1.9.1) | `results/separation_summary.csv`, `results/separation_features.csv` |
| `genre.py` | Phase 4 RQ2 (b): genre composition, Fisher test, within-genre comparison and regression check | `results/genre_*.csv` |

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
  - Exam 98.20%, coursebooks 97.80%: a difference of +0.40, 90% CI [−0.08, 0.89].
  - Equivalence test: p < .001 for both one-sided tests (Welch df = 48.4).
  - Difference test: g = 0.38, 95% CI [−0.15, 1.05], Welch p = .17, BH-corrected p = .17.
- **The length-matched check agrees on equivalence:** +0.59, 90% CI [0.07, 1.11], equivalence p < .001.
  - Here the CI excludes 0. So once length is matched, the exam texts have slightly *higher* 5k coverage, by under 1.2 points.
- **Concreteness: exam texts are clearly more abstract.**
  - 2.91 vs 3.14; g = −1.19, 95% CI [−1.90, −0.67], Welch p = .00005, BH-corrected p = .0001.
  - The robustness checks agree:
    - length-matched: g = −1.26;
    - type-weighted: g = −1.15;
    - 5k coverage from the band lists only: g = 0.34, p = .21;
    - 5k coverage with proper nouns counted as known: g = 0.27, p = .32.
- **Thresholds (group means):** the exam texts reach 95% coverage at 3k and 98% at 5k. The coursebooks reach 95% at 4k and 98% at 6k.
  - Text by text: at 6k, 18 of 26 exam texts reach 98%. At 5k, 25 of 26 reach 95%; the exception is 2016-06, at 94.4%.

### The same tests on subsets of the exam texts (`results/lexical_subsets.csv`)

| Exam texts | n | 5k diff [90% CI] | Equivalent ±2 | Concreteness g [95% CI] | BH p |
|---|---|---|---|---|---|
| All | 26 | +0.40 [−0.08, 0.89] | yes | −1.19 [−1.90, −0.67] | .0001 |
| June only | 17 | +0.22 [−0.37, 0.80] | yes | −1.09 [−1.82, −0.54] | .0007 |
| Original 13 (June 2010–2022) | 13 | +0.16 [−0.51, 0.83] | yes | −1.00 [−1.75, −0.42] | .005 |

**The conclusions agree across all three subsets.** The original-13 row reproduces the published Phase 2 figures exactly, so the new proper-noun override (*hygge*) did not change them.

### June vs resit (`results/lexical_sitting.csv`; resit − June; descriptive)

- 5k coverage: +0.54 points, g = 0.45, 95% CI [−0.32, 1.24], p = .25.
- Concreteness: g = −0.08 [−0.79, 0.71], p = .82.
- No clear difference between the sittings, but with 9 resit texts the CIs are wide. The June-only results above show that pooling the sittings does not drive any conclusion.

### Token accounting (mean % of tokens, 26 exam vs 28 coursebook texts)

| | Exam | Coursebook |
|---|---|---|
| Proper nouns | 1.12 | 6.43 |
| Supplementary lists | 0.74 | 0.78 |
| Off-list | 0.25 | 0.20 |
| Excluded non-alphabetic tokens containing letters | 1.54 | 1.21 |

### Extraction notes

- **2024-09 hidden text:** the PDF carries two hidden layers, and both are excluded.
  - An older draft of the last paragraph, about 100 words in a different font, removed by the font filter.
  - A fragment of the 2023-09 passage in the body font (*"u to look at the world — one not mediated through a screen…"*). The extractor reports it as overlapping lines, and it is removed by a recorded correction after a visual check. The final code review caught it after the first promotion; the corrected file was re-approved.
- **Two-column resits:** 2018-09, 2019-09 and 2020-09 are set in two columns and were read left column first.
- **2025-09 superscript:** the "th" of "10th" is kept.
- **Corrections** (`data/exam_corrections.csv`): 2023-06 "schooIs" → "schools", a typo in the paper; and the 2024-09 hidden fragment.
- **Words split by a font change:** where a word is split at a U+2010 hyphen set in another font, the pieces are joined without a space ("mid‐winter", "gallery‐going").
- **Characters kept as printed:** quotes, dashes and the U+2010 hyphen are kept as in each PDF, because the existing exam files already mix ASCII and typographic forms.
- **Passage length:** the 13 new passages run 335–382 alphabetic tokens; the original 13 June texts run 308–376.

## Phase 3 part 2: definitions (frozen before any corpus run)

The design is in `docs/superpowers/specs/2026-10-27-phase3-open-measures-design.md`. These definitions were committed before `difficulty.py` was run on any corpus text.

After the freeze, a rule may change only to fix a bug, meaning the code does not do what is written here. Every such change is listed under "Post-freeze changes" with its before and after values.

### Corpus and text versions

- **Corpus:** 27 coursebook texts and 26 exam texts. English 2 unit-4-1 is excluded as a formatting exercise (`data/excluded_texts.csv`). `**` markdown is removed from every text.
- **Two text versions:**
  - **Vocabulary measures** use the full text.
  - **Syntax, cohesion and readability measures** use the *heading-free* text: the title and subheading lines in `data/heading_lines.csv` (16 lines in 10 coursebook files) are removed first, because headings parse as sentences and noun phrases.
- **Length-matched version (`first360`):** whole sentences from the start of the heading-free text until at least 360 alphabetic tokens. All measures are recomputed on it.
- **Parser:** spaCy `en_core_web_sm` 3.8.0. Sentences are spaCy sentences containing at least one alphabetic token.
- **Content tokens:** alphabetic tokens tagged NOUN, VERB, ADJ or ADV that `lexical.classify` does not mark as proper nouns. That means Nation's proper-noun list (list 31) plus `data/propn_overrides.csv`, as in Phase 2.

### Measures (`results/difficulty_features.csv`)

**Vocabulary**

| Column | Definition |
|---|---|
| `imag`, `fam` | Token-weighted mean Glasgow Norms imageability and familiarity (1–7) of content tokens, matched by lower-cased lemma. Sense-tagged and multiword norm entries are ignored. |
| `imag_cov`, `fam_cov` | Percent of content tokens matched in the norms. |
| `mtld`, `hdd` | MTLD and HD-D (`lexical-diversity` package) on lower-cased alphabetic tokens. HD-D stands in for VOCD-D. |

**Syntax**

| Column | Definition |
|---|---|
| `n_clauses` | Count of finite-clause heads (see below). |
| `mlc` | Alphabetic tokens ÷ finite clauses; NaN if there are no clauses. **Primary.** |
| `clauses_per_sent`, `mean_sent_len` | Clauses ÷ sentences; alphabetic tokens ÷ sentences. |
| `passive_inc` | `auxpass` dependencies. |
| `np_inc` | spaCy noun chunks. |
| `vp_inc` | Tokens tagged VERB. |
| `adjp_inc` | Tokens tagged ADJ. |
| `pp_inc` | `prep` dependencies. |
| `neg_inc` | `neg` dependencies. |
| `gerund_inc` | VBG tokens without an `aux` child. |
| `inf_inc` | TO tokens whose head is tagged VB. |

All incidences (`_inc`) are per 1,000 alphabetic tokens.

A token is a **finite-clause head** if all three conditions hold:
1. It is a verb or auxiliary.
2. Its dependency is `ROOT`, `ccomp`, `advcl`, `relcl`, `csubj` or `acl`, or it is a `conj` with its own `nsubj`/`nsubjpass`.
3. It is finite: its tag, or the tag of one of its `aux`/`auxpass` children, is VBD, VBP, VBZ or MD. An imperative `ROOT` verb (tag VB) also counts.

This follows Lu's (2010) clause definition as closely as the parser allows.

**Cohesion**

| Column | Definition |
|---|---|
| `cwo_adj` | For each pair of adjacent sentences A and B: the content tokens of A and B whose lower-cased lemma occurs in both sentences, divided by all content tokens of A and B. The text score is the mean over pairs. Pairs where either sentence has no content token are skipped. **Primary.** |
| `cwo_skipped` | Percent of adjacent pairs skipped in `cwo_adj`. |
| `sem_overlap`, `sem_skipped` | Cosine between the mean `en_core_web_md` 3.8.0 vectors of adjacent sentences' content lemmas. Lemmas without a vector are ignored, and pairs without a vector on either side are skipped. Replaces LSA. |
| `conn_inc` | Connectives per 1,000 alphabetic tokens: TAACO's `all_connective`, `all_connective_ngram` and `basic_connectives` lists, matched on lower-cased words. Multiword items are matched first, longest first, without overlap. |
| `causal_inc` | The same for TAACO's `all_causal` list. |

TAACO's "caveat" items (*since*, *after*, *before*, …), which need context to decide, are not counted.

**Readability**

| Column | Definition |
|---|---|
| `fre`, `fkgl` | Flesch Reading Ease and Flesch–Kincaid Grade Level, with the `features.py` formulas and the pyphen syllable counter. |

### Post-freeze changes

None. No rule changed after the freeze commit (528abe9).

### Results: the difficulty table (27 coursebook vs 26 exam texts)

**What changed in the corpus**
- English 2 unit-4-1 is excluded from here on, so `results/lexical_features.csv` now holds 27 coursebook texts.
- The Phase 2 and Phase 3 part 1 figures above were computed with 28 coursebook texts. They remain as published in git history (commits `ee0280e` and `e9fbaab`), and rerunning `stats5.py` now gives the 27-text versions.
- The Phase 1 Coh-Metrix analyses are unchanged and keep all 28 texts.

**Primary tests** (one BH family of four; Welch tests; exam − school)

| Dimension | Measure | Coursebook | Exam | g [95% CI] | p | BH p |
|---|---|---|---|---|---|---|
| Vocabulary | 5k coverage (%) | 97.86 | 98.20 | 0.33 [−0.21, 0.98] | .24 | .31 |
| Vocabulary | Concreteness (1–5) | 3.13 | 2.91 | −1.15 [−1.85, −0.62] | .0001 | .0004 |
| Syntax | Mean length of clause (words) | 11.39 | 10.27 | −0.55 [−1.15, −0.05] | .045 | .09 |
| Cohesion | Content-word overlap, adjacent sentences | 0.061 | 0.069 | 0.21 [−0.26, 1.17] | .45 | .45 |

- **5k coverage:** still equivalent within ±2 points. The difference is +0.35, 90% CI [−0.14, 0.83], equivalence p < .001.
- **Concreteness:** the only primary difference that survives correction. The exam texts are more abstract.
- **Clause length:** the exam texts have *shorter* clauses (g = −0.55), significant before correction but not after (BH p = .09).
  - The direction holds in every robustness check: length-matched g = −0.67, p = .017; June-only g = −0.58, p = .057; original 13 g = −0.65, p = .053.
  - So the exam texts are not syntactically harder by this measure. If anything, their clauses are shorter.
- **Content-word overlap:** no difference by the pre-specified Welch test.
  - The Mann–Whitney test gives p = .029, slightly higher overlap in the exam texts by rank.
  - **Why the two tests disagree:** one coursebook outlier, English 2 unit-6-1 ("I Have A Dream", whose "Let freedom ring…" repetition gives `cwo_adj` = 0.268). The coursebook median is 0.049 and the exam maximum 0.124. The outlier inflates the coursebook variance and skews the g CI, so the Welch test misses the rank shift.
  - The pre-specified Welch test stands. This is reported, not used to change the primary result.
  - The robustness rows agree with Welch: length-matched g = 0.18, p = .51; June-only g = 0.11, p = .70; original 13 g = 0.24, p = .41.

**Descriptive measures** (Hedges' g, exam − school, 95% CI; not tested)
- **Vocabulary:**
  - imageability −1.19 [−1.87, −0.65];
  - familiarity 0.74 [0.27, 1.26];
  - MTLD 0.74 [0.26, 1.28];
  - HD-D 0.89 [0.43, 1.44].
  - The exam vocabulary is less imageable but more varied, and slightly more familiar.
- **Syntax:**
  - clauses per sentence 0.97 [0.46, 1.62];
  - sentence length 0.41 [−0.12, 0.99];
  - passives −1.17 [−1.74, −0.75];
  - prepositional phrases −0.53 [−1.08, −0.02];
  - adjectives 0.66 [0.14, 1.25];
  - negation 0.53 [0.01, 1.14].
  - The exam sentences hold more, shorter clauses, with fewer passives.
- **Cohesion:**
  - semantic overlap 1.21 [0.70, 1.95];
  - connectives 0.60 [0.07, 1.25];
  - causal connectives 0.46 [−0.06, 1.03].
- **Readability:**
  - Flesch Reading Ease −0.38 [−0.85, 0.14];
  - Flesch–Kincaid 0.44 [−0.06, 0.95].

**Validation against Coh-Metrix** (Spearman ρ with 95% CI over the 40 original texts; pooled, and within the 27 coursebook and 13 exam texts)

Pooled ρ partly reflects the difference between the groups, so the within-group columns are the stricter test. CIs use the Fisher z transformation with SE = 1/√(n − 3), which is slightly narrow for Spearman ρ at n = 13.

| New measure | Coh-Metrix | Pooled | Coursebook | Exam |
|---|---|---|---|---|
| Concreteness (primary) | WRDCNCc | .90 [.81, .94] | .85 [.70, .93] | .92 [.76, .98] |
| Content-word overlap (primary) | CRFSOa | .52 [.25, .72] | .38 [.00, .67] | .89 [.67, .97] |
| Imageability | WRDIMGc | .87 [.77, .93] | .78 [.57, .89] | .87 [.62, .96] |
| HD-D | LDVOCD | .98 [.96, .99] | .96 [.92, .98] | .91 [.71, .97] |
| Sentence length | DESSL | .91 [.83, .95] | .88 [.74, .94] | .89 [.68, .97] |
| Passives | DRPVAL | .95 [.91, .97] | .97 [.94, .99] | .82 [.48, .94] |
| Prepositional phrases | DRPP | .97 [.94, .98] | .96 [.91, .98] | .98 [.93, .99] |
| Infinitives | DRINF | .97 [.94, .98] | .95 [.89, .98] | .96 [.88, .99] |
| Gerunds | DRGERUND | .84 [.71, .91] | .82 [.64, .92] | .86 [.59, .96] |
| Negation | DRNEG | .79 [.64, .88] | .68 [.40, .84] | .89 [.66, .97] |
| Verb phrases | DRVP | .70 [.50, .83] | .75 [.51, .88] | .51 [−.06, .83] |
| Noun phrases | DRNP | .51 [.24, .71] | .54 [.20, .76] | .31 [−.29, .73] |
| Connectives | CNCAll | .85 [.73, .92] | .82 [.64, .92] | .93 [.79, .98] |
| Causal connectives | SMCAUSvp | .15 [−.16, .44] | .23 [−.16, .56] | .63 [.12, .88] |
| Semantic overlap | LSASSp | .12 [−.19, .42] | .26 [−.14, .58] | .25 [−.35, .70] |
| Adjectives | DRAP | −.24 [−.51, .08] | −.32 [−.62, .07] | −.15 [−.65, .44] |
| Flesch Reading Ease | RDFRE | .93 [.87, .96] | .93 [.85, .97] | .94 [.81, .98] |
| Flesch–Kincaid | RDFKGL | .92 [.85, .96] | .89 [.76, .95] | .92 [.74, .97] |

- **Not validated:** mean length of clause (a primary measure), clauses per sentence, MTLD and familiarity have no counterpart among the thesis's Coh-Metrix indices. MLC follows Lu's (2010) L2SCA definition instead.
- **Content-word overlap agrees well only within the exam texts** (ρ = .89). Within the coursebooks, agreement is weak (ρ = .38, CI reaching 0). The two indices differ by design: CRFSOa is binary stem overlap across all sentence pairs, `cwo_adj` is proportional lemma overlap between adjacent sentences. The paper should present `cwo_adj` as following CRFCWO1, not as a reproduction of the thesis index.
- **Clause rule limitations:** a check of all 1,431 sentences found the rule misses about 1% of finite clauses. These are wh-clauses inside prepositional phrases ("than where we were before"), parenthetical clauses ("it seems"), conjuncts whose only subject is expletive "there", and a few past-tense verbs mis-tagged by the parser. The misses are spread across both groups. 51 sentences have no finite clause at all (0.75% of coursebook tokens, 0.55% of exam tokens). This is a limitation to state in the paper; the rule stays as frozen.

- **Weakly agreeing measures don't measure what Coh-Metrix did.**
  - Our adjective count is not Coh-Metrix's adjective-phrase density.
  - TAACO's causal list differs from Coh-Metrix's causal verbs and particles.
  - Word-vector similarity is not LSA.
- **None of them is a primary measure.** In the paper they should be described as related open measures, not replacements.
- **Glasgow coverage:** the norms cover on average 59% (coursebooks) and 54% (exam) of content tokens, so imageability and familiarity rest on about half of each text's content words.
- **Skipped pairs:** under 1% of adjacent sentence pairs are skipped on average for the overlap measures (maximum 17% in one text).

**Scope paragraph for the paper (draft, replaces the Phase 2 draft):** Text difficulty was measured along four dimensions identified in the readability literature: vocabulary, syntax, cohesion (Graesser, McNamara & Kulikowich, 2011; Crossley, Greenfield & McNamara, 2008) and, for reference, classic readability formulas. Each dimension used open, reproducible measures computed on all texts. One or two measures per dimension were pre-specified as primary, giving four tests in a single Benjamini–Hochberg family: word-family coverage (Nation, 2017), concreteness (Brysbaert et al., 2014), mean length of clause (Lu, 2010), and adjacent-sentence content-word overlap. All other measures are reported descriptively with effect sizes. Where the thesis reported a corresponding Coh-Metrix index, the rebuilt measure was validated against it on the original texts, pooled and within each group. Mean length of clause has no Coh-Metrix counterpart and follows the L2SCA definition.

## Phase 4: RQ2 (what distinguishes the exam texts, and does genre account for it?)

The design is in `docs/superpowers/specs/2026-10-29-phase4-rq2-design.md`. This RQ2 replaces the thesis's circular question about which features correlate with RDL2. The corpus is 27 coursebook and 26 exam texts.

### (a) What separates the two groups

**Model:** an elastic-net logistic regression on 21 open measures (the Phase 3 part 2 measures minus the Flesch formulas).
- **Validation:** nested cross-validation. The outer loop is leave-one-out. The inner loop is stratified 5-fold over C ∈ {0.01 … 100} (9 log-spaced values) and L1 ratio ∈ {0.1, 0.5, 0.9}.
- **Chance check:** the AUC is compared with 200 label permutations, each rerunning the whole nested procedure.

| Coursebook version | Accuracy | Balanced accuracy | AUC | Permutation p |
|---|---|---|---|---|
| Full texts | .70 | .70 | .78 | .005 |
| Length-matched (first ~360 words) | .74 | .74 | .80 | .005 |

- **The two groups are reliably distinguishable from these measures.** No permuted run reached the observed AUC; .005 is the smallest possible p with 200 permutations.
- **The separation is clear but far from perfect.** About 3 in 10 texts are misclassified, so the groups overlap.
- **The AUC is probably conservative:** a pooled leave-one-out AUC tends to be biased downward. The permutation p is unaffected, because the null runs are built the same way.

**Which measures matter.** The inner CV chose a mostly ridge-like penalty (L1 ratio 0.1, C = 0.1) in both final fits. That keeps nearly every measure: 15 of 21 (full) and 17 of 21 (length-matched) pass the pre-specified rule of being selected in at least 80% of folds. **So the selection rule singles out little, and coefficient size is more informative.**

| Version | Largest standardised coefficients (+ = more typical of exam texts) | Never or rarely selected |
|---|---|---|
| Full texts | passives −0.28, semantic overlap +0.27, imageability −0.25, clauses per sentence +0.24, HD-D +0.23, concreteness −0.18 | mean sentence length, noun phrases, infinitives, prepositional phrases (≤ 19% of folds) |
| Length-matched | semantic overlap +0.29, imageability −0.26, HD-D +0.25, clauses per sentence +0.24, passives −0.22, connectives +0.21 | mean sentence length, noun phrases (≤ 19% of folds) |

The exam texts are marked by:
- **abstract vocabulary:** lower imageability and concreteness, higher lexical diversity. Familiarity runs the other way (+0.17; univariate g = +0.74): the exam texts' words are abstract but slightly *more* familiar;
- **more, shorter clauses per sentence;**
- **fewer passives;**
- **more semantic overlap and more connectives between sentences.**

Mean sentence length adds nothing once clauses per sentence and clause length are in the model (it correlates .61 with clauses per sentence). That does not make it irrelevant on its own: its univariate g is +0.41 [−0.12, 0.99]. All of these are associations within a penalised model, not causes.

### (b) Genre

**Composition** (`results/genre_composition.csv`)

| Fine label | Coursebook | Exam |
|---|---|---|
| Informational | 7 | 17 |
| Argumentative | 2 | 9 |
| Biography | 7 | 0 |
| Fiction | 3 | 0 |
| Speech | 3 | 0 |
| Review | 3 | 0 |
| Other (narrative: a plot retelling, a historical recount) | 2 | 0 |

- **Coarse:** 12 of 27 coursebook texts are narrative, against **0 of 26** exam texts.
- **Fisher's exact test:** p = .0001. The odds ratio compares the odds of a text being narrative in the coursebooks with the odds in the exam papers. It is infinite because of the zero cell; its exact 95% CI is [3.95, ∞].
- **One departure from the coding rule:** the spec codes reviews and plot summaries as non-narrative (`review`). Greg recoded English 1 unit-7-2, a chapter-by-chapter plot retelling, as narrative (`other`), and also English 2 unit-8-6, a historical recount.

**Within-genre comparison** (non-narrative texts only: 15 coursebook vs 26 exam; BH over the two pre-specified measures)

| Measure | Coursebook | Exam | g [95% CI], non-narrative only | BH p | g [95% CI], all texts (Phase 3 part 2) |
|---|---|---|---|---|---|
| Concreteness | 3.10 | 2.91 | −0.96 [−1.88, −0.28] | .017 | −1.15 [−1.85, −0.62] |
| Passives per 1,000 words | 15.4 | 7.5 | −1.31 [−2.08, −0.73] | .004 | −1.17 [−1.74, −0.75] |

**Regression check** (OLS on all texts, with and without coarse genre)
- **Concreteness:** the exam coefficient shrinks by 16% when genre is added (−0.22 → −0.19; 95% CI [−0.31, −0.06]).
- **Passives:** it shrinks by 4% (−8.2 → −7.9; [−12.4, −3.3]).
- **This restates the within-genre comparison; it is not separate evidence.** No exam text is narrative, so the genre-adjusted exam coefficient equals the non-narrative mean difference exactly (−0.187 and −7.87). The check shows the same result on the raw scale.

**What genre does and does not explain**
- **Genre composition differs sharply.** Narrative texts (fiction, biography, plot retellings) appear only in the coursebooks.
- **But genre is not what makes the exam texts different.** Comparing only non-narrative texts, the exam texts are still clearly more abstract and use far fewer passives. The gaps are about as large as in the full comparison: removing the narrative texts shrinks them by at most a sixth.
- **So the coursebooks' non-narrative texts are themselves more concrete and more passive-heavy** than the exam texts. The mismatch lies in *which* non-narrative texts the coursebooks contain, not only in how many narratives they include.
- **It holds within matching genres too** (descriptive):
  - coursebook informational 3.15 vs exam 2.95 (concreteness), 15.3 vs 8.6 (passives);
  - argumentative 3.12 vs 2.83 and 14.3 vs 5.5.
- **One caveat:** the coursebooks' non-narrative group includes speeches and reviews, which have no exam counterpart. The three speeches are as abstract as the exam texts (2.94) but use the most passives (16.4).

### Limitations

- **Single human coder for genre:** Claude proposed the labels and Greg confirmed them. A blind second coder on a subset could be added for a reliability statistic.
- **200 permutations, not the spec's default of 1,000:** in parallel, 200 took 22 min (full) and 17 min (length-matched), so 1,000 would take about 3.3 hours. No permuted run reached the observed AUC, so p sits at the floor of .005 for 200 runs. More runs would only lower the floor, not change the conclusion. The 1,000-run version can be run if a reviewer asks.
- **The yearly score statistics (2019–2026) were not analysed.** They cover the whole paper, not the reading task. At most they support a descriptive remark in the discussion.
