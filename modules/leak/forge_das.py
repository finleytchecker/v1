"""Utah FORGE fiber-optic (DAS) data: reading, shrinking to features, and labelling from the event catalogue.

Raw files are huge (a 12-second Neubrex file is 288 MB). We never keep them: each file is cut into
1-second windows and each window becomes a small feature vector (energy in frequency bands along the
cable). That shrinks the data roughly 3000x.

Known answers: the FORGE microseismic catalogue (GDR 1817, absolute UTC times). A window is 'event' if a
catalogued event's origin time falls in it (or up to 1 s before, allowing travel time), else 'no_event'.
"""
from __future__ import annotations

import datetime as dt
import glob
import os
import re
import struct
from pathlib import Path

import numpy as np
from scipy import signal as sps

from engine.config import PROJECT_ROOT

FEAT_DIR = PROJECT_ROOT / "data" / "features" / "forge-das"
CATALOG = glob.glob(str(PROJECT_ROOT / "data/real/utah-forge-das/forge-das-catalog-phasepick-1817/*.csv"))
N_GROUPS = 32                                    # cable is binned into 32 stretches
BANDS = [(2, 10), (10, 30), (30, 80), (80, 200), (200, 500), (500, 1500)]
WIN_S = 1.0


# ------------------------------------------------------------------ reading

def read_segy(path):
    """Returns (data[channels, samples], sample_rate_hz). Handles the big-endian Silixa files and the
    little-endian Neubrex files whose sample-count header overflows."""
    try:
        import segyio
        with segyio.open(path, ignore_geometry=True) as s:
            return np.asarray(s.trace.raw[:], np.float32), 1e6 / segyio.tools.dt(s)
    except RuntimeError:
        pass
    size = os.path.getsize(path) - 3600
    with open(path, "rb") as f:
        head = f.read(3600)
    dt_us = struct.unpack("<H", head[3216:3218])[0]
    fmt = struct.unpack("<H", head[3224:3226])[0]
    if fmt != 5 or not dt_us:
        raise ValueError(f"unsupported SEG-Y layout in {path}")
    # the true trace length divides the file AND lands exactly on the next trace's header
    # (its trace-sequence number is one more than the first trace's)
    best = None
    with open(path, "rb") as f:
        f.seek(3600)
        seq0 = struct.unpack("<i", f.read(4))[0]
        for ns in range(int(1e6 / dt_us), int(60e6 / dt_us) + 1):
            if size % (240 + 4 * ns):
                continue
            f.seek(3600 + 240 + 4 * ns)
            if struct.unpack("<i", f.read(4))[0] == seq0 + 1:
                best = ns
                break
    if best is None:
        raise ValueError(f"can't work out trace length in {path}")
    ntr = size // (240 + 4 * best)
    raw = np.memmap(path, dtype="<f4", mode="r", offset=3600, shape=(ntr, 60 + best))
    return np.asarray(raw[:, 60:], np.float32), 1e6 / dt_us


def start_time(path):
    """UTC start time from the file name (…20240407T030004… or …20240407030012.243…)."""
    name = Path(path).name
    m = re.search(r"(\d{8})T(\d{6})", name)
    if m:
        return dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(tzinfo=dt.timezone.utc)
    m = re.search(r"(\d{14})\.(\d{3})", name)
    t = dt.datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=dt.timezone.utc)
    return t + dt.timedelta(milliseconds=int(m.group(2)))


# ------------------------------------------------------------------ shrinking

def featurize(data, fs):
    """Cut into 1-s windows; for each: log energy per (cable stretch x frequency band) + a few totals."""
    nch, ns = data.shape
    data = data - np.median(data, axis=0, keepdims=True)          # remove common-mode noise
    groups = np.array_split(np.arange(nch), N_GROUPS)
    w = int(WIN_S * fs)
    out = []
    for k in range(ns // w):
        seg = data[:, k * w:(k + 1) * w]
        f, p = sps.welch(seg, fs=fs, nperseg=min(512, w), axis=1)
        feats = []
        for lo, hi in BANDS:
            m = (f >= lo) & (f < min(hi, fs / 2))
            band = p[:, m].sum(axis=1) if m.any() else np.zeros(nch)
            feats.append([np.log10(band[g].mean() + 1e-12) for g in groups])
        feats = np.array(feats)                                     # bands x groups
        norm = feats - np.median(feats, axis=1, keepdims=True)      # loudness relative to the cable's usual level
        extra = [norm.max(), norm.std(), (norm > 1).sum(), np.log10(np.abs(seg).max() + 1e-12)]
        out.append(np.concatenate([norm.ravel(), extra]).astype(np.float32))
    return np.array(out)


def catalog_times():
    import csv
    times = []
    for c in CATALOG:
        with open(c) as f:
            for row in csv.DictReader(f):
                t = row["time"][:26]
                times.append(dt.datetime.fromisoformat(t).replace(tzinfo=dt.timezone.utc).timestamp())
    return np.array(sorted(times))


def label_windows(t0, n_windows, times):
    """'event' if a catalogued origin is inside the window or up to 1 s before it."""
    starts = t0.timestamp() + np.arange(n_windows) * WIN_S
    labels = []
    for s in starts:
        i = np.searchsorted(times, s - 1.0)
        labels.append("event" if i < len(times) and times[i] < s + WIN_S else "no_event")
    return labels


def shrink_file(path, times=None, triggered=False):
    """Raw file -> features + labels saved as a small .npz. Returns the npz path."""
    data, fs = read_segy(path)
    X = featurize(data, fs)
    t0 = start_time(path)
    if triggered:
        y = ["event"] * len(X)                       # every triggered file holds a catalogued event
    else:
        y = label_windows(t0, len(X), times if times is not None else catalog_times())
    FEAT_DIR.mkdir(parents=True, exist_ok=True)
    out = FEAT_DIR / (Path(path).stem + ".npz")
    np.savez_compressed(out, X=X, y=np.array(y), t0=t0.timestamp(), fs=fs, shape=np.array(data.shape))
    return out


# ------------------------------------------------------------------ for the real-data loop

class ForgeDAS:
    name = "forge-das-events"

    def load(self):
        files = sorted(FEAT_DIR.glob("*.npz"))
        if not files:
            raise RuntimeError("No FORGE features yet. Run: python -m engine.data.stream forge")
        Xs, ys, gs, ids = [], [], [], []
        for f in files:
            d = np.load(f)
            hour = dt.datetime.fromtimestamp(float(d["t0"]), dt.timezone.utc).strftime("%m%d-%H")
            Xs.append(d["X"]); ys += list(d["y"]); gs += [hour] * len(d["y"])
            ids += [f"{f.stem}#{i}" for i in range(len(d["y"]))]
        X = np.vstack([x[:, :Xs[0].shape[1]] for x in Xs if x.shape[1] >= Xs[0].shape[1]])
        return dict(X=X, y=np.array(ys), groups=np.array(gs), ids=np.array(ids),
                    description="FORGE DAS: event vs no-event, labelled from the catalogue; groups = hour of recording")


if __name__ == "__main__":
    from engine import real_loop
    real_loop.run("leak", ForgeDAS.name, ForgeDAS())
