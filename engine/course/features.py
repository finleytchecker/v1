"""Feature sets: the different 'ways of looking' at a signal that a learner can use.

The learner starts with the crudest one and unlocks better ones when it fails because
it can't tell examples apart (underfitting). Each set is listed from simplest to richest,
so you can watch it discover, e.g., that looking at the spectrum beats looking at raw numbers.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sps
from scipy.stats import kurtosis, skew

FS_TRACE = 1000.0
FS_DAS = 500.0
DX = 2.0


def _spectrum(x, fs):
    f, p = sps.welch(x, fs=fs, nperseg=min(256, x.shape[-1]), axis=-1)
    return f, p


def _spec_feats(f, p, fmin=0.0):
    m = f >= fmin
    f, p = f[m], p[m]
    i = int(np.argmax(p))
    # parabolic interpolation of the peak for sub-bin accuracy
    if 0 < i < len(p) - 1:
        a, b, c = np.log(p[i - 1] + 1e-20), np.log(p[i] + 1e-20), np.log(p[i + 1] + 1e-20)
        off = 0.5 * (a - c) / (a - 2 * b + c + 1e-20)
    else:
        off = 0.0
    df = f[1] - f[0]
    peak = f[i] + off * df
    ps = p / (p.sum() + 1e-20)
    centroid = (f * ps).sum()
    bw = np.sqrt(((f - centroid) ** 2 * ps).sum())
    flat = np.exp(np.mean(np.log(p + 1e-20))) / (p.mean() + 1e-20)
    prom = p[i] / (np.median(p) + 1e-20)
    roll = f[np.searchsorted(np.cumsum(ps), 0.85)]
    return [peak, centroid, bw, flat, np.log10(prom), roll]


def _bandpower(f, p, nb=12):
    edges = np.logspace(np.log10(max(f[1], 1)), np.log10(f[-1]), nb + 1)
    return [np.log10(p[(f >= lo) & (f < hi)].sum() + 1e-20) for lo, hi in zip(edges[:-1], edges[1:])]


# ------------------------------------------------------------------ trace (1-D signals)

def trace_raw_stats(x):
    return [x.mean(), x.std(), x.min(), x.max(), skew(x), kurtosis(x)]


def trace_spectral(x):
    return _spec_feats(*_spectrum(x, FS_TRACE))


def trace_spectral_highpass(x):
    """Spectrum features after ignoring everything below 20 Hz (a 'filter')."""
    return _spec_feats(*_spectrum(x, FS_TRACE), fmin=20.0)


def trace_bandpower(x):
    return _bandpower(*_spectrum(x, FS_TRACE))


def trace_envelope(x):
    env = np.abs(sps.hilbert(x))
    return [env.max() / (env.mean() + 1e-12), env.std() / (env.mean() + 1e-12), kurtosis(env)]


def trace_time_frequency(x):
    """How the main frequency moves over time (chirps sweep, tones don't)."""
    f, t, s = sps.spectrogram(x, fs=FS_TRACE, nperseg=128, noverlap=64)
    pk = f[np.argmax(s, axis=0)]
    slope = np.polyfit(t, pk, 1)[0] if len(t) > 1 else 0.0
    return [slope, pk.std(), np.ptp(pk)]


# ------------------------------------------------------------------ waterfall (channels x time)

def wf_raw_stats(w):
    return [w.mean(), w.std(), np.abs(w).max(), kurtosis(w.ravel())]


def wf_spectral(w):
    f, p = _spectrum(w, FS_DAS)
    return _spec_feats(f, p.mean(axis=0))


def wf_bandpower(w):
    f, p = _spectrum(w, FS_DAS)
    return _bandpower(f, p.mean(axis=0), nb=8)


def wf_spatial(w):
    e = (w ** 2).mean(axis=1)
    en = e / (np.median(e) + 1e-12)
    above = (en > 0.5 * en.max()).sum()
    return [en.max(), en.std(), np.argmax(e) / len(e), above / len(e)]


def wf_local_spectral(w):
    """Spectrum at the loudest spot, compared to the cable's typical spectrum.
    A leak shows up as a sharp, steady peak at one place."""
    f, p = _spectrum(w, FS_DAS)
    med = np.median(p, axis=0) + 1e-20
    ratio = p / med
    band = (f > 40)
    score = ratio[:, band].max(axis=1)
    ch = int(np.argmax(score))
    sf = _spec_feats(f, p[ch])
    return [np.log10(score.max()), np.log10(np.median(score)), ch, sf[0], sf[3], sf[4]]


def wf_stationarity(w):
    """Is the energy at the loudest channel steady (leak) or bursty (digging) or passing (traffic)?"""
    e = (w ** 2).mean(axis=1)
    ch = int(np.argmax(e))
    seg = w[ch].reshape(16, -1)
    se = (seg ** 2).mean(axis=1)
    return [se.std() / (se.mean() + 1e-12), se.max() / (se.mean() + 1e-12)]


def wf_moveout(w):
    """Track where the energy is over time. A straight moving line = a vehicle; the slope is its speed."""
    nch, nt = w.shape
    win = 32
    env = (w[:, : nt // win * win] ** 2).reshape(nch, -1, win).mean(axis=2)
    env = env - np.median(env, axis=1, keepdims=True)
    env = np.clip(env, 0, None) + 1e-12
    pos = np.arange(nch)[:, None]
    cen = (env * pos).sum(axis=0) / env.sum(axis=0)
    t = (np.arange(env.shape[1]) + 0.5) * win / FS_DAS
    wts = env.max(axis=0)
    slope = np.polyfit(t, cen, 1, w=np.sqrt(wts))[0]
    resid = np.sqrt(np.average((cen - np.polyval(np.polyfit(t, cen, 1, w=np.sqrt(wts)), t)) ** 2, weights=wts))
    return [abs(slope) * DX, resid]


# ------------------------------------------------------------------ props (rock property vectors)

def props_raw(v):
    return list(v)


def props_derived(v):
    """Geophysicists' favourite combinations: Vp/Vs, impedance, Poisson's ratio, lambda-rho, mu-rho."""
    vp, vs, rho = v[0], v[1], v[2]
    vpvs = vp / vs
    pr = (vpvs ** 2 - 2) / (2 * (vpvs ** 2 - 1))
    lam_rho = (vp * rho) ** 2 - 2 * (vs * rho) ** 2
    mu_rho = (vs * rho) ** 2
    return [vpvs, vp * rho, vs * rho, pr, lam_rho, mu_rho]


def props_log(v):
    return list(np.log(np.abs(v) + 1e-6))


# ------------------------------------------------------------------ gather (amplitude vs angle)
ANGLES = np.array([0, 5, 10, 15, 20, 25, 30, 35])


def gather_near(r):
    return [r[0]]


def gather_all(r):
    return list(r)


def gather_avo_fit(r):
    """Fit R = A + B sin^2(angle). Gas sands: A and B both negative (class III) or B strongly negative."""
    s2 = np.sin(np.radians(ANGLES)) ** 2
    b, a = np.polyfit(s2, r, 1)
    return [a, b, a * b, np.sign(a) * np.sign(b), b / (abs(a) + 1e-3)]


# ------------------------------------------------------------------ profile (sensors along surface)

def profile_raw_stats(x):
    return [x.mean(), x.std()]


def profile_rows(x):
    return [x[0].mean(), x[1].mean(), x[2].mean(), x[0].min(), x[1].min(), x[2].max()]


def profile_shadow(x):
    """Where S-waves drop out relative to their usual level, how deep the drop, and the P delay there."""
    from scipy.ndimage import uniform_filter1d
    p, s, d = (uniform_filter1d(r, 3) for r in x)
    s_ratio = s / (np.median(s) + 1e-6)
    i = int(np.argmin(s_ratio))
    width = (s_ratio < 0.5).sum()
    return [s_ratio.min(), width, d[i], d.max(), p[i] / (np.median(p) + 1e-6)]


FEATURE_SETS = {
    "trace": [
        ("raw_stats", trace_raw_stats),
        ("spectral", trace_spectral),
        ("envelope", trace_envelope),
        ("time_frequency", trace_time_frequency),
        ("bandpower", trace_bandpower),
        ("spectral_highpass", trace_spectral_highpass),
    ],
    "waterfall": [
        ("raw_stats", wf_raw_stats),
        ("spectral", wf_spectral),
        ("spatial", wf_spatial),
        ("stationarity", wf_stationarity),
        ("local_spectral", wf_local_spectral),
        ("moveout", wf_moveout),
        ("bandpower", wf_bandpower),
    ],
    "props": [("raw", props_raw), ("derived", props_derived), ("log", props_log)],
    "gather": [("near_angle", gather_near), ("all_angles", gather_all), ("avo_fit", gather_avo_fit)],
    "profile": [("raw_stats", profile_raw_stats), ("rows", profile_rows), ("shadow", profile_shadow)],
}


def feature_names(kind):
    return [n for n, _ in FEATURE_SETS[kind]]


def extract(kind, X, sets):
    funcs = dict(FEATURE_SETS[kind])
    rows = [np.concatenate([np.atleast_1d(np.asarray(funcs[s](x), float)) for s in sets]) for x in X]
    return np.nan_to_num(np.array(rows), nan=0.0, posinf=1e6, neginf=-1e6)
