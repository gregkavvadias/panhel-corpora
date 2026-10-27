# Phase 3 (part 2): open measures of text difficulty

**Date:** 2026-10-27
**Branch:** `phase3-measures`, created from `phase3-corpus`. PRs #1 and #2 are not yet merged; this work needs the 26-text exam corpus from #2.
**Context:** `HANDOFF.md` §4. Part 1 (`docs/superpowers/specs/2026-10-27-phase3-corpus-extension-design.md`) extended the exam corpus to 26 texts. The Phase 1 Coh-Metrix analyses cannot include the 13 new texts.

## 1. Intent

The paper needs a table comparing coursebook and exam texts on **text difficulty**. Greg wants it to cover the variables of the original thesis, adjusted to what research says matters for difficulty.

Coh-Metrix values exist only for the original 41 texts, and they come from a web service that nobody can rerun exactly. So the table is rebuilt with **open, reproducible measures computed on all 53 texts** (27 coursebook after excluding one exercise, 26 exam). On the 40 original texts that remain, the thesis's Coh-Metrix values become a **validation check** for the new measures.

**Framework.** Graesser, McNamara & Kulikowich (2011) describe five dimensions of text difficulty: word concreteness, syntactic simplicity, referential cohesion, deep cohesion and narrativity. The Coh-Metrix L2 readability index (Crossley, Greenfield & McNamara, 2008) combines word frequency, syntactic similarity and content-word overlap. The table is organised by dimension:
- vocabulary;
- syntax;
- cohesion;
- readability formulas, as reference only;
- narrativity, deferred to the genre analysis in Phase 4(b).

Each dimension has one or two **pre-specified primary measures**. Everything else is descriptive. This keeps the broad picture of the thesis without its multiple-comparisons problem, and it is consistent with the scope rationale drafted in Phase 2.

## 2. Measures

### Primary: tested, in one BH family of four

| Dimension | Measure | Definition | Status |
|---|---|---|---|
| Vocabulary | `cov5k` | BNC/COCA 5k word-family coverage | Done (Phase 2) |
| Vocabulary | `conc_tok` | Mean Brysbaert concreteness of content lemmas | Done (Phase 2) |
| Syntax | `mlc` | Mean length of clause: alphabetic tokens ÷ finite clauses | New |
| Cohesion | `cwo_adj` | Content-word overlap between adjacent sentences | New |

- **Mean length of clause (`mlc`).** This follows Lu's L2SCA definition of MLC. A finite clause is counted as a token whose dependency label is `ROOT`, `ccomp`, `advcl`, `relcl`, `csubj` or `acl`, provided it is a verb or auxiliary with finite morphology (or a `ROOT` verb). The exact rule is the builder's to write down, test, and document in the README.
- **Content-word overlap (`cwo_adj`).** For each pair of adjacent sentences, take the proportion of content-word lemmas (NOUN, VERB, ADJ, ADV; not proper nouns) in the two sentences that appear in both. Average over all pairs. This follows Coh-Metrix CRFCWO1, the cohesion component of the L2 readability index.

### Descriptive: reported with group means, Hedges' g and 95% CIs; no p-values in the main table

| Dimension | Measure | Source |
|---|---|---|
| Vocabulary | Imageability; familiarity (mean over content lemmas found in the norms, with the coverage share) | Glasgow Norms (Scott et al., 2019) |
| Vocabulary | Lexical diversity: MTLD and HD-D (HD-D is the standard open substitute for VOCD-D) | `lexical-diversity` package (already a dependency) |
| Syntax | Mean sentence length; passives per 1,000 words; clauses per sentence; noun-phrase, verb-phrase, adjective-phrase and prepositional-phrase incidence; negation, gerund and infinitive incidence | spaCy |
| Cohesion | Connective incidence (all and causal); semantic overlap of adjacent sentences using word embeddings in place of LSA | TAACO word lists and models, or an equivalent, documented open source |
| Readability | Flesch Reading Ease; Flesch–Kincaid Grade Level | Same formula and syllable counter as `features.py` |

### Dropped, with reasons for the paper
- **Length counts** (DESPC, DESSC, DESWC, DESPL): not difficulty. Phase 1 showed they are artefacts of the exam's fixed length.
- **Meaningfulness** (WRDMEAc): its only source is the sparse MRC database. *Claude's call.*
- **RDL2:** Coh-Metrix's own formula, which can't be rebuilt openly. The paper reports its thesis values for the original texts only.
- **Parts-of-speech incidence** (WRDNOUN etc.): Phase 1 showed WRDNOUN mixes proper and common nouns. It is reported descriptively only if the builder finds it cheap; it is not part of the difficulty table.

## 3. Goals

- **G1.** `results/difficulty_features.csv`: one row per text and version (full; `first360` for coursebook texts) with every measure in §2 and the coverage share of each norm.
- **G2.** `results/difficulty_comparisons.csv`:
  - the primary tests, with the same statistics as Phase 2 (Welch and Mann–Whitney, Hedges' g with bootstrap 95% CI, B = 5000, seed 1) and BH over the four primary Welch p-values on full texts;
  - the TOST on `cov5k` (±2) reported as before, outside the family;
  - descriptive rows with g and CI only.
- **G3. Robustness checks for the two new primary measures:** length-matched texts, June-only exam texts, and the original-13 exam texts. These are uncorrected and labelled as robustness.
- **G4. Validation** (`results/difficulty_validation.csv`): on the 40 remaining original texts, the Spearman ρ between each new measure and its Coh-Metrix counterpart:

| New measure | Coh-Metrix counterpart |
|---|---|
| `conc_tok` | WRDCNCc |
| imageability | WRDIMGc |
| HD-D | LDVOCD |
| sentence length | DESSL |
| passives | DRPVAL |
| phrase incidences | DRNP, DRVP, DRAP, DRPP |
| negation | DRNEG |
| gerunds | DRGERUND |
| infinitives | DRINF |
| `cwo_adj` | CRFSOa (approximate: stem overlap across all sentences, binary) |
| connectives | CNCAll |
| causal connectives | SMCAUSvp |
| semantic overlap | LSASSp |
| FRE | RDFRE |
| FKGL | RDFKGL |

  Report ρ with its 95% CI. A low ρ is reported and explained, not hidden.
- **G5. README section** with the difficulty table (dimension, measure, school mean, exam mean, g [CI], p and BH p for the primaries), the validation table, the robustness rows, the list of dropped indices with reasons, and an updated scope paragraph for the paper.

## 4. Non-goals

- Narrativity and genre classification (Phase 4b).
- New research question 2, the classifier (Phase 4a).
- Rewriting `features.py`, `stats1.py`–`stats4.py` or the Phase 1 results. They stay as records.
- CEFR profiling, CAREC or transformer readability models.

## 5. Anti-goals

- Choosing primary measures, definitions or the correction family after seeing results.
- Testing every descriptive measure for significance and reporting the significant ones; that would bring back the thesis's selective-reporting problem.
- Presenting a rebuilt measure as equivalent to Coh-Metrix without the validation ρ.
- Silent loss of coverage: every norm-based measure reports the share of content words it covers.

## 6. Decisions

### Decided by Greg
- The table covers the original study's variables, adjusted by research on text difficulty.
- The measures, the primary/descriptive split and the dimensions in §2 (accepted 2026-10-27).
- **English 2 unit-4-1 is excluded.** It is a formatting exercise ("Format the text"), with spaces and punctuation removed (e.g. "flyslowly"), not a reading passage.
  - It is listed in a committed `data/excluded_texts.csv` (`book,text,reason`), and `corpus.iter_texts` skips listed texts.
  - The coursebook group is therefore **27 texts** in every analysis from this phase on, including the recomputed Phase 2 measures (coverage, concreteness).
  - The published 28-text results stay in git history, and the README notes the change.
  - Phase 1 Coh-Metrix analyses (`stats1.py`–`stats3.py`) and `features.py`/`stats4.py` are historical records and keep their 28 texts. The validation step (G4) uses the 40 original texts that remain (27 coursebook, 13 exam).
- **Title and subheading lines in coursebook files are skipped by the sentence-based measures.** The files themselves are not edited.
  - The lines are listed in a committed `data/heading_lines.csv` (`book,text,line`, exact line text), drawn from the files with heading lines: English 1 unit-5-2; English 2 unit-3-3, 3-4, 3-5, 6-1, 6-2, 8-2, 8-3, 8-5 ("The Memorial") and 8-6 ("Victims").
  - The sentence-based measures (`mlc`, `cwo_adj`, sentence length, clauses per sentence, semantic overlap) drop those lines before parsing. Markdown emphasis markers (`**`) are stripped for all measures.
  - Lines that are not headings (a broken line in English 1 unit-7-2, verse lines in English 2 unit-8-5) are kept.
  - Word-based measures are computed on the full text as before.

### Claude's calls
- **One BH family of four primary tests for the paper.** This supersedes Phase 2's two-test family; the Phase 2 numbers remain on record.
- **Meaningfulness dropped;** the Glasgow Norms supply imageability and familiarity.
- **The simple measures are computed in project code** (overlap, clauses, phrase incidences), with definitions written in the README. TAACO is a source of word lists and models only. Like the other resources, these are downloaded at run time and not committed, because TAACO's repository states no licence.
- **The primary cohesion measure follows CRFCWO1** (adjacent sentences, proportional), for its role in L2 readability. Its validation counterpart in the thesis data is CRFSOa, so a moderate correlation is expected and will be explained.
- **The exact `cwo_adj` formula:**
  - Content tokens are alphabetic tokens tagged NOUN, VERB, ADJ or ADV that `lexical.classify` does not mark as proper nouns, so Nation's list 31 and `propn_overrides.csv` apply, as in Phase 2.
  - For adjacent sentences A and B, the pair score is the number of content tokens in A and B whose lower-cased lemma occurs in both sentences, divided by the total number of content tokens in A and B.
  - Pairs where either sentence has no content tokens are skipped and counted, and the share of skipped pairs is reported per text.
  - The text score is the mean over the scored pairs.
  - Where this differs from Coh-Metrix's CRFCWO1, this written definition wins.
  - The Glasgow measures use the same content-token and proper-noun rules as `conc_tok`.
- **Definitions are frozen before any corpus run:**
  - The plan's first measure tasks write each rule, its unit tests on hand-made sentences and its README definition, and commit them. Only then does any script run on the corpus.
  - After the freeze, a rule may change only to fix a **bug**, meaning the code does not do what the written definition says. Improving agreement with Coh-Metrix or the look of the results is not a reason to change a rule.
  - Every post-freeze change is listed in the README with the before and after values of any primary measure it touches.
- **Validation ρ is reported pooled over the 40 texts and within each group** (27 coursebook, 13 exam). Pooled ρ partly reflects group differences.

## 7. Constraints

- Same conventions as earlier phases: run from `reanalysis/`, `pathlib`, `results/` outputs, sources and versions in `data/SOURCES.md`, tests with pytest, TDD.
- The same spaCy model (`en_core_web_sm` 3.8.0) for every measure.
- Statistics reuse `effects.py` and `stats5.py` helpers rather than duplicating them.

## 8. Left to the builder

- Script layout (e.g. `difficulty.py` for features and `stats6.py` for comparisons), as long as the README table is updated.
- Exact spaCy rules for clauses and phrase types, provided they are tested on hand-made sentences and documented.
- Which embedding model provides semantic overlap, provided it is open, versioned and recorded.
