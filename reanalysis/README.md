# Reanalysis (2026)

A reanalysis of the MA thesis data (Kavvadias, 2023, Hellenic Open University), comparing reading texts in the Greek state high-school English coursebooks (*English 1*, *English 2*; n = 28) with the Panhellenic English reading texts (2010–2022; n = 13).

Run every script from this folder (`cd reanalysis`).

## Data

- `data/cohmetrix_appA.csv`: Coh-Metrix 3.0 values per text, parsed from Appendix A of the thesis (`python3 parse_appA.py <thesis.pdf>`).
  - In Appendix A, CRFSOa and LSASSp are rounded to one decimal place, so results for those two indices are approximate.
  - Appendix A has a WRDPRO (pronoun) column, while Appendices B–D report WRDPOLc (polysemy), so polysemy can't be reproduced from this file.

## Scripts

| Script | What it does | Output |
|---|---|---|
| `stats1.py` | School vs exam on all 29 Coh-Metrix indices: Welch and Mann–Whitney tests, Hedges' g with bootstrap 95% CIs, Benjamini–Hochberg and Holm corrections, how much each index depends on text length | `results/group_comparisons.csv` |
| `stats2.py` | Pearson and Spearman correlations of each index with RDL2, within each group, BH-corrected | `results/corr_school.csv`, `results/corr_exam.csv` |
| `stats3.py` | English 1 vs English 2 vs exam (Kruskal–Wallis); minimum detectable effect at 80% power; 90% CI for the RDL2 difference | console |
| `features.py` | Features recomputed from the raw texts with spaCy and wordfreq: sentence length, noun and passive rates, MTLD, Flesch scores (pyphen syllables), content-word frequency, 2k/3k/5k frequency-list coverage. Includes a version of the school texts cut to their first ~360 words to match exam length | `results/own_features.csv` |
| `stats4.py` | Group tests on those features (full and length-matched texts); agreement with Coh-Metrix | console |
| `noun_split.py` | Splits Coh-Metrix WRDNOUN into common vs proper nouns and relates each to RDL2 | `results/nouns_split.csv` |

## Main findings

- **9 of the thesis's 14 significant differences survive BH correction.** Three of those are just text length (paragraph, sentence and word counts). The other six survive: the exam texts are lower in concreteness, imageability and meaningfulness, have fewer passives, longer sentences and fewer causal verbs and particles.
- **The readability formulas (FRE, FKGL, RDL2) show no difference, but the study is underpowered.** With 28 vs 13 texts, the minimum detectable effect is g ≈ 0.96. For RDL2, g = 0.29 with a 95% CI of [−0.34, 1.01], so the data can't show the groups are equivalent either.
- **The coursebooks' higher WRDNOUN comes entirely from proper nouns** (83 vs 27 per 1,000 words). The exam texts actually have slightly more common nouns.
- **The exam texts use more frequent vocabulary** (5k coverage 92.2% vs 90.2%) and this holds after length matching. Combined with the concreteness results, the exam texts are expository and abstract, while the coursebook texts are narrative.
- **The exam-group correlations in §4.7 reproduce from Appendix A.** Appendix D accidentally prints the school-text table twice.
- **English 1 and English 2 don't differ on any index.**

Caveat: coverage is calculated from wordfreq word-form lists, not BNC/COCA word families, so treat it as indicative.
