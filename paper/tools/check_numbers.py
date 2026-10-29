# Lists numbers in a paper draft that no figure in paper/numbers.md rounds to.
# A draft number matches if some numbers.md value, rounded to the draft's decimal places, equals it.
# Ignored: integers <= 100, years 1900-2100, numbers right after "<" (thresholds), and lines with "<!-- source:".
import re
import sys
from pathlib import Path

NUM = re.compile(r'(?<![\w.])[-−]?(?:\d{1,3}(?:,\d{3})+|\d+)?(?:\.\d+)?(?![\w])')

def _tokens(text):
    for line in text.splitlines():
        if '<!-- source:' in line:
            continue
        for m in NUM.finditer(line):
            tok = m.group()
            if not re.search(r'\d', tok):
                continue
            if re.search(r'<\s*$', line[:m.start()]):
                continue
            yield tok

def _value(tok):
    return float(tok.replace('−', '-').replace(',', ''))

def _places(tok):
    return len(tok.split('.')[1]) if '.' in tok else 0

def unmatched(draft_text, numbers_text):
    known = [_value(t) for t in _tokens(numbers_text)]
    out = []
    for tok in _tokens(draft_text):
        v, places = _value(tok), _places(tok)
        if places == 0 and (abs(v) <= 100 or 1900 <= v <= 2100):
            continue
        if not any(round(k, places) == round(v, places) for k in known):
            out.append(tok.replace('−', '-'))
    return out

if __name__ == '__main__':
    nums = (Path(__file__).resolve().parents[1] / 'numbers.md').read_text(encoding='utf-8')
    for f in sys.argv[1:]:
        bad = unmatched(Path(f).read_text(encoding='utf-8'), nums)
        print(f'{f}: {"OK" if not bad else "unmatched " + ", ".join(bad)}')
