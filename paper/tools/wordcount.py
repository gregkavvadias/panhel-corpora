# Main-text word count of a paper section: excludes headings, Markdown tables, HTML comments,
# [CHECK ...] markers, fenced code and everything from a "References" heading on.
import re
import sys
from pathlib import Path

def count(md_text):
    text = re.sub(r'<!--.*?-->', ' ', md_text, flags=re.S)
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    text = re.sub(r'\[CHECK[^\]]*\]', ' ', text)
    m = re.search(r'^#+\s*References\s*$', text, flags=re.M | re.I)
    if m:
        text = text[:m.start()]
    lines = [l for l in text.splitlines() if not l.lstrip().startswith(('#', '|'))]
    return sum(1 for w in ' '.join(lines).split() if re.search(r'\w', w))

if __name__ == '__main__':
    total = 0
    for f in sys.argv[1:]:
        n = count(Path(f).read_text(encoding='utf-8')); total += n
        print(f'{n:6d}  {f}')
    print(f'{total:6d}  total')
