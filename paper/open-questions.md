# Open questions for Greg

Last tidied 30 Oct 2026. Everything resolved so far is listed under "Resolved" below; the full history is in git.

## Editing in Claude Docs (from 3 Nov 2026)

- The manuscript is being edited in a Claude Doc: https://claude.ai/artifact/FMPqwihXGzUWRFzzVANPmK
- The Doc is the master copy for the wording until it is synced back; don't edit `paper/0*.md` meanwhile.
- Last synced 6 Nov 2026 from Doc revision 63. Earlier syncs: revision 33 (3 Nov), baseline commit `9a46350`.
- The master copy is now **non-blinded** (name, affiliation, ORCID, bio, Kavvadias 2023, repository link). The review copy is built with `python paper/tools/build_pdf.py --blind` → `paper/build/manuscript-blinded.pdf`. Numbers and references stay mastered here; after the sync, run `check_numbers.py`, `wordcount.py`, the citation check and `build_pdf.py`.

## Still open

- **Coursebook exclusions:** the Method says texts that only present vocabulary, and audio scripts, were excluded (following the thesis). Is that accurate, and were any other kinds excluded?
- **Resit papers from 2018:** the Method says the resits are those "available on the Ministry's examination archive (2018–2026)". Is that why they start in 2018 (no earlier papers published)? If so, I'll say so explicitly.
- **Coh-Metrix wording:** the paper calls it "a web-based tool whose code is not open", as the reason for rebuilding the measures. Adjust if you'd put it differently.
- **The cohesion outlier:** the Results describe English 2 unit-6-1 ("I Have a Dream") without naming it. Name it if you prefer.
- **Title:** "Equally Frequent, More Abstract: …". Keep it, or something plainer?
- **Elastic net:** a reviewer-style suggestion was to move RQ2(a) to an appendix. It now has plain-language explanations in the Method; keep it in the main text or move it?

## Before submission

- Set up the anonymised repository mirror for review (e.g. anonymous.4open.science).
- AI declaration: now in the manuscript, before the References; also put it in the cover letter.
- Cover letter.
- File format: check whether RFL wants .docx; the PDF is built by `python paper/tools/build_pdf.py`.

## Resolved

- **References:** every entry is verified against Crossref, a publisher page, the article PDF or the thesis reference list (see the `verified:` comments in `references.md`).
  - The coursebooks are cited under their authors (Nika was critical reader). Edition year and publisher are confirmed.
  - The exam regulation is cited as Φ.253/154481/Α5, ΦΕΚ 7261/Β/31-12-2024.
  - Lee & Kang (2021) is cited in its AJEMR version, pp. 53–60, from the PDF. The publisher's DOI landing page shows another article.
  - Kintsch & Vipond is cited in the 1979 original.
  - Greenfield (2004) is described as supporting the classic formulas for EFL readers.
  - Fulcher (1997) was dropped.
- **Context:**
  - *English 1* is for Lyceum Year 1 and *English 2* for Years 2–3.
  - Both sets of texts are adapted.
  - Tuition-centre preparation is sourced to Tsiplakou & Tsagari (2023) and Kim (2024).
  - The published exam statistics cover 2019–2026 for the whole paper only.
- **Second coder:** coarse κ = 1.00 (20/20); fine κ = .74 (16/20); disagreements are in Appendix C.
- **Funding and conflicts:** none.
- **AI disclosure:** Greg supplies it at submission; removed from the draft.
- **Word limit:** references and appendices don't count. The main text is 7,514 of 8,500.
- **RFL style:**
  - untitled introduction;
  - a "The Present Study" section;
  - APA title-case headings;
  - first person kept for the author's own decisions;
  - end-matter statements placed before the References;
  - Figure 1.
- **Expansions:**
  - a fuller review of the coursebook–exam studies;
  - plain-language glosses of the statistics;
  - the equivalence caveat.
