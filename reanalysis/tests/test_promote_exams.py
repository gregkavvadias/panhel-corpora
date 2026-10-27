import hashlib
import pytest
from promote_exams import promote

@pytest.fixture
def dirs(tmp_path):
    s, t = tmp_path / 's', tmp_path / 't'; s.mkdir(); t.mkdir()
    (s / 'a.txt').write_text('A'); (s / 'b.txt').write_text('B')
    ap = tmp_path / 'ap.csv'
    ap.write_text(f"file,approved_by,date,sha256\na,Greg,2026-10-27,{hashlib.sha256(b'A').hexdigest()}\n")
    return s, t, ap

def test_promote_only_approved(dirs):
    s, t, ap = dirs
    assert promote(s, t, ap) == ['a'] and (t / 'a.txt').read_text() == 'A' and not (t / 'b.txt').exists()

def test_promote_refuses_to_overwrite_different_file(dirs):
    s, t, ap = dirs; (t / 'a.txt').write_text('OLD')
    with pytest.raises(FileExistsError, match='a'):
        promote(s, t, ap)
    assert (t / 'a.txt').read_text() == 'OLD'

def test_promote_identical_target_is_noop(dirs):
    s, t, ap = dirs; (t / 'a.txt').write_text('A')
    assert promote(s, t, ap) == []

def test_promote_missing_staging_file(dirs, tmp_path):
    s, t, _ = dirs
    ap = tmp_path / 'ap2.csv'; ap.write_text('file,approved_by,date,sha256\nc,Greg,2026-10-27,x\n')
    with pytest.raises(FileNotFoundError, match='c'):
        promote(s, t, ap)

def test_promote_refuses_when_content_differs_from_approved_hash(tmp_path):
    import hashlib
    s, t = tmp_path / 's', tmp_path / 't'; s.mkdir(); t.mkdir()
    (s / 'a.txt').write_text('CHANGED')
    ap = tmp_path / 'ap.csv'
    ap.write_text(f"file,approved_by,date,sha256\na,Greg,2026-10-27,{hashlib.sha256(b'A').hexdigest()}\n")
    with pytest.raises(ValueError, match='a'):
        promote(s, t, ap)
    assert not (t / 'a.txt').exists()
