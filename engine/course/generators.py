"""Exercise generators. Each one makes labeled examples from physics, for free and without limit.

A generator is  gen(n, rng) -> (X, y, meta)
  X    : numpy array, one example per row (a trace, a waterfall, a property vector...)
  y    : the answers (class names or numbers)
  meta : one dict per example describing the conditions (SNR, speed, porosity...).
         The diagnoser uses meta to explain *where* the learner fails.
"""
from __future__ import annotations

import numpy as np

from . import physics as ph

REGISTRY: dict[str, dict] = {}


def generator(name, kind):
    def wrap(fn):
        REGISTRY[name] = dict(fn=fn, kind=kind)
        return fn
    return wrap


FS = 1000.0
N = 1024

# ====================================================================== shared track


@generator("tone_frequency", kind="trace")
def tone_frequency(n, rng):
    X, y, meta = [], [], []
    for _ in range(n):
        f = rng.uniform(5, 200)
        snr = rng.uniform(5, 30)
        X.append(ph.add_noise_snr(ph.tone(f, N, FS, rng), snr, rng))
        y.append(f)
        meta.append(dict(freq_hz=f, snr_db=snr))
    return np.array(X), np.array(y), meta


@generator("signal_present", kind="trace")
def signal_present(n, rng):
    X, y, meta = [], [], []
    for i in range(n):
        present = i % 2 == 0
        snr = rng.uniform(-18, 6)
        x = rng.standard_normal(N)
        if present:
            x = ph.add_noise_snr(ph.tone(rng.uniform(20, 300), N, FS, rng), snr, rng)
        X.append(x / x.std())            # normalised: loudness gives nothing away
        y.append("signal" if present else "noise")
        meta.append(dict(snr_db=snr if present else np.nan))
    return np.array(X), np.array(y), meta


@generator("signal_shapes", kind="trace")
def signal_shapes(n, rng):
    shapes = ["tone", "chirp", "noise", "impulses"]
    X, y, meta = [], [], []
    t = np.arange(N) / FS
    for i in range(n):
        s = shapes[i % 4]
        snr = rng.uniform(0, 20)
        if s == "tone":
            x = ph.tone(rng.uniform(20, 300), N, FS, rng)
        elif s == "chirp":
            f0, f1 = sorted(rng.uniform(10, 400, 2))
            f1 = max(f1, f0 + 80)
            x = np.sin(2 * np.pi * (f0 * t + (f1 - f0) * t ** 2 / (2 * t[-1])))
        elif s == "noise":
            x = rng.standard_normal(N)
        else:
            x = np.zeros(N)
            for k in rng.integers(0, N, rng.integers(1, 5)):
                x[k] = rng.choice([-1, 1]) * rng.uniform(5, 10)
        x = ph.add_noise_snr(x, snr, rng)
        X.append(x / x.std())
        y.append(s)
        meta.append(dict(snr_db=snr))
    return np.array(X), np.array(y), meta


@generator("tone_under_rumble", kind="trace")
def tone_under_rumble(n, rng):
    """A weak tone hidden under a loud low-frequency rumble (like traffic or wind)."""
    X, y, meta = [], [], []
    for _ in range(n):
        f = rng.uniform(40, 300)
        ratio = rng.uniform(5, 40)             # rumble is this many times louder
        x = ph.tone(f, N, FS, rng) + ratio * ph.lowpass_noise(8, N, FS, rng)
        X.append(ph.add_noise_snr(x, 25, rng))
        y.append(f)
        meta.append(dict(freq_hz=f, rumble_ratio=ratio))
    return np.array(X), np.array(y), meta


# ====================================================================== leak track (DAS)
NCH, DX = 32, 2.0            # 32 channels, 2 m apart
FS_DAS, NT = 500.0, 512      # 500 samples/s, ~1 s window


def _waterfall_background(rng, noise=1.0, wind=0.0):
    w = noise * rng.standard_normal((NCH, NT))
    if wind > 0:  # wind shakes the whole cable at low frequency, slowly varying along it
        base = ph.lowpass_noise(5, NT, FS_DAS, rng)
        gain = 1 + 0.3 * ph.lowpass_noise(0.2 * FS_DAS / NCH, NCH + 64, FS_DAS, rng)[:NCH]
        w += wind * np.outer(gain, base) + 0.3 * wind * rng.standard_normal((NCH, NT))
    return w


def _add_traffic(w, rng, speed=None, amp=None):
    speed = speed if speed is not None else rng.choice([-1, 1]) * rng.uniform(8, 30)
    amp = amp if amp is not None else rng.uniform(2, 5)
    t = np.arange(NT) / FS_DAS
    x0 = rng.uniform(0.2, 0.8) * NCH * DX - speed * t[-1] / 2
    src = ph.lowpass_noise(30, NT, FS_DAS, rng)
    pos = np.arange(NCH)[:, None] * DX
    dist = pos - (x0 + speed * t)[None, :]
    w += amp * src[None, :] / (1 + (dist / 4.0) ** 2)
    return speed


def _add_leak(w, rng, ch=None, amp=None):
    ch = ch if ch is not None else int(rng.integers(2, NCH - 2))
    amp = amp if amp is not None else rng.uniform(0.6, 2.0)
    fc = rng.uniform(70, 180)
    hiss = ph.band_noise(fc - 6, fc + 6, NT, FS_DAS, rng)
    for d, g in ((-2, 0.2), (-1, 0.55), (0, 1.0), (1, 0.55), (2, 0.2)):
        w[ch + d] += amp * g * hiss
    return ch


def _add_digging(w, rng):
    ch = int(rng.integers(1, NCH - 1))
    for k in rng.integers(0, NT - 20, rng.integers(2, 6)):
        burst = rng.standard_normal(20) * np.exp(-np.arange(20) / 4) * rng.uniform(6, 12)
        for d, g in ((-1, 0.5), (0, 1.0), (1, 0.5)):
            w[ch + d, k:k + 20] += g * burst
    return ch


@generator("das_three_events", kind="waterfall")
def das_three_events(n, rng):
    classes = ["quiet", "traffic", "leak"]
    X, y, meta = [], [], []
    for i in range(n):
        c = classes[i % 3]
        w = _waterfall_background(rng)
        amp = rng.uniform(0.6, 2.0)
        if c == "traffic":
            _add_traffic(w, rng)
        elif c == "leak":
            _add_leak(w, rng, amp=amp)
        X.append(w); y.append(c); meta.append(dict(leak_amp=amp if c == "leak" else np.nan))
    return np.array(X), np.array(y), meta


@generator("das_five_events", kind="waterfall")
def das_five_events(n, rng):
    classes = ["quiet", "traffic", "leak", "digging", "wind"]
    X, y, meta = [], [], []
    for i in range(n):
        c = classes[i % 5]
        wind = rng.uniform(1, 3) if c == "wind" else rng.uniform(0, 0.5)
        w = _waterfall_background(rng, wind=wind)
        if c == "traffic":
            _add_traffic(w, rng)
        elif c == "leak":
            _add_leak(w, rng)
        elif c == "digging":
            _add_digging(w, rng)
        X.append(w); y.append(c); meta.append(dict(wind=wind))
    return np.array(X), np.array(y), meta


@generator("das_leak_in_clutter", kind="waterfall")
def das_leak_in_clutter(n, rng):
    """Is there a leak? Weak leaks, hidden among traffic, wind and digging."""
    X, y, meta = [], [], []
    for i in range(n):
        has_leak = i % 2 == 0
        wind = rng.uniform(0, 2)
        w = _waterfall_background(rng, wind=wind)
        n_traffic = int(rng.integers(0, 3))
        for _ in range(n_traffic):
            _add_traffic(w, rng)
        if rng.random() < 0.3:
            _add_digging(w, rng)
        amp = rng.uniform(0.25, 1.2)
        if has_leak:
            _add_leak(w, rng, amp=amp)
        X.append(w); y.append("leak" if has_leak else "no_leak")
        meta.append(dict(leak_amp=amp if has_leak else np.nan, wind=wind, n_traffic=n_traffic))
    return np.array(X), np.array(y), meta


@generator("das_traffic_speed", kind="waterfall")
def das_traffic_speed(n, rng):
    X, y, meta = [], [], []
    for _ in range(n):
        w = _waterfall_background(rng, noise=rng.uniform(0.3, 1.0))
        v = _add_traffic(w, rng)
        X.append(w); y.append(abs(v)); meta.append(dict(speed_ms=abs(v)))
    return np.array(X), np.array(y), meta


@generator("das_leak_location", kind="waterfall")
def das_leak_location(n, rng):
    X, y, meta = [], [], []
    for _ in range(n):
        w = _waterfall_background(rng)
        traffic = rng.random() < 0.5
        if traffic:
            _add_traffic(w, rng)
        amp = rng.uniform(0.5, 2.0)
        ch = _add_leak(w, rng, amp=amp)
        X.append(w); y.append(float(ch)); meta.append(dict(leak_amp=amp, traffic=float(traffic)))
    return np.array(X), np.array(y), meta


# ====================================================================== fluid track

@generator("fluid_from_logs", kind="props")
def fluid_from_logs(n, rng):
    """Vp, Vs, density as a well log would measure them (2% noise). Which fluid is in the pores?"""
    classes = ["brine", "oil", "gas", "dry"]
    X, y, meta = [], [], []
    for i in range(n):
        c = classes[i % 4]
        phi = rng.uniform(0.10, 0.33)
        vp, vs, rho = ph.saturated_rock(phi, c, rng)
        noisy = np.array([vp, vs, rho]) * (1 + 0.02 * rng.standard_normal(3))
        X.append(noisy); y.append(c); meta.append(dict(porosity=phi))
    return np.array(X), np.array(y), meta


@generator("gassmann_vp", kind="props")
def gassmann_vp(n, rng):
    """Given porosity and the pore fluid's stiffness and density, predict the rock's P-velocity."""
    X, y, meta = [], [], []
    for _ in range(n):
        phi = rng.uniform(0.05, 0.35)
        fluid = rng.choice(["brine", "oil", "gas"])
        k_fl, rho_fl = ph.sample_fluid(fluid, rng)
        k_dry, mu_dry = ph.dry_frame(phi)
        k_sat = ph.gassmann(k_dry, ph.QUARTZ["k"], k_fl, phi)
        rho = (1 - phi) * ph.QUARTZ["rho"] + phi * rho_fl
        vp, _ = ph.velocities(k_sat, mu_dry, rho)
        X.append([phi, k_fl, rho_fl]); y.append(vp); meta.append(dict(porosity=phi, k_fluid=k_fl))
    return np.array(X), np.array(y), meta


ANGLES = np.array([0, 5, 10, 15, 20, 25, 30, 35])


@generator("avo_gas_vs_brine", kind="gather")
def avo_gas_vs_brine(n, rng):
    """Reflection strength at 8 angles from a shale sitting on a sand. Is the sand gas or brine?"""
    X, y, meta = [], [], []
    for i in range(n):
        fluid = "gas" if i % 2 == 0 else "brine"
        phi = rng.uniform(0.15, 0.32)
        vp2, vs2, rho2 = ph.saturated_rock(phi, fluid, rng)
        # shale cap: velocities scattered around the sand's brine-case values
        vp1, vs1, rho1 = ph.saturated_rock(phi, "brine", rng)
        vp1 *= rng.uniform(0.85, 1.1); vs1 *= rng.uniform(0.75, 0.95); rho1 *= rng.uniform(0.97, 1.05)
        r, a, b = ph.shuey(vp1, vs1, rho1, vp2, vs2, rho2, ANGLES)
        scale = rng.uniform(0.5, 2.0)          # unknown overall amplitude scaling, as in real data
        X.append(scale * r + 0.004 * rng.standard_normal(len(ANGLES)))
        y.append(fluid); meta.append(dict(porosity=phi, intercept=a))
    return np.array(X), np.array(y), meta


@generator("attenuation_q", kind="trace")
def attenuation_q(n, rng):
    """A pulse after travelling through rock. Low Q (fluid-filled, absorbing) or high Q (tight, dry)?"""
    X, y, meta = [], [], []
    for i in range(n):
        low = i % 2 == 0
        q = rng.uniform(8, 30) if low else rng.uniform(60, 200)
        tt = rng.uniform(0.3, 1.0)
        f0 = rng.uniform(30, 60)
        x = ph.attenuate(ph.ricker(f0, N, FS), FS, tt, q)
        x = ph.add_noise_snr(x, rng.uniform(10, 30), rng)
        X.append(x / np.abs(x).max()); y.append("low_q" if low else "high_q")
        meta.append(dict(q=q, travel_time=tt, source_freq=f0))
    return np.array(X), np.array(y), meta


@generator("s_wave_shadow", kind="profile")
def s_wave_shadow(n, rng):
    """32 surface sensors. Row 0 = P-wave amplitude, row 1 = S-wave amplitude, row 2 = P arrival delay (ms).
    A pocket of liquid blocks S-waves above it and slows P a little; gas slows P a lot and dims it."""
    classes = ["none", "liquid", "gas"]
    X, y, meta = [], [], []
    xs = np.arange(32)
    for i in range(n):
        c = classes[i % 3]
        p = np.ones(32); s = np.ones(32) * rng.uniform(0.6, 1.0); d = np.zeros(32)
        width = rng.uniform(3, 9)
        if c != "none":
            x0 = rng.uniform(5, 27)
            shadow = np.exp(-((xs - x0) / (width / 2)) ** 2)
            s *= 1 - 0.9 * shadow
            if c == "liquid":
                d += rng.uniform(2, 5) * shadow; p *= 1 - 0.1 * shadow
            else:
                d += rng.uniform(8, 15) * shadow; p *= 1 - 0.5 * shadow
        noise = rng.uniform(0.05, 0.2)
        prof = np.stack([p, s, d / 10]) + noise * rng.standard_normal((3, 32))
        X.append(prof); y.append(c); meta.append(dict(noise=noise, width=width))
    return np.array(X), np.array(y), meta
