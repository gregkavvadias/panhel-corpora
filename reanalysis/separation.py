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
