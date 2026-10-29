# Phase 5: the paper

**Date:** 2026-10-29
**Branch:** `phase5-paper`, created from `phase4-rq2`. PR #4 is not yet merged; the paper reports its results.
**Author:** Grigorios Kavvadias, sole author (first person singular). Claude drafts every section; Greg revises.

## 1. Intent

The paper turns the reanalysis (Phases 2–4, all in `reanalysis/README.md`) into a journal article. It is a **new paper, not a trimmed thesis**.

- **Target:** *Reading in a Foreign Language* (RFL).
- **Fallback:** a Greek ELT journal (*Research Papers in Language Teaching and Learning*, or GALA's *Journal of Applied Linguistics*).

The draft is written for RFL's standards. Preparing for RFL also strengthens the fallback version.

**Core story.** The Panhellenic English exam asks candidates to read texts whose vocabulary is no rarer than the coursebooks' (5k coverage equivalent within ±2 points), but which are clearly more abstract (lower concreteness and imageability) and entirely expository or argumentative. The state coursebooks contain many narratives. More importantly, their own non-narrative texts are more concrete and more passive-heavy than the exam's. So the mismatch lies in the kind of expository prose the school provides, not just in genre mix. Classic readability formulas do not register any of this.

## 2. Requirements (RFL submission guidelines, checked 2026-10-29)

- **Article:** at most **8,500 words**, excluding appendices.
- **Abstract:** at most 150 words; **5–7 keywords**.
- **Style:** **APA 7th edition**, checked at the desk stage.
- **Audience:** accessible to a broad audience of language educators, including people unfamiliar with the methods.
- **Review:** editor's desk check, then blind review by 2–3 reviewers. The manuscript must be anonymisable: self-citations to the thesis and the repository are written so they can be blinded for submission.

## 3. Research questions (as the paper states them)

- **RQ1:** How do the reading texts of the Panhellenic English examination compare with those of the state senior-high-school coursebooks in vocabulary, syntax and cohesion?
- **RQ2:** What distinguishes the examination texts from the coursebook texts, and does genre account for the difference?

## 4. Structure and word budget (about 8,200 words)

| File | Section | Words |
|---|---|---|
| `paper/00-front.md` | Title, abstract, keywords, author note (blinded version flagged) | 200 |
| `paper/01-introduction.md` | Problem, Greek context (the English special subject and its candidates), aim, RQs | 1,100 |
| `paper/02-background.md` | Text difficulty versus comprehensibility; readability formulas and their limits; lexical coverage and thresholds; abstractness and genre; teaching–testing alignment studies | 1,600 |
| `paper/03-method.md` | Corpus (27 + 26, how the exam texts were extracted and checked, the exclusion); measures by dimension, with primary and descriptive measures; pre-specification and statistics (equivalence test, BH family, robustness); separation model; genre coding | 2,100 |
| `paper/04-results.md` | RQ1 (difficulty table, equivalence, robustness); RQ2 (separation; genre composition; within-genre comparison) | 1,700 |
| `paper/05-discussion.md` | Interpretation; relation to the alignment literature; implications for materials and teaching; limitations; further research | 1,500 |
| `paper/06-conclusion.md` | Conclusion | 200 |
| `paper/references.md` | APA 7 reference list | n/a |
| `paper/appendices.md` | Full measure definitions; validation table; genre labels; data availability | n/a |

- **Tables in the main text, at most 5:** corpus description; the difficulty table (primary and key descriptive measures); equivalence and robustness; the separation model; genre composition and the within-genre comparison.
- **Figures:** at most 2, optional (for example, coverage curves by band for both groups). Figures are made from the result CSVs by a script in `paper/figures/`, never drawn by hand.

## 5. Sources of truth

- **Every number** in the paper comes from `reanalysis/results/*.csv` or the README sections that report them. No number is retyped from memory, and none comes from the thesis except where the paper explicitly reports the thesis's original values, for example RDL2.
- **The 27 vs 26 texts** are the corpus for all main results. The 13-text and 28-coursebook-text runs are mentioned only where the paper explains how its corpus was built.
- **The thesis literature** is the starting point for references. Every reference that is kept is verified against the published source (DOI or publisher page) before it goes in, and the errors the audit found are fixed (Kintsch & Vipond 1979; Alderson 2000; Hu & Nation 2000; and others). No reference may be cited that has not been located and checked.
- **New literature:**
  - a search for studies on Greek ELT materials, examinations or alignment published since 2023;
  - recent work on lexical coverage, abstractness and concreteness in L2 reading, and on genre in L2 reading;
  - Yildiz (2023) on Turkish exam-passage coverage.

## 5a. Settled during the builder check (Claude's calls unless marked)

- **Corpus selection** (from the thesis, §3.4):
  - **Coursebooks:** the texts in *English 1* and *English 2* (Nika, 2019a, 2019b) designed for reading comprehension. Vocabulary-focused texts and audio scripts were excluded, and some units have no reading text, hence the gaps in unit numbering.
  - **Exam:** only the main reading passage (Part A) of each paper (Greg).
- **Thesis and its references:** Greg supplied the thesis in this session. Its reference list is the starting point.
- **Reference verification standard:** "verified" means the source was located and its bibliographic details checked against the publisher or DOI record.
  - Where the paper describes a source's content and Claude cannot read the full text (paywalled), the claim is marked `[CHECK: content]` in the draft for Greg.
  - No claim stays marked at submission.
- **Word budget:** RFL's limit is ambiguous about references, so the draft plans conservatively. Main text about 7,000 words plus references about 1,300 gives about 8,300.
  - Section targets become: introduction 900, background 1,300, method 1,800, results 1,500, discussion 1,300, conclusion 200.
  - The full measure definitions, the validation table and the genre labels go to appendices.
- **How confirmatory the paper claims to be:** "pre-specified" is used only in the narrow sense of *fixed before the analysis reported here*.
  - The paper says openly that the concreteness and passives differences were observed in the author's earlier analysis of the original 13 exam texts.
  - It presents the present study as a re-test with open measures, corrected statistics and 13 additional exam texts. The 13 new exam texts are reported as a partial out-of-sample check (the June-only and original-13 subsets in `lexical_subsets.csv` / `difficulty_comparisons.csv`).

## 6. Framing decisions

- **The English special subject.** The paper explains what the Panhellenic English special subject is, who takes it (mainly candidates for English and foreign-language departments) and since when it has had a reading component (2010; Greek Official Gazette 493/Β/18-3-09).
  - Claims about candidates' preparation (frontistiria, C1/C2 certificates) appear only with a source, or are phrased as widely reported and flagged for Greg to source.
- **No claims about learners.** The paper is text-side and says so (the readability/comprehensibility distinction). Every claim about difficulty is phrased as a demand the texts make, not as an effect on learners.
- **Readability formulas** are reported as what the field commonly uses, and as unable to detect the differences found.
- **Diaspora papers** are excluded and described as popularly believed to be easier (Greg's wording).
- **Reporting.** The paper reports what fails as plainly as what holds: no difference in clause length after correction; no difference in content-word overlap by the pre-specified test; weak validation for three measures; the near-ridge model.

## 7. Non-goals

- New analyses. If drafting reveals a gap, it is raised with Greg, not quietly analysed.
- A Greek-language version (later, if the fallback venue requires it).
- A submission-ready Word or LaTeX file. Conversion with pandoc and an APA CSL file is a separate final step.
- Cover letter and submission forms.

## 8. Anti-goals

- Fabricated or unverified references, or a reference whose content is misdescribed.
- Numbers that differ from the result files.
- Overclaiming: equivalence beyond the ±2 raw-point sense; causal language about features; claims about learners' comprehension.
- Reusing thesis prose wholesale. The paper is newly written.
- Exceeding 8,500 words in the main text.

## 9. Process

- One section at a time, in order. Each section is committed when drafted. Greg revises in the repo or comments in chat.
- After each section, a short list of open questions for Greg (sources he must supply, claims he must confirm).
- A reference file is maintained as sections are written. Each entry carries a `verified:` note giving the source checked.
- Once all sections are drafted: a whole-paper consistency pass (numbers, terminology, word count), then a review by a fresh reader acting as an RFL reviewer.

## 9a. Decided by Greg (2026-10-29)

- **Alignment framing:**
  - The exam is **not formally tied** to *English 1* and *English 2*.
  - The paper frames the comparison as a question of the public school's **ethical responsibility to prepare candidates** for the Panhellenic examinations, not as a check of formal alignment.
  - Supporting facts: all Lyceum students take English in all three grades; the books were in use throughout the period covered (2010–2026); both the books and the past papers are publicly available on Greek state websites.
- **Data availability (updated 2026-10-29):** the corpus texts, scripts and derived measures are all **public** in the repository; the texts stay public (Greg). For review, the repository link is anonymised (e.g. via an anonymised mirror).
- **Thesis:** publicly available. It is cited as the origin of the corpus and of the earlier analysis (blinded as "Author, 2023" for review). The paper is not framed as a correction of the thesis. It reports its own analysis and notes, factually, where its findings revise earlier ones.
- **AI assistance:** declared.
  - **Method:** states that the genre labels were proposed with AI assistance (Claude) and confirmed or changed by the author, and that the exam passages were extracted by script and checked by the author against the PDFs.
  - **Disclosure statement:** covers AI-assisted analysis code and drafting, in the form the journal requires.
- **Second genre coder:** a person Greg arranges codes a sample blind. *Claude's call for the procedure:*
  - **Sample:** 20 texts, stratified so that both groups and all fine labels in use are represented.
  - **What the coder gets:** the coding scheme and its dominant-purpose rule, but not the author's labels.
  - **Agreement:** Cohen's κ on the coarse labels (primary) and on the fine labels.
  - **Disagreements:** reported, not resolved into the analysis; the confirmed labels stay frozen.
  - **Timing:** this is new data collection (not new analysis), so it can run in parallel with drafting. The method section has a placeholder until the result is in.

## 10. Open items for Greg (known now)

- **AI-assistance disclosure.** RFL's and the fallback journals' policies on disclosing AI-assisted drafting need checking. Greg decides how to declare it.
- **Sources for the claims about the candidates** (preparation in frontistiria, certificate levels), or confirmation that they should be softened.
- **Co-authorship** stays single-author unless Greg changes it after speaking to Karasimos.
