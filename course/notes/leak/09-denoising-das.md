# 09 — Cleaning DAS data (denoising)

## The idea in plain English
Raw DAS is noisy. A practical cleaning recipe goes from simple to clever:

1. **Detrend / demean** each channel (remove slow drift).
2. **Common-mode removal** — subtract the median across channels at each time sample; kills noise that hits every channel at once (laser phase noise, interrogator glitches).
3. **Band-pass filter** — keep only the band you care about (e.g. leak band). Butterworth filters are standard.
4. **Decimate** — downsample after low-passing.
5. **f-k / slope filter** — remove traffic or keep a velocity range (note 08).
6. **Spectral noise floor** — per channel, subtract the median (or a long-term average) spectrum so only *changes* show; Stajanca et al. did exactly this to reveal leaks.
7. **Adaptive f-k (AFK) filter** (lightguide) — boosts coherent energy, suppresses incoherent noise.
8. **Deep learning, self-supervised** — jDAS predicts each channel from its neighbours: coherent signals are predictable, random noise is not, so the prediction is a denoised channel. DAS-N2N trains on two fibres in the same cable (two noisy copies). Neither needs "clean" labels.

**Warning for leaks:** coherence-based denoisers assume the signal is coherent across neighbouring channels. A leak spans only a few channels (about one gauge length plus pipe spreading). Check that your denoiser does not erase it — test on synthetic leaks injected into real noise.

## Key equations
- Common-mode removal: x'(c, t) = x(c, t) − median_c x(c, t)
- Noise-floor subtraction (dB): S'(c, f) = S(c, f) − median_t S(c, f)
- Averaging gain for a steady signal in random noise over K windows: SNR improves ≈ 10·log10(K) dB in power-spectrum estimates (variance shrinks by K).

## Typical real numbers
- das4whales: Butterworth band-pass order 5 (10–30 Hz) and high-pass order 2 at 5 Hz.
- DAS-N2N: 47,065 parameters; denoises 30 s × 985 channels in < 1 s.
- Traffic waterfall paper: Butterworth low-pass order 1 at normalized cutoff 0.5, plus wavelet thresholding.

## Checkable facts
- jDAS relies on the idea that spatio-temporally coherent signals can be interpolated from neighbouring channels while incoherent noise cannot. [source: jdas]
- jDAS requires TensorFlow 2.2.0 or later. [source: jdas]
- DAS-N2N trains on two fibres in the same cable and needs only one fibre after training; the model has 47,065 parameters. [source: das-n2n]
- lightguide's AFK filter is applied with an exponent parameter (e.g. 0.8) to suppress incoherent noise. [source: lightguide]
- The das4whales tutorial designs a 5th-order Butterworth band-pass of 10–30 Hz and a 2nd-order 5 Hz high-pass. [source: das4whales-tutorial]
- Stajanca et al. subtracted the median of each spectrum as a noise floor before integrating leak-band power. [source: stajanca-2018-das-leak]
- DASPy includes DAS-specific denoising and strain-velocity conversion and is MIT licensed. [source: daspy]

## Sources
jdas, das-n2n, lightguide, daspy, dascore, das4whales-tutorial, stajanca-2018-das-leak, wang-2024-traffic-das
