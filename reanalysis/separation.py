# Phase 4 RQ2 (a): which open measures separate exam from coursebook texts?
# Elastic-net logistic regression, nested CV (outer leave-one-out, inner stratified 5-fold); see the Phase 4 spec.
import warnings
from contextlib import contextmanager
import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import LeaveOneOut, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from corpus import is_exam

FEATURES = ['cov5k', 'conc_tok', 'imag', 'fam', 'mtld', 'hdd', 'mlc', 'clauses_per_sent', 'mean_sent_len',
            'passive_inc', 'np_inc', 'vp_inc', 'adjp_inc', 'pp_inc', 'neg_inc', 'gerund_inc', 'inf_inc',
            'cwo_adj', 'sem_overlap', 'conn_inc', 'causal_inc']

def design(F, school_version='full'):
    """X (21 features), y (exam = 1) and row ids: exam texts in full, school texts in the given version."""
    exam = F.book.map(is_exam)
    D = F[(exam & (F.version == 'full')) | (~exam & (F.version == school_version))]
    return D[FEATURES].to_numpy(float), D.book.map(is_exam).astype(int).to_numpy(), list(D.book + '/' + D.text)

def make_model():
    return make_pipeline(StandardScaler(), LogisticRegressionCV(
        Cs=np.logspace(-2, 2, 9), l1_ratios=[0.1, 0.5, 0.9], penalty='elasticnet', solver='saga',
        cv=StratifiedKFold(5, shuffle=True, random_state=1), scoring='neg_log_loss', max_iter=5000))

@contextmanager
def _quiet():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', ConvergenceWarning); warnings.simplefilter('ignore', FutureWarning)
        yield

def nested_cv(X, y):
    """Leave-one-out predictions with the penalty chosen inside each training fold; scaler fitted per fold."""
    prob = np.empty(len(y)); selected = np.zeros((len(y), X.shape[1]), bool)
    with _quiet():
        for i, (tr, te) in enumerate(LeaveOneOut().split(X)):
            m = make_model().fit(X[tr], y[tr])
            prob[te] = m.predict_proba(X[te])[:, 1]
            selected[i] = m[-1].coef_.ravel() != 0
    pred = (prob >= 0.5).astype(int)
    return dict(prob=prob, selected=selected, accuracy=accuracy_score(y, pred),
                balanced_accuracy=balanced_accuracy_score(y, pred), auc=roc_auc_score(y, prob))

def final_fit(X, y):
    """Fit on all texts (penalty chosen by the same inner CV); standardised coefficients."""
    with _quiet():
        m = make_model().fit(X, y)
    lr = m[-1]
    return dict(coef=lr.coef_.ravel(), C=float(np.ravel(lr.C_)[0]), l1_ratio=float(np.ravel(lr.l1_ratio_)[0]))

def _null_auc(X, y, i):
    return nested_cv(X, np.random.default_rng(1 + i).permutation(y))['auc']

def permutation_p(X, y, observed_auc, n_perm=200, n_jobs=-1):
    """Permutation test of the cross-validated AUC: labels shuffled, the whole nested procedure rerun each time."""
    from joblib import Parallel, delayed
    null = np.array(Parallel(n_jobs=n_jobs)(delayed(_null_auc)(X, y, i) for i in range(n_perm)))
    return {'p': (1 + np.sum(null >= observed_auc)) / (1 + n_perm), 'null_aucs': null}

def main(n_perm=200):
    import time
    import pandas as pd
    from stats6 import load_features
    F = load_features()
    summary, feats = [], []
    for version in ('full', 'first360'):
        t = time.time()
        X, y, _ = design(F, version)
        cv = nested_cv(X, y)
        perm = permutation_p(X, y, cv['auc'], n_perm)
        fit = final_fit(X, y)
        summary.append(dict(version=version, n_school=int((y == 0).sum()), n_exam=int(y.sum()),
                            accuracy=cv['accuracy'], balanced_accuracy=cv['balanced_accuracy'], auc=cv['auc'],
                            perm_p=perm['p'], n_perm=n_perm, C=fit['C'], l1_ratio=fit['l1_ratio'],
                            minutes=round((time.time() - t) / 60, 1)))
        pct = 100 * cv['selected'].mean(axis=0)
        feats += [dict(version=version, feature=f, selected_pct=p, coef=c, interpret=p >= 80)
                  for f, p, c in zip(FEATURES, pct, fit['coef'])]
        print(summary[-1], flush=True)
    pd.DataFrame(summary).to_csv('results/separation_summary.csv', index=False)
    P = pd.DataFrame(feats); P.to_csv('results/separation_features.csv', index=False)
    print(P.sort_values(['version', 'selected_pct'], ascending=[True, False]).round(3).to_string(index=False))

if __name__ == '__main__':
    main()
