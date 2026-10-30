# Figure 1: mean lexical coverage by BNC/COCA frequency band, coursebook vs examination texts (full texts).
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

def coverage_table(results_dir):
    """Group means of 1k-9k coverage (%), one row per band."""
    sys.path.insert(0, str(ROOT / 'reanalysis'))
    from stats5 import thresholds
    T = thresholds(pd.read_csv(Path(results_dir) / 'lexical_features.csv')).set_index('group')
    rows = [dict(band=k, Coursebook=T.loc['school', f'cov{k}k'], Examination=T.loc['exam', f'cov{k}k']) for k in range(1, 10)]
    return pd.DataFrame(rows)

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    T = coverage_table(ROOT / 'reanalysis' / 'results')
    fig, ax = plt.subplots(figsize=(6, 3.6), dpi=300)
    ax.plot(T.band, T.Coursebook, marker='o', color='black', label='Coursebook (n = 27)')
    ax.plot(T.band, T.Examination, marker='s', linestyle='--', color='black', label='Examination (n = 26)')
    for th in (95, 98):
        ax.axhline(th, color='grey', linewidth=0.6, linestyle=':')
        ax.text(0.65, th + 0.4, f'{th}%', va='bottom', fontsize=8, color='grey')
    ax.set_xlim(0.5, 9.3)
    ax.set_xticks(range(1, 10), [f'{k}k' for k in range(1, 10)])
    ax.set_xlabel('BNC/COCA word-family band')
    ax.set_ylabel('Mean coverage (%)')
    ax.set_ylim(75, 100)
    ax.legend(frameon=False, loc='lower right')
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    out = ROOT / 'paper' / 'figures' / 'coverage.png'
    fig.savefig(out)
    print(f'wrote {out}')

if __name__ == '__main__':
    main()
