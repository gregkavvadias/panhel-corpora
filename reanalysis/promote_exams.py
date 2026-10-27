# Copy Greg-approved exam passages from staging/Panhellenics/ into Texts/Panhellenics/.
# Every approved file is checked before anything is copied, so a conflict leaves the corpus untouched.
import csv, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

def promote(staging, target, approvals):
    """Copy approved files whose content matches the approved sha256; return the ones copied.
    Identical targets are skipped; differing ones refuse."""
    staging, target = Path(staging), Path(target)
    with Path(approvals).open(encoding='utf-8-sig', newline='') as fh:
        approved = [(r['file'], r['sha256']) for r in csv.DictReader(fh)]
    todo = []
    for f, sha in approved:
        src, dst = staging / f'{f}.txt', target / f'{f}.txt'
        if not src.exists():
            raise FileNotFoundError(f'{f}: approved but not in {staging}')
        if hashlib.sha256(src.read_bytes()).hexdigest() != sha:
            raise ValueError(f'{f}: staging content differs from the approved version (sha256); needs re-approval')
        if dst.exists():
            if dst.read_bytes() != src.read_bytes():
                raise FileExistsError(f'{f}: {dst} exists with different content; not overwriting')
            continue
        todo.append((f, src, dst))
    for f, src, dst in todo:
        dst.write_bytes(src.read_bytes())
    return [f for f, _, _ in todo]

if __name__ == '__main__':
    print(promote(HERE / 'staging' / 'Panhellenics', HERE.parent / 'Texts' / 'Panhellenics',
                  HERE / 'data' / 'exam_approvals.csv'))
