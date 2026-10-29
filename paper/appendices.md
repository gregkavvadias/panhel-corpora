# Appendices

## Appendix A: Measures

All measures are computed by `reanalysis/difficulty.py` and `reanalysis/lexical.py` in the repository ([anonymised repository link]); the code, its tests and the frozen definitions are there. Content tokens are alphabetic tokens tagged NOUN, VERB, ADJ or ADV that are not proper nouns. Incidences are per 1,000 alphabetic tokens.

| Dimension | Measure | Definition |
|---|---|---|
| Vocabulary | 5k coverage (primary) | Percentage of running words (proper nouns excluded) in the 1k–5k BNC/COCA word-family bands (Nation, 2017), with the supplementary lists counted as known. Also computed for 1k–9k. |
| Vocabulary | Concreteness (primary) | Token-weighted mean Brysbaert et al. (2014) rating (1–5) of content tokens. |
| Vocabulary | Imageability, familiarity | Token-weighted mean Glasgow Norms rating (1–7) of content tokens matched by lemma (Scott et al., 2019). |
| Vocabulary | MTLD, HD-D | Lexical diversity of lower-cased alphabetic tokens (McCarthy & Jarvis, 2010). |
| Syntax | Mean length of clause (primary) | Alphabetic tokens ÷ finite clauses. A finite-clause head is a verb or auxiliary whose dependency is ROOT, ccomp, advcl, relcl, csubj or acl, or a conj with its own subject, and that is finite (it or one of its auxiliaries is tagged VBD, VBP, VBZ or MD; an imperative ROOT also counts). |
| Syntax | Clauses per sentence; mean sentence length | Finite clauses ÷ sentences; alphabetic tokens ÷ sentences. |
| Syntax | Passives; noun phrases; verbs; adjectives; prepositional phrases; negation; gerunds; infinitives | Incidence of auxpass dependencies; noun chunks; VERB tokens; ADJ tokens; prep dependencies; neg dependencies; VBG tokens without an auxiliary; *to* + base-form verb. |
| Cohesion | Content-word overlap (primary) | Mean over adjacent sentence pairs of the share of the pair's content tokens whose lemma occurs in both sentences. |
| Cohesion | Semantic overlap | Mean cosine between the mean word vectors (spaCy `en_core_web_md`) of adjacent sentences' content lemmas. |
| Cohesion | Connectives; causal connectives | Incidence of items on the TAACO connective lists and causal list (Crossley et al., 2016; Crossley, Kyle, & Dascalu, 2019), longest match first; context-dependent items excluded. |
| Readability | Flesch Reading Ease; Flesch–Kincaid Grade Level | Standard formulas (Flesch, 1948; Kincaid et al., 1975), syllables counted with pyphen. |

**Descriptive measures not shown in Table 2** (exam − coursebook)

| Measure | Coursebook *M* | Examination *M* | *g* [95% CI] |
|---|---|---|---|
| Noun phrases per 1,000 words | 298.1 | 291.9 | −0.36 [−0.96, 0.17] |
| Verbs per 1,000 words | 125.0 | 134.9 | 0.45 [−0.06, 1.03] |
| Adjectives per 1,000 words | 80.0 | 98.2 | 0.66 [0.14, 1.25] |
| Prepositional phrases per 1,000 words | 123.4 | 112.7 | −0.53 [−1.08, −0.02] |
| Negation per 1,000 words | 5.03 | 7.85 | 0.53 [0.01, 1.14] |
| Gerunds per 1,000 words | 18.7 | 22.0 | 0.35 [−0.16, 0.98] |
| Infinitives per 1,000 words | 14.9 | 17.3 | 0.30 [−0.24, 0.81] |
| Causal connectives per 1,000 words | 6.55 | 8.98 | 0.46 [−0.06, 1.03] |

## Appendix B: Validation against Coh-Metrix

Spearman's ρ [95% CI] between each open measure and the corresponding Coh-Metrix 3.0 index on the 40 original texts: pooled, and within the 27 coursebook and 13 examination texts. Confidence intervals use the Fisher *z* transformation and are slightly narrow for ρ at *n* = 13. Mean length of clause, clauses per sentence, MTLD and familiarity have no Coh-Metrix counterpart in the earlier data.

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

## Appendix C: Genre labels

Labels were assigned by dominant communicative purpose, proposed with AI assistance and confirmed or changed by the author, and frozen before analysis. Coarse groups: narrative (fiction, personal, biography, and two texts labelled *other*: a plot retelling and a historical recount) and non-narrative (informational, argumentative, speech, review).

**Second-coder agreement:** [κ: pending] (coarse), [κ: pending] (fine), on a stratified sample of 20 texts. Disagreements: [to be listed].

| Book | Text | Label | Group |
|---|---|---|---|
| English 1 | unit-2-1 | informational | non-narrative |
| English 1 | unit-3-1 | informational | non-narrative |
| English 1 | unit-4-1 | biography | narrative |
| English 1 | unit-5-1 | informational | non-narrative |
| English 1 | unit-5-2 | argumentative | non-narrative |
| English 1 | unit-6-1 | informational | non-narrative |
| English 1 | unit-7-1 | review | non-narrative |
| English 1 | unit-7-2 | other | narrative |
| English 1 | unit-8-1 | informational | non-narrative |
| English 1 | unit-8-2 | argumentative | non-narrative |
| English 2 | unit-2-1 | biography | narrative |
| English 2 | unit-2-2 | fiction | narrative |
| English 2 | unit-3-1 | biography | narrative |
| English 2 | unit-3-2 | biography | narrative |
| English 2 | unit-3-3 | biography | narrative |
| English 2 | unit-3-4 | biography | narrative |
| English 2 | unit-3-5 | biography | narrative |
| English 2 | unit-5-1 | informational | non-narrative |
| English 2 | unit-6-1 | speech | non-narrative |
| English 2 | unit-6-2 | speech | non-narrative |
| English 2 | unit-7-1 | speech | non-narrative |
| English 2 | unit-8-1 | review | non-narrative |
| English 2 | unit-8-2 | review | non-narrative |
| English 2 | unit-8-3 | fiction | narrative |
| English 2 | unit-8-4 | fiction | narrative |
| English 2 | unit-8-5 | informational | non-narrative |
| English 2 | unit-8-6 | other | narrative |
| Panhellenics | 2010-06 | informational | non-narrative |
| Panhellenics | 2011-06 | informational | non-narrative |
| Panhellenics | 2012-06 | informational | non-narrative |
| Panhellenics | 2013-06 | argumentative | non-narrative |
| Panhellenics | 2014-06 | informational | non-narrative |
| Panhellenics | 2015-06 | informational | non-narrative |
| Panhellenics | 2016-06 | informational | non-narrative |
| Panhellenics | 2017-06 | argumentative | non-narrative |
| Panhellenics | 2018-06 | informational | non-narrative |
| Panhellenics | 2018-09 | informational | non-narrative |
| Panhellenics | 2019-06 | argumentative | non-narrative |
| Panhellenics | 2019-09 | argumentative | non-narrative |
| Panhellenics | 2020-06 | informational | non-narrative |
| Panhellenics | 2020-09 | informational | non-narrative |
| Panhellenics | 2021-06 | argumentative | non-narrative |
| Panhellenics | 2021-09 | argumentative | non-narrative |
| Panhellenics | 2022-06 | argumentative | non-narrative |
| Panhellenics | 2022-09 | informational | non-narrative |
| Panhellenics | 2023-06 | informational | non-narrative |
| Panhellenics | 2023-09 | informational | non-narrative |
| Panhellenics | 2024-06 | argumentative | non-narrative |
| Panhellenics | 2024-09 | argumentative | non-narrative |
| Panhellenics | 2025-06 | informational | non-narrative |
| Panhellenics | 2025-09 | informational | non-narrative |
| Panhellenics | 2026-06 | informational | non-narrative |
| Panhellenics | 2026-09 | informational | non-narrative |
