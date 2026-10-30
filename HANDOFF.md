# Project handoff: from MA thesis to journal article

**Owner:** Greg Kavvadias
**Source thesis:** *A computational comparative analysis of text difficulty in the Greek high school English coursebooks and the national university entrance examinations for English*. MA TEFL/TEIL, Hellenic Open University, 2023 (supervisor: Karasimos).
**Goal:** a substantially reworked, publishable paper built on this corpus. It is a new paper, not a trimmed thesis.
**Status (30 Oct 2026):** Phases 1–5 are done. The analyses are in `reanalysis/README.md`. The paper is drafted in `paper/`, targeting *Reading in a Foreign Language*; what is left before submission is in `paper/open-questions.md`.

---

## 1. Repository layout

```
Texts/
  English 1/      10 reading texts (state coursebook, Lyceum Year 1)
  English 2/      18 reading texts (state coursebook, Years 2–3; unit-4-1 is excluded from analysis)
  Panhellenics/   26 exam reading passages: June 2010–2026 and September resits 2018–2026
reanalysis/       analysis scripts (Phases 1–4), data, results/ and tests/; README.md documents every step
  staging/        extracted exam passages as approved before promotion (provenance)
paper/            the article: one Markdown file per section, references, appendices
  numbers.md      every figure the paper may quote, generated from reanalysis/results
  tools/          numbers_build.py, check_numbers.py, wordcount.py, build_pdf.py (+ tests)
  figures/        coverage.py → coverage.png (Figure 1)
  second-coder/   blind genre-coding sample, instructions, key and responses
docs/superpowers/ design specs and implementation plans for each phase
HANDOFF.md        this file
```

Run all scripts from `reanalysis/` (`cd reanalysis`). Setup:

```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python fetch_resources.py        # BNC/COCA lists, Brysbaert and Glasgow norms, TAACO lists (not committed)
```

Note: `textstat` is not used because it needs NLTK's cmudict. Syllables are counted with `pyphen`.

---

## 2. Audit of the thesis: problems to fix in the paper

### Errors in the reporting
1. **Appendix D prints the school-text correlation table twice.** The exam-text correlations reported in §4.7 do reproduce from Appendix A, so this is a copy-paste error, not an analysis error.
2. **RDL2 direction is reversed in places.** RDL2 measures ease: higher means easier.
   - §5.3 calls paragraphs, connectives, negations and adverbs correlates of "difficulty". In fact they go with *easier* texts.
   - §5.4 says verb-phrase density and polysemy go with difficulty. They correlate positively with ease (r = .45 and .47).
3. **The concreteness and imageability finding is inverted in §5.2.** The *exam* texts are more abstract, but §5.2 says the coursebooks take "a more abstract, theoretical approach".
4. **VOCD-D is misread** as "unique words" (§4.2). It is a curve-fitted D estimate, not a type count.
5. **Appendix A has a WRDPRO (pronoun) column, but Appendices B–D report WRDPOLc (polysemy).** Polysemy values are therefore unavailable. CRFSOa and LSASSp are printed to one decimal place only.
6. **Typos in values:**
   - "r[26] = .053" should be .453.
   - Sig. values 0.20, 0.56 and 0.64 should be .020, .056 and .064.
7. **Problems in the references:**
   - Kintsch & Vipond is dated 2014; it is a 1979 chapter.
   - "Alderson, C. J., & Alderson, J. C." lists the same author twice.
   - The White (2010) short-term-memory claim is weakly supported.
8. **Selective reporting in §4.7.** These significant correlations were left out:
   - School texts: pronouns (r = .61) and concreteness (r = −.44).
   - Exam texts: concreteness (r = −.79), imageability (r = −.70) and word count (r = .64).

### Design and statistics problems
- **No correction for multiple comparisons.** The thesis ran 29 t-tests plus about 29 correlations per group.
- **One-sided p-values** are stated in the methods, while the text reports two-sided ones.
- **No effect sizes or confidence intervals.** "Not significant" is read as "comparable difficulty".
- **Length confound.** Exam texts are fixed at about 350 words; coursebook texts run from 197 to 1,689 words.
- **Normality is never checked,** although several school-text distributions are skewed.
- **RQ2 is partly circular.** RDL2 is built from content-word overlap, syntactic similarity and minimum content-word frequency, so correlating other Coh-Metrix indices with it mostly recovers their relationship to those three components.
- **WRDNOUN includes proper nouns** (see §3), which undermines the noun-density argument in §5.3.

### Corrections to earlier advice from the audit
- English 2 unit-8-3 is **not** a glossary. It is a dialogue-heavy passage from *The Book Thief* and is legitimate data.
- The idea that the later coursebook is easier than the earlier one is **not supported**: English 1 and English 2 do not differ on any index.

---

## 3. Reanalysis results (Phase 1, done)

All figures come from `reanalysis/results/`. Sample: 28 coursebook texts vs 13 exam texts.

**Group differences (Welch tests with Benjamini–Hochberg correction across 29 indices).**
- 9 of the thesis's 14 significant differences survive.
- 3 of those 9 are length artefacts: paragraph count (DESPC), sentence count (DESSC) and word count (DESWC).
- 6 substantive differences remain. In the exam texts:

| Index | What it measures | Exam vs coursebooks | Hedges' g |
|---|---|---|---|
| WRDIMGc | imageability | lower | −1.42 |
| WRDCNCc | concreteness | lower | −1.16 |
| DRPVAL | passives | fewer | −1.07 |
| SMCAUSvp | causal verbs and particles | fewer | −0.98 |
| WRDMEAc | meaningfulness | lower | −0.85 |
| DESSL | sentence length | longer | +0.85 |

- These 5 lose significance: LDVOCD (lexical diversity), DRVP (verb-phrase density), WRDNOUN (nouns), WRDADV (adverbs) and LSASSp (LSA similarity).
- The stricter Holm correction leaves 4: word count, passives, concreteness and imageability.

**The readability formulas (FRE, FKGL, RDL2) show no difference, but the study can't detect one.**
- RDL2: g = 0.29, 95% CI [−0.34, 1.01].
- The minimum detectable effect at 80% power is g ≈ 0.96. Adding exams up to 2026 (n = 17) would bring it down only to about 0.88.
- The paper must not claim the groups are equivalent.

**Nouns (`noun_split.py`).** Coh-Metrix WRDNOUN correlates ρ = .98 with nouns plus proper nouns, and only ρ = .22 with common nouns alone.

| | Proper nouns per 1k words | Common nouns per 1k words |
|---|---|---|
| Coursebook texts | 83 | 220 |
| Exam texts | 27 | 238 |

- The coursebooks' higher noun count comes entirely from proper nouns.
- Within the exam texts, RDL2 tracks common nouns: r = −.79.

**Lexical coverage (`features.py`, wordfreq word-form lists; indicative only).**
- Exam texts use more frequent vocabulary: 92.2% vs 90.2% of words fall in the top 5,000 (g ≈ 0.85).
- This holds when the coursebook texts are cut to their first ~360 words to match exam length.
- Both groups fall well short of the 98% coverage threshold.

**Progression.** English 1 vs English 2 vs exam (Kruskal–Wallis): the two coursebooks don't differ on any index, and the spread within each book is large.

**Emerging story:** the exam texts are *expository and abstract*, written in frequent but general-academic vocabulary. The coursebook texts are *narrative and full of names*. The readability formulas can't tell the two apart.

---

## 4. Phases (all done)

The plan below was written in Phase 1; each phase now has a design spec and a plan in `docs/superpowers/`, and its results in `reanalysis/README.md`.

- **Phase 2, methods upgrade:** BNC/COCA word-family coverage, Brysbaert concreteness, an equivalence test (TOST ±2 points).
- **Phase 3, corpus extension and open measures:** 13 exam passages added (June 2023–2026, resits 2018–2026); open measures of vocabulary, syntax and cohesion replace Coh-Metrix; one primary family of four tests.
- **Phase 4, new RQ2:** elastic-net separation model; genre composition and within-genre comparison.
- **Phase 5, the paper:** drafted in `paper/` for *Reading in a Foreign Language*; second-coder reliability done (κ = 1.00 coarse, .74 fine).

Rebuild order after any change: run the relevant `reanalysis/` script, then `python paper/tools/numbers_build.py`, `python paper/tools/check_numbers.py paper/0*.md paper/appendices.md`, `python paper/figures/coverage.py` and `python paper/tools/build_pdf.py`.

---

## 5. Working conventions
- Commits go on a feature branch and are fast-forwarded into `main` (Greg merges, or approves the merge).
- Keep scripts runnable from `reanalysis/` with paths relative to it; write outputs to `results/`.
- Every new finding goes into `reanalysis/README.md` with its effect size and corrected p-value.
- Greg's preference: direct, pressure-tested analysis; no overclaiming; report what fails as plainly as what survives.
