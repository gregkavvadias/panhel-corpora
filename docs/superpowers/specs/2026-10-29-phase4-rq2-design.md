# Phase 4: a new RQ2 (what distinguishes the exam texts, and does genre account for it?)

**Date:** 2026-10-29
**Branch:** `phase4-rq2`, created from `main` after PRs #1–#3 were merged.
**Context:** `HANDOFF.md` §4 Phase 4. The thesis's RQ2 asked which Coh-Metrix features correlate with RDL2 in each group. That question is partly circular, because RDL2 is built from content-word overlap, syntactic similarity and word frequency. Phase 3 part 2 produced open difficulty measures for 27 coursebook and 26 exam texts (`results/difficulty_features.csv`, `results/lexical_features.csv`).

## 1. Intent

**New RQ2:** *What distinguishes the Panhellenic exam reading texts from the state coursebook texts, and does genre account for the difference?*

Greg's reasons:
- The original aim of RQ2 was "what makes these texts difficult". Without RDL2 there is no non-circular difficulty criterion. The yearly score statistics Greg has (2019–2026) cover the whole paper, not the reading task.
- The paper's story is a **mismatch**: the exam texts are expository and abstract, while the coursebook texts are narrative and full of names. RQ2 tests that story directly.
- Greg describes the exam texts' abstractness as a matter of **topic and argument**, not single words (Phase 2 design). Genre is the variable that captures this.

## 2. Goals

### Part (a): separation

- **G1.** A penalised logistic regression (elastic net) that predicts group (exam = 1) from the open measures.
  - **Features:** the 21 measures in `difficulty_comparisons.csv` other than the readability formulas: `cov5k, conc_tok, imag, fam, mtld, hdd, mlc, clauses_per_sent, mean_sent_len, passive_inc, np_inc, vp_inc, adjp_inc, pp_inc, neg_inc, gerund_inc, inf_inc, cwo_adj, sem_overlap, conn_inc, causal_inc`. FRE and FKGL are excluded because they are composites of sentence length and syllables already represented. There are no length counts.
  - **Data:** full texts, 27 + 26.
- **G2. Validation by nested cross-validation.**
  - The outer loop is leave-one-out. The inner loop is 5-fold CV choosing the penalty strength and the L1 ratio.
  - Features are standardised inside each training fold.
  - Report cross-validated accuracy, balanced accuracy and AUC.
  - Add a permutation test: 1,000 label permutations through the whole nested procedure. If that is too slow, 200 with the number stated.
- **G3. Which measures matter.**
  - Report how often each measure is selected (non-zero coefficient) across the outer folds.
  - Report the sign and size of its standardised coefficient in a final fit on all data, with the penalty chosen by the same inner CV.
  - Signs are interpreted only for measures selected in at least 80% of folds.
- **G4. Robustness:** repeat G1–G3 with the length-matched coursebook texts (`first360`) against the full exam texts.

### Part (b): genre

- **G5. Genre labels for all 53 texts,** in `data/genre_labels.csv` (`book,text,fine,coarse,reason,status`).
  - Claude proposes a fine label and a one-sentence reason for each text, with `status = proposed`.
  - Greg confirms or changes each one, and `status` becomes `confirmed`.
  - No genre analysis runs on unconfirmed labels.
- **G6. Fine scheme:**

| Fine label | Coarse group |
|---|---|
| `fiction` (narrative fiction or literary extract) | narrative |
| `personal` (personal narrative or memoir) | narrative |
| `biography` | narrative |
| `informational` (expository or informational) | non-narrative |
| `argumentative` (argumentative or opinion) | non-narrative |
| `speech` | non-narrative |
| `review` (review or plot summary of a book or film) | non-narrative |
| `other` (a reason is required) | decided case by case, recorded in `coarse` |

- **Coding rule for mixed texts:** a text is labelled by its **dominant communicative purpose**, not by how it opens. A feature article that opens with an anecdote and then explains or argues is `informational` or `argumentative`. A review or plot summary describes a story rather than telling one, so it is `review`. The reason column states the purpose.
- **G7. Composition:**
  - a table of fine label × group;
  - Fisher's exact test of coarse genre × group, with the conditional maximum-likelihood odds ratio and its exact 95% CI (`scipy.stats.contingency.odds_ratio(kind='conditional')`), so a zero cell does not give an infinite estimate without a bound.
- **G8. Within-genre comparison** (the decisive test of whether genre accounts for the mismatch):
  - Compare **non-narrative coursebook texts with non-narrative exam texts** (both sides filtered by coarse genre) on two pre-specified measures: `conc_tok` (abstractness) and `passive_inc` (passives), the two differences the handoff names.
  - Statistics as before: Welch test, Hedges' g with bootstrap 95% CI, BH correction across these two tests.
  - Next to each result, show the all-text difference from Phase 3 part 2, so the reader can see whether the gap shrinks once genre is held constant.
  - **Small-group rule (fixed in advance):** if fewer than 5 coursebook texts **or** fewer than 5 exam texts are non-narrative, G8 is reported descriptively only (means, g, CI; no tests), and the README says that genre and group are too confounded to separate.
- **G9. Regression check:** for `conc_tok` and `passive_inc`, fit OLS with measure ~ group + coarse genre and report the group coefficient, its 95% CI and how much it changes from the group-only model. This is descriptive and outside the BH family.

### Reporting

- **G10. README "Phase 4: RQ2" section:**
  - cross-validated performance with the permutation p;
  - the selection-frequency table;
  - the composition table and Fisher test;
  - the within-genre results;
  - the regression check;
  - a plain statement of what genre does and does not explain.
- **G11. Optional:** if Greg supplies the 2019–2026 score statistics, add a descriptive table or plot of the yearly mean against each year's exam text measures (concreteness, 5k coverage), with no tests and with the caveat that scores cover the whole paper. Otherwise, a sentence in the README's notes for the discussion.

## 3. Non-goals

- Explaining or predicting difficulty itself (no difficulty criterion exists).
- Random forests or other high-variance models.
- New measures; Phase 3 part 2's measures are used as they are.
- A second human coder for genre. This can be added later as a reliability check on a subset.

## 4. Anti-goals

- Reading the classifier's coefficients as causes, or interpreting measures that are selected only occasionally.
- Reporting in-sample (non-cross-validated) accuracy as performance.
- Running genre analyses on labels Greg has not confirmed, or changing labels after seeing the within-genre results.
- Hiding the confounding of genre with group when it is severe.

## 5. Decisions

### Decided by Greg
- RQ2 is the mismatch question, with genre as the explanatory variable.
- Yearly score statistics are at most a descriptive aside.
- Genre is coded at a fine level; Claude proposes the labels with reasons, and Greg confirms or changes them.
- The model, the two-layer genre scheme and the within-genre test (accepted 2026-10-29).

### Claude's calls
- Elastic net with nested LOOCV, no random forest.
- The 21 features; FRE and FKGL excluded.
- The 80% selection threshold for interpreting signs.
- `speech` and `review` are coarse non-narrative; mixed texts are coded by dominant purpose.
- The within-genre comparison filters both groups by genre; the small-group rule applies to each side.
- The odds ratio uses the conditional MLE with an exact CI.
- The two within-genre measures (`conc_tok`, `passive_inc`) and the small-group rule (fewer than 5).
- Labels are frozen once Greg confirms them, before any within-genre analysis runs.

## 6. Constraints

- Same conventions as earlier phases: run from `reanalysis/`; `pathlib`; outputs in `results/`; pytest; TDD; seed 1.
- scikit-learn may be added to `requirements.txt`, pinned to the installed version.
- Corpus: 27 coursebook and 26 exam texts, as in Phase 3 part 2.

## 7. Left to the builder

- Script layout (e.g. `separation.py`, `genre.py`, or one `stats7.py`).
- The inner-CV grid, provided it is stated in the README.
- The format of the label proposal for Greg (the CSV with reasons is enough).
