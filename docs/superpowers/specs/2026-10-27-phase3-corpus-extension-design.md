# Phase 3 (part 1): extending the exam corpus

**Date:** 2026-10-27
**Branch:** `phase3-corpus`, created from `phase2-lexical`. PR #1 is not yet merged, and this work builds on the Phase 2 scripts.
**Context:** `HANDOFF.md` §4 Phase 3, items 7 and 9. Part 2, replacing the Coh-Metrix indices with open measures on all texts, gets its own design and depends on this one.

## 1. Intent

The paper's main claims will rest on a larger exam corpus. It adds the June papers for 2023–2026 and the September resit papers (επαναληπτικές) for 2018–2026 to the existing 13 June texts from 2010–2022. This takes the exam group from 13 to **26 texts**.

Greg's reasons:
- The paper is about the exam as it is now, so recent papers belong in it.
- The resit papers come from the same central committee (ΚΕΕΜ), written to the same specification, so they are a fair sample of what the exam asks of candidates.
- A larger exam group gives more power. With 13 texts the minimum detectable effect is g ≈ 0.96.

The 13-text Phase 2 results stay on record as the originally pre-specified run.

## 2. Goals

- **G1. Thirteen new files** in `Texts/Panhellenics/`:
  - `2023-06.txt` … `2026-06.txt` (4 June papers)
  - `2018-09.txt` … `2026-09.txt` (9 resit papers)
  - Each contains **only the main reading passage**, part A of the paper.
- **G2. Same format as the existing exam files:**
  - Plain text, UTF-8, CRLF line endings.
  - One paragraph per line, with a blank line between paragraphs.
  - No title, subheadings, source line ("Adapted from…", URL, year), instructions, questions or page furniture ("ΑΡΧΗ 2ΗΣ ΣΕΛΙΔΑΣ", "ΤΕΛΟΣ…").
- **G3. A reproducible extraction script** that:
  - downloads each paper PDF into a gitignored folder;
  - extracts the passage and writes the 13 files;
  - writes a review report.
- **G4. A review report for Greg** listing, for each new file:
  - the word count;
  - the number of paragraphs;
  - every *suspect* token, for Greg to judge.

  A suspect token is any of: a word that is neither on the BNC/COCA lists nor in the Brysbaert norms; a capital I inside a lowercase word (e.g. "schooIs"); a single letter split from its word (e.g. a drop cap rendered as "H ow"); a hyphen at the end of a line that was rejoined; mojibake or an unexpected character.

  Suspect tokens are **flagged, never silently corrected**. The script changes text only in the mechanical ways §5 lists.
- **G5. Greg's verification gate.** Greg compares each new file with its PDF and either approves it or reports corrections (the mechanism is in §5). No new text enters any analysis before his approval.
- **G6. Phase 2 rerun on 28 coursebook vs 26 exam texts**, with the pre-specified settings unchanged: 5k coverage, TOST margin ±2 points, full texts primary, length-matched texts as robustness, BH correction over the two primary tests. This includes the proper-noun review for any new proper-noun types (same process as before: `results/propn_types.csv` → `data/propn_overrides.csv`).
- **G7. Sitting check:** compare the 17 June texts with the 9 resit texts on the Phase 2 primary measures (5k coverage, token-weighted concreteness). Report Hedges' g with a 95% CI. This is descriptive and outside the BH family. A large difference must be reported, because it would make pooling the sittings something the paper has to explain.
- **G8. README:** report the 26-text results as primary, next to the 13-text results. Any conclusion that differs between the two is stated plainly. Record the paper sources in a sources file.

## 3. Non-goals

- **Diaspora (ομογενείς) papers.** They are a separate exam for a different group of candidates, widely believed to be easier. Including them would bias the exam group. They can be listed as possible future work.
- **Coh-Metrix-based Phase 1 analyses** (`stats1.py`–`stats3.py`). These stay as they are on the original 13 exam texts. Part 2 replaces them with open measures on all texts.
- **Re-extracting or editing the existing 13 June files.**
- **New coursebook texts** (HANDOFF item 8).

## 4. Anti-goals

- A new text entering the analysis without Greg's approval.
- Silent correction of anything that might be in the original paper. For example, "schooIs" might be a typo in the paper itself.
- Two-column passages extracted with the columns interleaved (see §6).
- The Phase 2 settings changing because of the new texts.
- Presenting the 26-text result while hiding a disagreement with the 13-text result.

## 5. Decisions

### Decided by Greg
- Only the main reading passage is extracted.
- June and resit papers are included; diaspora papers are excluded.
- All 26 exam texts carry the paper's main claims, with the 13-text run kept on record.
- The Coh-Metrix replacement is a separate part 2, applied to all texts and validated against the thesis Coh-Metrix values.
- Greg checks each new file against its PDF.

### Claude's calls
- **Subheadings inside the passage are dropped** (none is known in the 13 new papers; see §6). None of the existing 13 exam files contains a heading line, so this matches them. The review report lists every dropped line so Greg can see them.
- **Mechanical fixes the script may apply** (anything else is only flagged):
  - rejoining lines within a paragraph;
  - rejoining a word hyphenated across a line break (and listing it);
  - normalising typographic quotes and dashes to the forms used in the existing files;
  - removing page furniture.
- **Paragraph boundaries** are inferred from the layout: a line that ends well short of the right margin closes a paragraph, as does a vertical gap. Greg's comparison against the PDF is the safeguard.
- **Resit naming** uses `-09` (September) for every resit year, even if a particular sitting fell in late August.
- **Staging and the source of truth:**
  - The script writes to `reanalysis/staging/Panhellenics/`, a committed folder outside `Texts/`, so nothing unapproved can reach `corpus.iter_texts`, `features.py` or `noun_split.py`.
  - Greg does not edit the files directly. He reports corrections, and Claude records each one in `reanalysis/data/exam_corrections.csv` (`file,find,replace,note`). The script applies them, and fails if a `find` string isn't present exactly once.
  - The script's output therefore reproduces the approved files exactly, which supports the open-data claim.
  - Approval is recorded in `reanalysis/data/exam_approvals.csv` (`file,approved_by,date`).
  - A separate step copies only approved files into `Texts/Panhellenics/`, and refuses to overwrite a file that differs from the current script output.
  - `tests/test_helpers.py`'s count of 13 exam files becomes 26 in the same commit as the copy.
- **Sitting check (G7) needs no threshold:**
  - A June-only sensitivity run of the two primary Phase 2 tests (17 June texts vs 28 coursebook texts, same settings including TOST ±2) is always run and reported, whatever the June-vs-resit g turns out to be. Fixing it in advance means no post-hoc trigger is needed.
  - The README states whether the June-only and 26-text conclusions agree.
- **Scope of the rerun:**
  - Only the Phase 2 pipeline is rerun on 26 texts: `lexical.py` and `stats5.py`.
  - `features.py` and `stats4.py` (Phase 1's own spaCy and wordfreq features) are left for part 2, which replaces or extends them on all texts. Their committed results stay at 13 exam texts, and they are not rerun in part 1.
  - `stats1.py`–`stats3.py` are unchanged (see §3).
- **What "the 13-text record" means:**
  - The published Phase 2 numbers stay in git history (commit `ee0280e`) and in the README text that reports them.
  - The side-by-side comparison in G8 recomputes the 13-text run using the **same** updated `propn_overrides.csv` as the 26-text run, so the comparison isolates the effect of adding texts. If a new override changes any 13-text figure compared with the published one, the README notes it.

## 6. Sources and known extraction issues (verified 2026-10-27)

**Source index:** https://www.panellinies.net/θεματα-πανελλαδικεσ-αγγλικά/

Each year's page links the paper PDF (link text "Θέματα", not "Απαντήσεις"):

| File | Paper link |
|---|---|
| 2023-06 | Google Drive `1bVSjtJUAu0id-mfCEbPLIGhuJQ6naVWG` |
| 2024-06 | Google Drive `1AqGpKo4SXtcizQ3vQP5-EbG3D9aNfDqu` |
| 2025-06 | `https://www.panellinies.net/wp-content/uploads/2025_them/2025_them_eidika/agglika_2025_00.pdf` |
| 2026-06 | `https://www.panellinies.net/wp-content/uploads/2026_them/2026_them_eidika/agglika_2026.pdf` |
| 2018-09 | Google Drive `16miilGBwkHO5nOqZWnhXkNDGXbp4qTTw` |
| 2019-09 | Google Drive `12iNtH_HMe7chDtiaT2-dLj0qbp5tbRnm` |
| 2020-09 | Google Drive `1sIGNJ-FIxPabwEOV5xu4qvZv52GGoaT8` |
| 2021-09 | Google Drive `1oOxQcGMYuhzZrX9yxdHig_rpAbloHUtv` |
| 2022-09 | Google Drive `1900AalHuwGgkyLI5Jtc78OwN6Q_mXmqv` |
| 2023-09 | Google Drive `1kFa-NEY7v08CLgLpIqPKfZutUfvoC-7V` |
| 2024-09 | Google Drive `1CAk8OFX9rwARXqHZ6dS8J5COFVnSsbjy` |
| 2025-09 | Google Drive `11ho542jvHPGmw34egyLwWa_QLWe_zukZ` |
| 2026-09 | Google Drive `1DMcOWHIv_z0ZWpZc9yhQoG3mvGTBqUte` |

- **Downloading:** a Drive file downloads from `https://drive.google.com/uc?export=download&id=<id>`. All 13 return a PDF with a text layer, so no OCR is needed. Use curl with `--ssl-no-revoke`, or urllib with a browser User-Agent.
- **Where the passage is:** it starts after the line "A. Read the text below and respond to tasks A1 and A2." on page 2. It ends before "Adapted from" or the source URL line, or before the page footer when no source line exists.
- **Two-column layout:** 2018-09, 2019-09 and 2020-09 set the passage in two columns, and plain text extraction interleaves them. These need column-aware extraction: crop the left and right halves of the page by x-coordinate, and read the left column, then the right.
- **Known artefacts** (re-verified by the builder check and by Claude; corrected 2026-10-27):
  - 2023-06 contains "schooIs" (capital I). This is flagged, not corrected.
  - **2024-09 carries a hidden text layer.** Page 2 holds roughly 100 words in Calibri 11: what looks like an older draft of the last paragraph, plus a stray fragment ("u to look at the world — one not mediated through a screen — and translate that."). Neither is visible on the rendered page. The visible passage is in ArialMT 10, about 374 words in 4 paragraphs, and starts with a plain "How can we protect children…". The Calibri text must be excluded. *Claude's call:* the target for every file is the text **visible on the rendered page**. The script reports, for every file, any characters whose font or size differs from the passage's main body font, so that hidden or stray layers are detected rather than avoided by luck.
  - **No new paper has a heading inside the passage.** "Pet care and self-care are linked." (2020-09) is the first sentence of a paragraph; the earlier note that it was a subheading came from interleaved columns.
  - The rule from §5 still stands for any heading the script does find: drop it and list it.
- **Fragility:** the source is a third-party site, so links may change. The script records each URL and the SHA-256 hash of each downloaded PDF in the sources file.

## 7. Left to the builder

- Script name and structure; whether the Phase 2 rerun is a separate step.
- The exact layout heuristics, provided they are tested on the known cases above.
- The format of the review report (Markdown is fine).
