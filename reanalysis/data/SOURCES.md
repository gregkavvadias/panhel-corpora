# External resources

These are downloaded by `python fetch_resources.py` and are not committed, because their redistribution terms are unclear.

## BNC/COCA word-family lists

- **Download:** https://www.laurenceanthony.net/software/wordfamilyfinder/downloads/basewords_130.zip, saved to `data/bnc_coca/basewrd1.txt` … `basewrd35.txt`
- **Version:** basewords 1.3.0, as distributed with Laurence Anthony's WordFamilyFinder
- **Downloaded:** 2026-10-23
- **Citation:** Nation, I. S. P. (2017). *The BNC/COCA Level 6 word family lists* (Version 1.0.0) [Data file]. Victoria University of Wellington. The version used here is the basewords 1.3.0 distribution by L. Anthony.
- **Format:** UTF-8 with CRLF line endings. An unindented line holds a headword and its frequency. A tab-indented line holds a family member and its frequency.
- **What each list is:**

| Lists | Content | Treatment |
|---|---|---|
| 1–30 | Frequency bands of 1,000 families each | band *k* |
| 31 | Proper nouns | proper noun |
| 32 | Marginal words (interjections, letters, swearwords, some prefixes) | supplementary, counted as known |
| 33 | Transparent compounds | supplementary, counted as known |
| 34 | Abbreviations and acronyms | supplementary, counted as known |
| 35 | Accented spellings (e.g. *café*, *fête*) | supplementary, counted as known |

## Concreteness norms

- **Download:** https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-013-0403-5/MediaObjects/13428_2013_403_MOESM1_ESM.xlsx (supplementary material S1), saved to `data/brysbaert_concreteness.xlsx`. The older crr.ugent.be text file now returns 404.
- **Downloaded:** 2026-10-23 (39,954 rows)
- **Citation:** Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. *Behavior Research Methods, 46*(3), 904–911. https://doi.org/10.3758/s13428-013-0403-5
- **Columns used:** `Word` and `Conc.M` (1 = abstract, 5 = concrete). Multiword entries are ignored.

## NLP environment for Phase 2

- spaCy 3.8.16
- en_core_web_sm 3.8.0
