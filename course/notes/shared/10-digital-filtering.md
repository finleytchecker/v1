# 10 Digital filtering

## Plain-English idea
A filter keeps some frequencies and suppresses others:
- **low-pass** keeps slow wiggles and removes fast ones
- **high-pass** removes slow drift
- **band-pass** keeps a band
- **band-stop / notch** removes a band, such as 50 or 60 Hz mains hum.

Two families:
- **FIR** (finite impulse response): a weighted moving average. It is always stable and can have exactly linear phase.
- **IIR** (infinite impulse response, e.g. Butterworth): it feeds back on its own output. It gets sharp cut-offs cheaply but shifts phase in a frequency-dependent way.

**Phase matters for timing.** A causal (one-pass) filter delays and distorts arrivals. A **zero-phase** filter runs forward and then backward, which cancels the phase shift and doubles the effective order. ObsPy's example: a 2-corner low-pass with `zerophase=True` acts as 4 corners. [obspy-filtering] Zero-phase filters are non-causal (they use "future" samples), so they cannot run in strict real time.

The **order** (number of corners/poles) controls steepness. A Butterworth filter rolls off at about 6 dB per octave for each pole.

## Key equations
- FIR: y[n] = Σ_{k=0}^{M} b_k x[n−k]
- IIR: y[n] = Σ b_k x[n−k] − Σ_{k≥1} a_k y[n−k]
- Butterworth magnitude: |H(f)|² = 1 / (1 + (f/fc)^(2n)). At f = fc the gain is 1/sqrt(2) (−3 dB).
- Prefer second-order sections (`scipy.signal.sosfiltfilt`) over (b, a) coefficients for high orders, for numerical stability.

## Typical numbers
- EQTransformer pre-processing: band-pass 1–45 Hz on 100 Hz data. [eqtransformer-paper]
- ObsPy FK example: band-pass 1–8 Hz. [obspy-fk]

## Why V1 cares
- **Leak:** band-pass to the leak band and notch out known machinery tones before computing features. Use the identical filter in training and deployment.
- **Fluid:** filtering changes wavelet shape and so changes amplitude attributes. Do not filter one class differently from another, or the model will learn the filter rather than the fluid (a hidden leakage path, note 15).

## Checkable facts
- A Butterworth filter's gain at its corner frequency is −3 dB (amplitude ≈ 0.707). [mit-6-341]
- A 4-pole Butterworth low-pass falls about 24 dB per octave above its corner. [dspguide]
- Running a 2-corner filter forward and backward (zero-phase) gives an effective 4 corners. [obspy-filtering]
- The ObsPy filtering tutorial applies a 1.0 Hz low-pass. [obspy-filtering]
- EQTransformer band-passes its 100 Hz input between 1 and 45 Hz. [eqtransformer-paper]
- A band-pass upper corner must stay below Nyquist: for 100 Hz data, below 50 Hz. [think-dsp]

## Sources
obspy-filtering, obspy-tutorial, dspguide, think-dsp, mit-6-341, coursera-epfl-dsp-specialization, eqtransformer-paper, obspy-fk
