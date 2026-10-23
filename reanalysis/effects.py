# Effect sizes as in stats1.py; direction is b - a (exam - school).
import numpy as np

def hedges(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    return (np.mean(b) - np.mean(a)) / sp * (1 - 3 / (4 * (na + nb) - 9))

def boot_ci(a, b, B=5000, seed=1):
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a), np.asarray(b)
    g = [hedges(rng.choice(a, len(a)), rng.choice(b, len(b))) for _ in range(B)]
    lo, hi = np.percentile(g, [2.5, 97.5])
    return float(lo), float(hi)
