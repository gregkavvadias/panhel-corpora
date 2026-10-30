# Coursebook and Panhellenic English reading texts: corpus, analysis and paper

This repository holds the data, code and manuscript for a study comparing the reading texts of the Greek state Lyceum English coursebooks (*English 1*, *English 2*) with the reading passages of the Panhellenic English examination (2010–2026).

## Contents

| Folder | What it holds |
|---|---|
| `Texts/` | The corpus: 28 coursebook reading texts (27 analysed) and 26 examination passages, one plain-text file each |
| `reanalysis/` | Analysis scripts, input data, results (`results/*.csv`) and tests. `reanalysis/README.md` documents every analysis and its findings |
| `paper/` | The manuscript in Markdown (one file per section), references, appendices, the generated numbers file, Figure 1 and the build tools |
| `docs/superpowers/` | Design specifications and implementation plans for each phase of the work |

## Reproducing the results

Run from `reanalysis/`, with Python 3.13:

```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python fetch_resources.py      # word lists and norms, which are not redistributed here
python -m pytest tests
```

Then run the scripts listed in `reanalysis/README.md` (`lexical.py`, `stats5.py`, `difficulty.py`, `stats6.py`, `separation.py`, `genre.py`). Back in the repository root, these commands regenerate the paper's numbers and outputs:

```
python paper/tools/numbers_build.py
python paper/tools/check_numbers.py paper/0*.md paper/appendices.md
python paper/figures/coverage.py
python paper/tools/build_pdf.py     # writes paper/build/manuscript.pdf (needs Chrome or Edge)
```

## Licence

The code and derived measures are released under CC0 1.0 (see `LICENSE`). The corpus texts are taken from coursebooks and examination papers that the Greek state makes publicly available; rights in those texts remain with their original holders. The lexical resources fetched by `fetch_resources.py` keep their own licences (see `reanalysis/data/SOURCES.md`).
