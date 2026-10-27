from extract_exams import style, passage_lines, is_end_marker, paragraphs, clean

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
