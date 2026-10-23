# Phase 2 (lexical): frequency-band coverage and concreteness norms

**Date:** 2026-10-23
**Branch:** `phase2-lexical`
**Context:** `HANDOFF.md` §4 Phase 2, items 1–2 and 6. The Phase 1 results are summarised in `reanalysis/README.md`.

## 1. Intent

The paper needs a defensible claim about vocabulary difficulty in the Panhellenic exam texts compared with the state coursebook texts. Greg's target claim is that **the exam vocabulary is roughly as difficult as the coursebook vocabulary.** Phase 1 suggests a more nuanced version:

- by frequency, the exam vocabulary is similar or slightly easier (wordfreq 5k coverage 92.2% vs 90.2%);
- the exam texts are more abstract (Coh-Metrix concreteness g = −1.16).

Phase 2 replaces the two indicative measures from Phase 1 with standard, reproducible ones, so that both halves of that claim can withstand review:

1. **Coverage by frequency band**, from Nation's BNC/COCA word-family lists. This replaces the wordfreq coverage.
2. **Concreteness of content words**, from the Brysbaert, Warriner & Kuperman (2014) norms. This replaces Coh-Metrix WRDCNCc.

Greg's view is that what makes the exam texts feel abstract is **their topics and the way their ideas are argued**, more than the individual words. Word-level concreteness is therefore only partial evidence. The fuller claim waits for the genre analysis in Phase 4(b). The write-up must say this.

## 2. Goals

- G1. Measure per-text coverage at cumulative band levels 1k–9k, plus off-list words, using BNC/COCA word families.
- G2. Run an **equivalence test (TOST)** of exam vs coursebook coverage at the **5k level**, with a margin of **±2 percentage points**.
  - The margin was agreed with Greg. It is justified by the gap between the 95% (minimal) and 98% (optimal) coverage thresholds (Laufer & Ravenhorst-Kalovski 2010; Hu & Nation 2000; Nation 2006).
  - 5k is the primary, pre-specified comparison. The other bands are descriptive only.
- G3. Report each group's coverage at each band level against the 95% and 98% thresholds. Also report, for each group, the lowest band level at which mean coverage reaches 95% and 98% (or "not reached by 9k").
- G4. Compute mean Brysbaert concreteness of content-word lemmas per text and compare the groups with an ordinary difference test, since a difference is expected.
- G5. Report how much of each text the measures actually cover: the share of tokens on the band lists, and the share of content lemmas found in the concreteness norms. Gaps in the resources must not be able to drive a result unnoticed.
- G6. Use the Phase 1 statistics for all comparisons: Welch t and Mann–Whitney, Hedges' g with 95% bootstrap CIs, and BH correction across the family of difference tests. Repeat everything on the length-matched version (coursebook texts cut to their first ~360 words).
- G7. Add the findings to `reanalysis/README.md`, each with its effect size and corrected p-value, plus a short **scope rationale paragraph** that can go into the paper's methods (see §6).

## 3. Non-goals (deferred to later phases, deliberately)

- TAALES, TAASSC, TAACO, CAREC or transformer readability models, and CEFR (EVP / CEFR-J) profiling. These don't feed the vocabulary claim, and each adds tooling and interpretation cost. The paper defends this narrow scope (§6).
- Genre classification (Phase 4b) and the corpus extension to 2023–2026 (Phase 3).
- Changes to the Phase 1 Coh-Metrix analyses.

## 4. Anti-goals (would count as failure even if the code works)

- Claiming the groups are "similar" or "equivalent" from a non-significant difference test. Similarity may be claimed **only** if the 90% CI of the 5k coverage difference lies within ±2 points, as TOST requires.
- Moving the primary band or the margin after seeing the results. If another band tells a different story, report it as descriptive.
- Silent loss of tokens. Every token is counted as on-list, off-list, proper noun or excluded (numbers, punctuation), and the shares are reported.
- Reporting concreteness without saying what share of content words the norms cover.

## 5. Decisions

### Decided by Greg
- The claim being tested is approximate similarity of vocabulary difficulty.
- The equivalence margin is ±2 percentage points of coverage.
- The primary comparison is the 5k band, set before any results are seen (proposed by Claude, accepted by Greg).
- Phase 2 is limited to frequency bands and concreteness, and the paper must defend that scope.

### Claude's calls (Greg can override)
- **Proper nouns count as known.** They are left out of both the numerator and the denominator of coverage, which is the standard treatment in coverage studies. Coverage with proper nouns counted as known (i.e. included in the numerator) is also reported, as a sensitivity check.
- **How tokens are matched to word families:**
  - Each token's lower-cased word form is looked up in a form→family index built from the BNC/COCA lists (the 2017 release of Nation's 25k lists plus their supplementary lists).
  - If the form isn't there, the spaCy lemma is tried.
  - Tokens found in neither are off-list.
- **Proper-noun rule:**
  - A token is a proper noun if (a) its form is on the BNC/COCA proper-noun supplementary list, or (b) spaCy tags it `PROPN` **and** its lower-cased form is not on any base band list.
  - A token tagged `PROPN` whose form *is* on a band list (e.g. "English", "May", "China" if listed) is classified by the band list, not as a proper noun. Proper nouns hit the two groups unevenly (83 vs 27 per 1,000 words), and this keeps that imbalance from shifting the coverage baseline.
  - The script writes `results/propn_types.csv`, listing every type the rule classifies as a proper noun, with its counts per group, so the rule can be audited.
  - **Manual review (decided by Greg: yes):**
    - Greg reviews `propn_types.csv` and marks any misclassified types.
    - His corrections go in `data/propn_overrides.csv` (type → `proper` / `common`, committed), which the script applies.
    - Coverage results count as final only after this review.
    - The pipeline must run end to end without the overrides file, so that the review can happen after a first run.
- **Supplementary lists (marginal words, transparent compounds, abbreviations) count as known at every band level.** For example, "5k coverage" means bands 1–5 plus the supplementary lists. This is the convention in Nation's coverage studies. The supplementary share is reported as its own column, and 5k coverage with bands 1–5 only is reported as a sensitivity check.
- **Resources are not committed.** Their redistribution licences are unclear, so `reanalysis/fetch_resources.py` downloads Nation's lists and the Brysbaert norms into `reanalysis/data/` (gitignored). `data/SOURCES.md` records each URL, version and citation, and the open-data statement points to the fetch script.
- **Concreteness:**
  - Content words are tokens tagged NOUN, VERB, ADJ or ADV, excluding PROPN, matched by lemma to the Brysbaert norms (1–5 scale).
  - The score is a token-weighted mean per text.
  - A type-weighted mean is also reported as a sensitivity check.
  - Auxiliaries (spaCy `AUX`) are excluded.
- **Correction family:**
  - BH correction is applied to **Welch** p-values, matching Hedges' g. Mann–Whitney p-values are reported alongside, uncorrected, as a robustness check.
  - The family is the two primary tests: 5k coverage and token-weighted concreteness, on the primary text version.
  - The length-matched and type-weighted results are robustness checks, reported with uncorrected p-values and labelled as such.
- **TOST:** two one-sided Welch tests with the Welch–Satterthwaite df. Equivalence is declared if the 90% CI of the difference lies within ±2 points. Both one-sided p-values are reported, outside the BH family.
- **Primary text version: full texts** (Greg accepted Claude's recommendation).
  - **Reasons:**
    - The research question concerns the input students actually receive.
    - Token coverage is a proportion and depends little on length.
    - Cutting to the first ~360 words over-samples text openings, which are denser in names and setting-up vocabulary.
  - The length-matched version is the robustness check.
  - **Rule:** if the length-matched result disagrees with the full-text result (e.g. TOST passes on full texts but fails on length-matched texts), the paper reports the disagreement and does not state the equivalence claim without qualification.

## 6. Scope rationale for the paper (draft text, to refine during writing)

> Lexical difficulty was operationalised with two well-established, openly available resources that answer the research question directly: text coverage by BNC/COCA word-family frequency bands (Nation, 2017), which links directly to established comprehension thresholds (Hu & Nation, 2000; Laufer & Ravenhorst-Kalovski, 2010), and word concreteness ratings (Brysbaert et al., 2014). Broader multi-index tools (e.g. TAALES) were not used, because with 41 texts adding many correlated indices would raise the multiple-comparison burden without sharpening the test of the central claim.

## 7. Constraints

- Run the scripts from `reanalysis/`, with relative paths. Downloaded resources go in `reanalysis/data/` and outputs go in `reanalysis/results/`.
- **Windows path bug:** `features.py` gets the book name with `f.split('/')`, which may fail on Windows. New code uses `os.path` / `pathlib`.
- Downloaded resources: record the source URL, version or date, and citation in `reanalysis/data/SOURCES.md`.
- Tests: unit tests for the token-classification and coverage logic, run on small hand-made strings; a regression check that the wordfreq 5k numbers from Phase 1 still reproduce if that code is touched.

## 8. Left to the builder

- Whether to extend `features.py` or add a new script (e.g. `lexical.py` + `stats5.py`), as long as the README table is updated.
- How to parse the downloaded list files (their format depends on the release).
- The output CSV layout, provided it gives one row per text and version (full / first360) and includes the coverage-accounting columns from G5.
