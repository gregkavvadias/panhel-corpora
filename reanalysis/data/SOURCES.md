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

## Glasgow Norms (Phase 3 part 2)

- **Download:** https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-018-1099-3/MediaObjects/13428_2018_1099_MOESM2_ESM.csv (supplementary material 2), saved to `data/glasgow_norms.csv`. Not committed, although the paper is CC BY 4.0, to keep resource handling uniform.
- **Downloaded:** 2026-10-27. The file has 5,553 words; 4,682 single-word entries remain after sense-tagged entries such as "bank (money)" are skipped.
- **Citation:** Scott, G. G., Keitel, A., Becirspahic, M., Yao, B., & Sereno, S. C. (2019). The Glasgow Norms: Ratings of 5,500 words on nine scales. *Behavior Research Methods, 51*(3), 1258–1270. https://doi.org/10.3758/s13428-018-1099-3
- **Columns used:** the IMAG and FAM means (scales 1–7).

## TAACO connective lists (Phase 3 part 2)

- **Download:** https://raw.githubusercontent.com/LCR-ADS-Lab/TAACO/ae5340c5385be849095f840004d70509d4732749/TAACOnoGUI.py (pinned commit of 2023-10-06), saved to `data/taaco/TAACOnoGUI.py`. Only the word lists are read from it; the code is not run.
- **Not committed:** the repository states no licence.
- **Citation:** Crossley, S. A., Kyle, K., & Dascalu, M. (2019). The Tool for the Automatic Analysis of Cohesion 2.0: Integrating semantic similarity and text overlap. *Behavior Research Methods, 51*(1), 14–27.

## Word vectors (Phase 3 part 2)

- **Model:** spaCy `en_core_web_md` 3.8.0, installed with `python -m spacy download en_core_web_md`.
- **Use:** its vectors only, for semantic overlap between sentences. All parsing uses `en_core_web_sm` 3.8.0.
