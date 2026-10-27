# Reanalysis (2026)

A reanalysis of the MA thesis data (Kavvadias, 2023, Hellenic Open University), comparing reading texts in the Greek state high-school English coursebooks (*English 1*, *English 2*; n = 28) with the Panhellenic English reading texts (2010–2022; n = 13).

Run every script from this folder (`cd reanalysis`).

## Data

- `data/cohmetrix_appA.csv`: Coh-Metrix 3.0 values per text, parsed from Appendix A of the thesis (`python3 parse_appA.py <thesis.pdf>`).
  - In Appendix A, CRFSOa and LSASSp are rounded to one decimal place, so results for those two indices are approximate.
  - Appendix A has a WRDPRO (pronoun) column, while Appendices B–D report WRDPOLc (polysemy), so polysemy can't be reproduced from this file.
- `data/bnc_coca/` and `data/brysbaert_concreteness.xlsx`: the BNC/COCA word-family lists (basewords 1.3.0) and the Brysbaert et al. (2014) concreteness norms. Both are downloaded by `python fetch_resources.py` and are not committed. Their sources, versions and citations are in `data/SOURCES.md`.
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

`corpus.py` (text loading, length-matching window) and `effects.py` (Hedges' g, bootstrap CI) are shared helpers. Tests: `python -m pytest tests`.

## Main findings

- **9 of the thesis's 14 significant differences survive BH correction.** Three of those are just text length (paragraph, sentence and word counts). The other six survive: the exam texts are lower in concreteness, imageability and meaningfulness, have fewer passives, longer sentences and fewer causal verbs and particles.
- **The readability formulas (FRE, FKGL, RDL2) show no difference, but the study is underpowered.** With 28 vs 13 texts, the minimum detectable effect is g ≈ 0.96. For RDL2, g = 0.29 with a 95% CI of [−0.34, 1.01], so the data can't show the groups are equivalent either.
- **The coursebooks' higher WRDNOUN comes entirely from proper nouns** (83 vs 27 per 1,000 words). The exam texts actually have slightly more common nouns.
- **The exam texts use more frequent vocabulary** (5k coverage 92.2% vs 90.2%) and this holds after length matching. Combined with the concreteness results, the exam texts are expository and abstract, while the coursebook texts are narrative.
- **The exam-group correlations in §4.7 reproduce from Appendix A.** Appendix D accidentally prints the school-text table twice.
- **English 1 and English 2 don't differ on any index.**

Caveat: coverage is calculated from wordfreq word-form lists, not BNC/COCA word families, so treat it as indicative. Phase 2 (below) replaces it.

## Phase 2: lexical measures

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
  - So by word frequency, the exam vocabulary is no harder than the coursebook vocabulary.
- **This replaces the Phase 1 finding that the exam texts use more frequent vocabulary.** Measured by word families, with proper nouns left out of the count, that difference disappears.
- **Thresholds (mean coverage):** the exam texts reach 95% at the 3k level and 98% at 6k (97.96% at 5k). The coursebook texts reach 95% at 4k and 98% at 6k. So a reader who knows about 6,000 word families would meet the 98% threshold in either group.
- **Concreteness: the exam texts use more abstract vocabulary.**
  - Mean Brysbaert concreteness of content words is 2.92 for the exam texts and 3.14 for the coursebooks: g = −1.00, 95% CI [−1.75, −0.42], Welch p = .003, BH-corrected p = .005.
  - This confirms the Phase 1 Coh-Metrix concreteness result with a measure anyone can reproduce.
  - The norms cover at least 95% of the content words in every text.
- **The robustness checks all agree:**
  - length-matched concreteness: g = −1.06, p = .001;
  - type-weighted concreteness: g = −1.05, p = .0004;
  - 5k coverage from the band lists only, without the supplementary lists: g = 0.13, p = .71;
  - 5k coverage with proper nouns counted as known: g = 0.04, p = .92.
- **Caveats:**
  - **Proper nouns:** they are identified from Nation's proper-noun list (list 31) plus spaCy's PROPN tag. A word on a frequency-band list is never treated as a proper noun.
    - Greg reviewed all 404 detected types. 15 foreign or ordinary words were reclassified as common (`data/propn_overrides.csv`); 24 tokens changed category.
  - **List 35:** accented spellings are counted as known, like the other supplementary lists. This was Claude's call.
  - **Concreteness:** word-level ratings capture only part of what makes the exam texts abstract. Their topics and the way they argue are left for the genre analysis (Phase 4b).
  - **Ceiling effect:** word-family coverage is near the ceiling for every text (5k range 94.4–100%). It correlates only weakly with the Phase 1 word-form coverage (ρ = .35, before the proper-noun review).

**Scope rationale (draft for the paper's methods):** Lexical difficulty was operationalised with two well-established, openly available resources that answer the research question directly. The first is text coverage by BNC/COCA word-family frequency bands (Nation, 2017), which links directly to established comprehension thresholds (Hu & Nation, 2000; Laufer & Ravenhorst-Kalovski, 2010). The second is word concreteness ratings (Brysbaert et al., 2014). Broader multi-index tools (e.g. TAALES) were not used, because with 41 texts, adding many correlated indices would raise the multiple-comparison burden without sharpening the test of the central claim.
