# Downloads the external lexical resources into data/ (gitignored; see data/SOURCES.md).
# urllib, not curl: on Windows curl's schannel revocation check fails for these hosts.
import io, sys, zipfile, urllib.request
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent / 'data'
FAMILIES_URL = 'https://www.laurenceanthony.net/software/wordfamilyfinder/downloads/basewords_130.zip'
NORMS_URL = ('https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-013-0403-5/'
             'MediaObjects/13428_2013_403_MOESM1_ESM.xlsx')
FAMILIES_DIR = DATA / 'bnc_coca'
NORMS_PATH = DATA / 'brysbaert_concreteness.xlsx'
GLASGOW_URL = ('https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-018-1099-3/'
               'MediaObjects/13428_2018_1099_MOESM2_ESM.csv')
GLASGOW_PATH = DATA / 'glasgow_norms.csv'
TAACO_URL = ('https://raw.githubusercontent.com/LCR-ADS-Lab/TAACO/'
             'ae5340c5385be849095f840004d70509d4732749/TAACOnoGUI.py')  # pinned commit; no licence stated, not committed
TAACO_PATH = DATA / 'taaco' / 'TAACOnoGUI.py'

def get(url):
    # the families host answers 406 to urllib's default User-Agent
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (panhel-corpora fetch_resources.py)'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def main():
    force = '--force' in sys.argv
    if force or not any(FAMILIES_DIR.glob('basewrd*.txt')):
        FAMILIES_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(get(FAMILIES_URL))) as z:
            for m in z.infolist():
                if m.filename.lower().endswith('.txt'):
                    (FAMILIES_DIR / Path(m.filename).name).write_bytes(z.read(m))
    if force or not NORMS_PATH.exists():
        NORMS_PATH.write_bytes(get(NORMS_URL))
    for url, path in ((GLASGOW_URL, GLASGOW_PATH), (TAACO_URL, TAACO_PATH)):
        if force or not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(get(url))
    lists = sorted(FAMILIES_DIR.glob('basewrd*.txt'))
    assert len(lists) == 35, f'expected 35 basewrd files, found {len(lists)}'
    norms = pd.read_excel(NORMS_PATH)
    assert {'Word', 'Conc.M'} <= set(norms.columns), norms.columns.tolist()
    print(f'{len(lists)} BNC/COCA list files in {FAMILIES_DIR}')
    print(f'{len(norms)} concreteness norm rows in {NORMS_PATH}')
    from difficulty import load_glasgow
    print(f'{len(load_glasgow(GLASGOW_PATH))} Glasgow single-word entries in {GLASGOW_PATH}')
    assert 'all_connective = ' in TAACO_PATH.read_text(encoding='utf-8'), 'TAACO lists not found'
    print(f'TAACO lists in {TAACO_PATH}')
    try:
        import en_core_web_md
        print(f'en_core_web_md {en_core_web_md.__version__} installed (word vectors)')
    except ImportError:
        print('en_core_web_md missing: run python -m spacy download en_core_web_md')

if __name__ == '__main__':
    main()
