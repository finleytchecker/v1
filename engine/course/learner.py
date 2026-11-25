"""The student: a local scikit-learn model plus a 'strategy' it changes after each fail."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import features as F

MODEL_LADDER = {
    "classify": ["logistic", "random_forest", "gradient_boosting"],
    "regress": ["ridge", "random_forest", "gradient_boosting"],
}

MODEL_PLAIN = {
    "logistic": "straight-line boundaries (logistic regression)",
    "ridge": "a straight-line fit (ridge regression)",
    "random_forest": "a forest of decision trees",
    "gradient_boosting": "boosted trees that fix each other's errors",
}


def make_model(task, name, seed):
    if task == "classify":
        m = {"logistic": LogisticRegression(max_iter=2000),
             "random_forest": RandomForestClassifier(300, random_state=seed, n_jobs=-1),
             "gradient_boosting": HistGradientBoostingClassifier(random_state=seed)}[name]
    else:
        m = {"ridge": Ridge(1e-3),
             "random_forest": RandomForestRegressor(300, random_state=seed, n_jobs=-1),
             "gradient_boosting": HistGradientBoostingRegressor(random_state=seed)}[name]
    return make_pipeline(StandardScaler(), m)


@dataclass
class Strategy:
    features: list[str]
    model: str
    n_train: int
    focus: dict | None = None          # {"key": .., "lo": .., "hi": ..} -> extra examples of a weak condition
    mistake_weight: float = 1.0        # extra weight on examples it got wrong before
    history: list[str] = field(default_factory=list)

    def as_dict(self):
        return dict(features=list(self.features), model=self.model, n_train=self.n_train,
                    focus=self.focus, mistake_weight=self.mistake_weight)

    def plain(self):
        s = f"looked at [{', '.join(self.features)}] using {MODEL_PLAIN[self.model]}, trained on {self.n_train} examples"
        if self.focus:
            s += f", with extra practice where {self.focus['key']} is {self.focus['lo']:.3g}–{self.focus['hi']:.3g}"
        if self.mistake_weight > 1:
            s += f", re-studying past mistakes at {self.mistake_weight:g}x weight"
        return s


def score(task, y_true, y_pred, tol_rel=0.0, tol_abs=0.0):
    """Main score is accuracy (classify) or share of answers within tolerance (regress)."""
    if task == "classify":
        avg = "macro"
        return dict(score=float(accuracy_score(y_true, y_pred)),
                    precision=float(precision_score(y_true, y_pred, average=avg, zero_division=0)),
                    recall=float(recall_score(y_true, y_pred, average=avg, zero_division=0)))
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    err = np.abs(y_pred - y_true)
    ok = err <= np.maximum(tol_rel * np.abs(y_true), tol_abs)
    return dict(score=float(ok.mean()), mae=float(err.mean()), median_err=float(np.median(err)))


def correct_mask(task, y_true, y_pred, tol_rel=0.0, tol_abs=0.0):
    if task == "classify":
        return np.asarray(y_true) == np.asarray(y_pred)
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    return np.abs(y_pred - y_true) <= np.maximum(tol_rel * np.abs(y_true), tol_abs)


def fit_predict(task, kind, strat: Strategy, Xtr, ytr, wtr, Xte, seed):
    Ftr = F.extract(kind, Xtr, strat.features)
    Fte = F.extract(kind, Xte, strat.features)
    model = make_model(task, strat.model, seed)
    last = model.steps[-1][0]
    model.fit(Ftr, ytr, **{f"{last}__sample_weight": wtr})
    return model, model.predict(Ftr), model.predict(Fte)
