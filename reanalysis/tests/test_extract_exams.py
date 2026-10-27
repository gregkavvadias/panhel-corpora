import pytest
from extract_exams import (style, passage_lines, is_end_marker, paragraphs, clean, apply_corrections,
                           suspects, split_headings, write_text, extract, load_sources, PDFS, SOURCES,
                           group_lines, overlapping_lines)

def W(text, x0, top, font='GCNONE+ArialMT', size=10.0):
    return dict(text=text, x0=x0, x1=x0 + 6 * len(text), top=top, bottom=top + 10, fontname=font, size=size)

def L(text, x0, x1, top):
    return dict(text=text, x0=x0, x1=x1, top=top, bottom=top + 10)

def test_style_family_and_size():
    assert style(W('a', 0, 0, 'GCNONE+ArialMT', 10.04)) == ('Arial', 10.0)
    assert style(W('a', 0, 0, 'Arial,Bold', 11)) == ('Arial', 11.0)
    assert style(W('a', 0, 0, 'ABCDEF+Helvetica-Bold', 11)) == ('Helvetica', 11.0)

def test_offstyle_words_are_dropped_and_reported():
    ws = [W('Read the text below', 50, 100), W('Visible', 50, 120), W('words', 100, 120),
          W('hidden', 50, 140, font='GCNOLO+Calibri', size=11)]
    lines, dropped = passage_lines(ws, 600, 1)
    assert [l['text'] for l in lines] == ['Visible words'] and dropped == ['hidden']

def test_two_columns_read_left_then_right():
    ws = [W('Read the text below', 50, 100),
          W('left1', 50, 120), W('right1', 320, 120), W('left2', 50, 135), W('right2', 320, 135)]
    lines, _ = passage_lines(ws, 600, 2)
    assert [l['text'] for l in lines] == ['left1', 'left2', 'right1', 'right2']

def test_end_markers():
    for s in ['Adapted from', 'https://www.bbc.com (2022)', 'bbc.com', 'https://www.bbc focus.co.uk',
              '(2018)', '(June 2023)', 'ΤΕΛΟΣ 2ΗΣ ΑΠΟ 6 ΣΕΛΙΔΕΣ', 'Adapted from https://www.scientificamerican.com']:
        assert is_end_marker(s), s
    assert not is_end_marker('Pet care and self-care are linked. When')

def test_end_marker_ignores_long_body_line_with_domain():
    assert not is_end_marker('people now post their diaries on blogger.com and read them every day')

def test_paragraph_break_on_short_line():
    ls = [L('aaaa aaaa aaaa aaaa', 50, 450, 100), L('end.', 50, 120, 112), L('next para', 50, 450, 124)]
    ps, _ = paragraphs(ls)
    assert ps == ['aaaa aaaa aaaa aaaa end.', 'next para']

def test_paragraph_break_on_vertical_gap():
    ls = [L('one', 50, 440, 100), L('two', 50, 445, 112), L('three.', 50, 442, 124), L('new', 50, 450, 152)]
    assert paragraphs(ls)[0] == ['one two three.', 'new']

def test_dehyphenation_is_recorded():
    ls = [L('the class-', 50, 450, 100), L('room was', 50, 450, 112)]
    ps, dh = paragraphs(ls)
    assert ps == ['the classroom was'] and dh == ['classroom']

def test_clean_ligatures_and_soft_hyphen():
    assert clean('ﬁne  ﬂow co­operate') == 'fine flow cooperate'

def test_correction_applies_once():
    rows = [{'file': '2023-06', 'find': 'schooIs', 'replace': 'schools', 'note': ''}]
    assert apply_corrections('in schooIs or', '2023-06', rows) == 'in schools or'
    assert apply_corrections('in schooIs or', '2024-06', rows) == 'in schooIs or'

def test_correction_must_match_exactly_once():
    rows = [{'file': 'x', 'find': 'a', 'replace': 'b', 'note': ''}]
    with pytest.raises(ValueError, match="x.*'a'.*2"):
        apply_corrections('a a', 'x', rows)
    with pytest.raises(ValueError, match="x.*'a'.*0"):
        apply_corrections('zzz', 'x', rows)

def test_suspects():
    fam = {'school': 1, 'cat': 1, 'the': 1, 'had': 1, 'a': 1, 'how': 1, 'odd': 1}
    s = dict(suspects('The schooIs had a cat. H ow odd zqxv.', fam, {}))
    assert s['schooIs'] == 'capital-I' and s['zqxv'] == 'unknown' and s['H ow'] == 'split-letter'

def test_split_headings():
    ps, hs = split_headings(['Pet care and self-care', 'Pet care and self-care are linked.', 'A short one.'])
    assert hs == ['Pet care and self-care'] and ps == ['Pet care and self-care are linked.', 'A short one.']

def test_write_text_crlf_paragraphs(tmp_path):
    p = tmp_path / 't.txt'; write_text(p, ['One.', 'Two.'])
    assert p.read_bytes() == b'One.\r\n\r\nTwo.'

real = pytest.mark.skipif(not (PDFS / '2024-09.pdf').exists(), reason='exam PDFs not downloaded')

@real
def test_real_2024_09_excludes_hidden_layer():
    r = extract(PDFS / '2024-09.pdf', 1); text = ' '.join(r['paragraphs'])
    assert text.startswith('How can we protect children') and 'burdening' not in text
    assert 340 <= len(text.split()) <= 400 and r['dropped_offstyle']

@real
def test_real_2018_09_columns_in_order():
    text = ' '.join(extract(PDFS / '2018-09.pdf', 2)['paragraphs'])
    assert text.startswith('Many people would find long dark nights and bitter cold pretty depressing.')

@real
def test_real_2020_09_keeps_pet_care_sentence_in_paragraph():
    ps = extract(PDFS / '2020-09.pdf', 2)['paragraphs']
    assert any(p.startswith('Pet care and self-care are linked.') for p in ps)
    assert not any(p == 'Pet care and self-care' for p in ps)

@real
def test_real_all_word_counts_plausible():
    for row in load_sources(SOURCES):
        n = len(' '.join(extract(PDFS / f"{row['file']}.pdf", int(row['columns']))['paragraphs']).split())
        assert 300 <= n <= 420, (row['file'], n)

def test_superscript_attached_to_previous_word():
    ws = [W('Read the text below', 50, 100), W('10', 50, 120), W('th', 62, 119.7, size=7.0), W('graders', 80, 120)]
    lines, dropped = passage_lines(ws, 600, 1)
    assert [l['text'] for l in lines] == ['10th graders'] and dropped == []

def test_suspects_ignore_newlines_and_one_letter_words():
    fam = {'moved': 1, 'recent': 1, 'b': 1}
    assert suspects('I moved.\n\nA recent b', fam, {}) == []

def test_end_marker_footer_half():
    assert is_end_marker('ΑΠΟ 6 ΣΕΛΙΔΕΣ')

def test_dehyphenation_keeps_hyphen_in_compound_when_lexicon_says_so():
    ls = [L('the problem-', 50, 450, 100), L('solving skills', 50, 450, 112)]
    ps, dh = paragraphs(ls, known={'problem', 'solving', 'skills', 'the'})
    assert ps == ['the problem-solving skills'] and dh == ['problem-solving']

@real
def test_real_2025_09_superscript_ordinal_kept():
    r = extract(PDFS / '2025-09.pdf', 1)
    assert '10th graders' in ' '.join(r['paragraphs']) and r['dropped_offstyle'] == []

def test_group_lines_joins_touching_words_without_space():
    ws = [W('mid', 50, 120), W('‐', 68, 120, font='X+Calibri'), W('winter', 74.2, 120), W('next', 120, 120)]
    assert group_lines(ws)[0]['text'] == 'mid‐winter next'

def test_overlapping_lines_reported():
    ls = [dict(L('visible one', 50, 450, 96), col=0), dict(L('u to look hidden', 50, 450, 108), col=0),
          dict(L('visible two', 50, 450, 112), col=0)]
    assert overlapping_lines(ls) == [('u to look hidden', 'visible two')]

@real
def test_real_2024_09_hidden_fragment_is_reported():
    r = extract(PDFS / '2024-09.pdf', 1)
    assert any(a.startswith('u to look at the world') for a, b in r['overlapping_lines'])

@real
def test_real_2018_09_hyphen_not_spaced():
    assert 'mid‐winter' in ' '.join(extract(PDFS / '2018-09.pdf', 2)['paragraphs'])

def test_corpus_2024_09_has_no_hidden_fragment():
    from corpus import TEXTS_DIR
    assert 'mediated through a screen' not in (TEXTS_DIR / 'Panhellenics' / '2024-09.txt').read_text(encoding='utf-8')
