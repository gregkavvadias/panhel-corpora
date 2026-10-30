# Builds the blinded manuscript as HTML and PDF (paper/build/) from the paper's Markdown files.
# HTML comments (verification notes, number sources) are stripped; placeholders stay as they are.
# PDF is printed with headless Chrome or Edge. Usage: python paper/tools/build_pdf.py
import re
import shutil
import subprocess
from pathlib import Path
import markdown

PAPER = Path(__file__).resolve().parents[1]
ORDER = ['00-front.md', '01-introduction.md', '02-background.md', '03-method.md', '04-results.md',
         '05-discussion.md', '06-conclusion.md', 'references.md', 'appendices.md']
BROWSERS = [r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']

CSS = """
@page { size: A4; margin: 2.54cm; }
body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 2; }
h1 { font-size: 12pt; font-weight: bold; text-align: center; margin: 1.5em 0 0.5em; }
h1.title { font-size: 14pt; margin-top: 0; }
h2 { font-size: 12pt; font-weight: bold; margin: 1em 0 0; }
h3 { font-size: 12pt; font-weight: bold; font-style: italic; margin: 1em 0 0; }
p { margin: 0; text-indent: 0.5in; text-align: left; }
h1 + p, h2 + p, h3 + p, .noindent { text-indent: 0; }
table { border-collapse: collapse; margin: 0.5em 0; font-size: 10pt; line-height: 1.3; width: 100%; }
.float { break-inside: avoid; page-break-inside: avoid; margin: 0.5em 0 1em; }
.float p { line-height: 1.5; }
th, td { padding: 3px 6px; text-align: left; vertical-align: top; }
thead tr { border-top: 1px solid black; border-bottom: 1px solid black; }
tbody tr:last-child { border-bottom: 1px solid black; }
img { max-width: 100%; display: block; margin: 0.5em auto; }
.refs p { text-indent: -0.5in; padding-left: 0.5in; }
.pagebreak { page-break-before: always; }
"""

def section_html(name, text):
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    html = markdown.markdown(text, extensions=['tables'])
    if name == '00-front.md':
        html = html.replace('<h1>', '<h1 class="title">', 1)
        html = html.replace('<p>[Author]\n[affiliation]</p>', '<p class="noindent" style="text-align:center">[Author]<br>[affiliation]</p>')
    if name == 'references.md':
        html = f'<div class="refs">{html}</div>'
    # APA captions: "Table N" in bold on its own line, title in italics below, unindented
    html = re.sub(r'<p><strong>(Table|Figure) (\d+)</strong>\s*', r'<p class="noindent"><strong>\1 \2</strong><br>', html)
    html = html.replace('<p><em>Note.</em>', '<p class="noindent"><em>Note.</em>')
    # keep caption, table or figure, and note together on one page
    html = re.sub(r'(<p class="noindent"><strong>(?:Table|Figure) \d+</strong>.*?</p>\s*'
                  r'(?:<table>.*?</table>|<p><img[^>]*></p>)(?:\s*<table>.*?</table>)*'
                  r'(?:\s*<p class="noindent"><em>Note\.</em>.*?</p>)?)',
                  r'<div class="float">\1</div>', html, flags=re.S)
    breaks = {'01-introduction.md', 'references.md', 'appendices.md'}
    return (f'<div class="pagebreak"></div>' if name in breaks else '') + html

def build():
    out = PAPER / 'build'
    out.mkdir(exist_ok=True)
    (out / 'figures').mkdir(exist_ok=True)
    for f in (PAPER / 'figures').glob('*.png'):
        shutil.copy(f, out / 'figures' / f.name)
    title = re.search(r'^# (.+)$', (PAPER / '00-front.md').read_text(encoding='utf-8'), re.M).group(1)
    intro = (PAPER / '01-introduction.md').read_text(encoding='utf-8')
    body = ''.join(section_html(n, (PAPER / n).read_text(encoding='utf-8') if n != '01-introduction.md'
                                else f'# {title}\n\n' + intro) for n in ORDER)
    html_path = out / 'manuscript.html'
    html_path.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
                         f'<style>{CSS}</style></head><body>{body}</body></html>', encoding='utf-8')
    browser = next((b for b in BROWSERS if Path(b).exists()), None)
    if browser is None:
        raise SystemExit(f'wrote {html_path}; no Chrome/Edge found for PDF')
    pdf = out / 'manuscript.pdf'
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf}', html_path.as_uri()], check=True, capture_output=True)
    print(f'wrote {pdf}')

if __name__ == '__main__':
    build()
