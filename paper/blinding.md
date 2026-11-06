# Blinding key (not for submission)

Since 6 Nov 2026 the manuscript files are the non-blinded master copy. `python paper/tools/build_pdf.py --blind` produces the review copy (`paper/build/manuscript-blinded.pdf`): it drops the author block and bio and applies the substitutions below in reverse. Check the blinded PDF before submission (any new self-reference must be added to `blind()` in `build_pdf.py`).

| Placeholder | Real value |
|---|---|
| `[Author]` | Grigorios Kavvadias |
| `[Author, 2023]` | Kavvadias, G. (2023). *A computational comparative analysis of text difficulty in the Greek high school English coursebooks and the national university entrance examinations for English* [Master's dissertation, Hellenic Open University]. |
| `[anonymised repository link]` | https://github.com/gregkavvadias/panhel-corpora (for review: an anonymised mirror, e.g. via anonymous.4open.science) |
| `[affiliation]` | to be supplied by Greg |
| About the author (RFL: at most 50 words, sentence format; removed for blind review) | to be supplied by Greg at submission |
