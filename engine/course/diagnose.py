"""Explains WHY an attempt failed and WHERE (under which conditions), then picks the next fix."""
from __future__ import annotations

from collections import Counter

import numpy as np

from . import features as F
from .learner import MODEL_LADDER, MODEL_PLAIN, Strategy


def weakest_condition(meta, correct):
    """Find the slice of examples (e.g. 'snr_db between -18 and -12') where it fails most."""
    overall = 1 - correct.mean()
    best = None
    keys = {k for m in meta for k in m}
    for k in sorted(keys):
        v = np.array([m.get(k, np.nan) for m in meta], float)
        ok = ~np.isnan(v)
        if ok.sum() < 20 or np.unique(v[ok]).size < 4:
            continue
        edges = np.quantile(v[ok], [0, .25, .5, .75, 1])
        for lo, hi in zip(edges[:-1], edges[1:]):
            sel = ok & (v >= lo) & (v <= hi)
            if sel.sum() < 5:
                continue
            rate = 1 - correct[sel].mean()
            if best is None or rate > best["error_rate"]:
                best = dict(key=k, lo=float(lo), hi=float(hi), error_rate=float(rate), n=int(sel.sum()))
    if best and best["error_rate"] >= max(1.5 * overall, overall + 0.1):
        return best
    return None


def top_confusions(y_true, y_pred, k=3):
    c = Counter((t, p) for t, p in zip(y_true, y_pred) if t != p)
    return [dict(true=t, pred=p, count=n) for (t, p), n in c.most_common(k)]


def per_class_error(y_true, correct):
    out = {}
    for c in sorted(set(y_true)):
        sel = np.asarray(y_true) == c
        out[str(c)] = float(1 - correct[sel].mean())
    return out


def diagnose(task, train_score, test_score, threshold, meta, y_true, y_pred, correct):
    reasons, why = [], []
    gap = train_score - test_score
    if train_score < threshold:
        reasons.append("underfit")
        why.append(f"It can't even get its own practice examples right ({train_score:.0%} on training data). "
                   "The way it looks at the signal can't tell the cases apart yet.")
    elif gap > 0.05:
        reasons.append("overfit")
        why.append(f"It memorised the practice set ({train_score:.0%}) but does worse on hidden examples "
                   f"({test_score:.0%}). It needs more varied examples.")
    else:
        reasons.append("close")
        why.append(f"It understands the idea but isn't precise enough yet ({test_score:.0%} vs {threshold:.0%} needed).")
    where = weakest_condition(meta, correct)
    if where:
        reasons.append("weak_condition")
    details = dict(train_score=train_score, test_score=test_score, gap=gap, where=where)
    if task == "classify":
        details["confusions"] = top_confusions(y_true, y_pred)
        details["per_class_error"] = per_class_error(y_true, correct)
        if details["confusions"]:
            c = details["confusions"][0]
            why.append(f"Most common mix-up: called '{c['true']}' a '{c['pred']}' ({c['count']} times).")
    if where:
        why.append(f"Fails most when {where['key']} is {where['lo']:.3g}–{where['hi']:.3g} "
                   f"({where['error_rate']:.0%} wrong there vs {1 - correct.mean():.0%} overall).")
    return reasons, " ".join(why), details


def choose_fix(task, kind, strat: Strategy, reasons, details, base_n, max_n_factor=8):
    """Return (new strategy, plain-English description of the fix)."""
    s = Strategy(**{k: (list(v) if isinstance(v, list) else v) for k, v in strat.as_dict().items()})
    s.history = strat.history + [strat.plain()]
    all_sets = F.feature_names(kind)
    unused = [f for f in all_sets if f not in s.features]
    ladder = MODEL_LADDER[task]
    fixes = []

    def more_data():
        if s.n_train < base_n * max_n_factor:
            s.n_train *= 2
            fixes.append(f"double the practice set to {s.n_train} examples")
            return True
        return False

    def next_feature():
        if unused:
            s.features.append(unused[0])
            fixes.append(f"start looking at '{unused[0]}' features too")
            return True
        return False

    def upgrade_model():
        i = ladder.index(s.model)
        if i + 1 < len(ladder):
            s.model = ladder[i + 1]
            fixes.append(f"switch to {MODEL_PLAIN[s.model]}")
            return True
        return False

    if "underfit" in reasons:
        next_feature() or upgrade_model() or more_data()
    elif "overfit" in reasons:
        more_data() or upgrade_model()
    else:
        (upgrade_model() if s.model == ladder[0] else False) or next_feature() or more_data()

    if "weak_condition" in reasons and details.get("where"):
        w = details["where"]
        s.focus = dict(key=w["key"], lo=w["lo"], hi=w["hi"])
        fixes.append(f"generate extra examples where {w['key']} is {w['lo']:.3g}–{w['hi']:.3g}")
    if s.mistake_weight < 3:
        s.mistake_weight = min(3.0, s.mistake_weight + 1.0)
    fixes.append(f"re-study this round's mistakes at {s.mistake_weight:g}x weight")
    if not fixes[:-1]:
        fixes.insert(0, "nothing left to unlock; retry with fresh examples")
    return s, "; ".join(fixes)
