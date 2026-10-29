import pytest
from genre import load_labels

TEXTS = {('English 1', 'u1'), ('Panhellenics', '2010-06')}
HEAD = 'book,text,fine,coarse,reason,status\n'

def test_load_labels_ok(tmp_path):
    p = tmp_path / 'g.csv'
    p.write_text(HEAD + 'English 1,u1,fiction,narrative,a story,confirmed\n'
                        'Panhellenics,2010-06,informational,non-narrative,explains a study,confirmed\n')
    assert len(load_labels(p, TEXTS)) == 2

@pytest.mark.parametrize('rows, msg', [
    ('English 1,u1,poem,narrative,x,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,fiction,non-narrative,x,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,other,,x,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,fiction,narrative,,confirmed\nPanhellenics,2010-06,informational,non-narrative,x,confirmed\n', 'u1'),
    ('English 1,u1,fiction,narrative,x,confirmed\n', '2010-06'),
])
def test_load_labels_validation_errors(tmp_path, rows, msg):
    p = tmp_path / 'g.csv'; p.write_text(HEAD + rows)
    with pytest.raises(ValueError, match=msg):
        load_labels(p, TEXTS)

def test_load_labels_requires_confirmed(tmp_path):
    p = tmp_path / 'g.csv'
    p.write_text(HEAD + 'English 1,u1,fiction,narrative,x,proposed\n'
                        'Panhellenics,2010-06,informational,non-narrative,x,confirmed\n')
    with pytest.raises(ValueError, match='u1'):
        load_labels(p, TEXTS)
    assert len(load_labels(p, TEXTS, require_confirmed=False)) == 2
