"""Small physics toolkit used to make course exercises.

Everything here is textbook physics (sources are listed in course/notes):
- signals: tones, chirps, band-limited noise, Ricker wavelets
- rock physics: Gassmann fluid substitution, Wood's mixing law, velocities
- AVO: Shuey's two-term approximation
- attenuation: constant-Q amplitude decay exp(-pi f t / Q)
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sps

# ---------------------------------------------------------------- signals

def tone(f, n, fs, rng, amp=1.0):
    t = np.arange(n) / fs
    return amp * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))


def band_noise(lo, hi, n, fs, rng, order=4):
    """White noise squeezed into the band lo..hi Hz (like a leak's hiss)."""
    hi = min(hi, 0.99 * fs / 2)
    sos = sps.butter(order, [lo, hi], btype="band", fs=fs, output="sos")
    x = sps.sosfiltfilt(sos, rng.standard_normal(n + 200))[100:-100]
    return x / (x.std() + 1e-12)


def lowpass_noise(hi, n, fs, rng, order=4):
    sos = sps.butter(order, hi, btype="low", fs=fs, output="sos")
    x = sps.sosfiltfilt(sos, rng.standard_normal(n + 200))[100:-100]
    return x / (x.std() + 1e-12)


def add_noise_snr(x, snr_db, rng):
    p = np.mean(x ** 2)
    noise = rng.standard_normal(x.shape) * np.sqrt(p / 10 ** (snr_db / 10))
    return x + noise


def ricker(f, n, fs, t0=None):
    t = np.arange(n) / fs - (t0 if t0 is not None else n / fs / 2)
    a = (np.pi * f * t) ** 2
    return (1 - 2 * a) * np.exp(-a)


def attenuate(x, fs, travel_time, q):
    """Constant-Q attenuation: each frequency f loses exp(-pi f t / Q)."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / fs)
    return np.fft.irfft(spec * np.exp(-np.pi * f * travel_time / q), n=len(x))


# ---------------------------------------------------------------- rock physics
# Moduli in GPa, densities in g/cc -> velocities in km/s.
QUARTZ = dict(k=37.0, mu=44.0, rho=2.65)
FLUIDS = {
    #          bulk modulus (GPa)   density (g/cc)
    "brine": dict(k=(2.4, 3.0), rho=(1.01, 1.10)),
    "oil":   dict(k=(0.7, 1.5), rho=(0.70, 0.88)),
    "gas":   dict(k=(0.02, 0.12), rho=(0.08, 0.25)),
    "dry":   dict(k=(0.0001, 0.0002), rho=(0.0012, 0.0013)),  # air-filled pores
}


def wood(k_a, k_b, s_a):
    """Wood/Reuss mix of two fluids; s_a = fraction of fluid a."""
    return 1.0 / (s_a / k_a + (1 - s_a) / k_b)


def dry_frame(phi, phi_c=0.40, k_min=QUARTZ["k"], mu_min=QUARTZ["mu"]):
    """Critical-porosity model (Nur): rock gets softer linearly until phi_c."""
    f = np.clip(1 - phi / phi_c, 0.02, 1)
    return k_min * f, mu_min * f


def gassmann(k_dry, k_min, k_fl, phi):
    """Saturated bulk modulus. Shear modulus is NOT changed by the fluid."""
    num = (1 - k_dry / k_min) ** 2
    den = phi / k_fl + (1 - phi) / k_min - k_dry / k_min ** 2
    return k_dry + num / den


def velocities(k, mu, rho):
    vp = np.sqrt((k + 4.0 / 3.0 * mu) / rho)
    vs = np.sqrt(mu / rho)
    return vp, vs


def sample_fluid(name, rng):
    p = FLUIDS[name]
    return rng.uniform(*p["k"]), rng.uniform(*p["rho"])


def saturated_rock(phi, fluid, rng, sw=None):
    """Vp, Vs, rho for a sandstone filled with `fluid` (rest of pore space brine)."""
    k_dry, mu_dry = dry_frame(phi)
    k_hc, rho_hc = sample_fluid(fluid, rng)
    if fluid in ("brine", "dry"):
        k_fl, rho_fl = k_hc, rho_hc
    else:
        sw = rng.uniform(0.1, 0.4) if sw is None else sw
        k_b, rho_b = sample_fluid("brine", rng)
        k_fl = wood(k_b, k_hc, sw)
        rho_fl = sw * rho_b + (1 - sw) * rho_hc
    k_sat = gassmann(k_dry, QUARTZ["k"], k_fl, phi)
    rho = (1 - phi) * QUARTZ["rho"] + phi * rho_fl
    vp, vs = velocities(k_sat, mu_dry, rho)
    return vp, vs, rho


def shuey(vp1, vs1, rho1, vp2, vs2, rho2, angles_deg):
    """Two-term Shuey AVO: R(theta) = A + B sin^2(theta)."""
    vp, vs, rho = (vp1 + vp2) / 2, (vs1 + vs2) / 2, (rho1 + rho2) / 2
    dvp, dvs, drho = vp2 - vp1, vs2 - vs1, rho2 - rho1
    a = 0.5 * (dvp / vp + drho / rho)
    b = 0.5 * dvp / vp - 2 * (vs / vp) ** 2 * (drho / rho + 2 * dvs / vs)
    th = np.radians(angles_deg)
    return a + b * np.sin(th) ** 2, a, b
