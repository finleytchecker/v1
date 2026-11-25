# 09 Convolution and cross-correlation

## Plain-English idea
**Convolution** describes what a linear, time-invariant system does to a signal. Each input sample triggers a copy of the system's impulse response, and the output is the sum of all those copies. A seismic trace is roughly the **earth's reflectivity convolved with the source wavelet**. A recorded leak vibration is the leak's source signal convolved with the response of the pipe, soil and cable.

**Cross-correlation** slides one signal past another and measures how alike they are at each lag. The lag with the biggest peak tells you the **time shift** between them. Uses include:
- finding when a known pattern (template) appears in a long record (template matching / matched filtering)
- measuring arrival-time differences between channels, which gives direction and speed
- **ambient-noise interferometry**: cross-correlating long noise records between two sensors recovers the wave travelling between them.

**Autocorrelation** (a signal against itself) reveals periodicities and the signal's spectrum. Its Fourier transform is the power spectrum.

## Key equations
- Convolution: y[n] = Σ_k x[k] · h[n − k]. In frequency: Y(f) = X(f) · H(f).
- Cross-correlation: c[τ] = Σ_n x[n] · y[n + τ]. In frequency: C(f) = conj(X(f)) · Y(f).
- Normalised cross-correlation lies in [−1, 1]. A value of 1 means identical shape.
- Output length of full linear convolution: N + M − 1.

## Typical numbers
- A correlation peak at lag 25 samples at 100 Hz means a 0.25 s delay.

## Why V1 cares
- **Leak:** cross-correlating neighbouring DAS channels gives the apparent velocity and direction of a vibration. That helps separate a fixed leak (a stationary source) from passing traffic (a moving source).
- **Fluid:** synthetic traces are reflectivity * wavelet. MLReal uses cross- and auto-correlation to make synthetic training data look real. [mlreal-paper]

## Checkable facts
- Convolving a 100-sample signal with a 21-sample filter gives a full output of 120 samples. [dspguide]
- Convolution in time equals multiplication in frequency. [mit-6-003]
- A cross-correlation peak at +40 samples with fs = 200 Hz means a 0.2 s delay. [think-dsp]
- Two channels 10 m apart with a 5 ms delay imply an apparent velocity of 2,000 m/s. [obspy-fk]
- The normalised cross-correlation of a signal with itself at zero lag is 1. [think-dsp]
- MLReal cross-correlates each input with a fixed reference trace as part of its domain adaptation. [mlreal-paper]

## Sources
think-dsp, dspguide, mit-6-003, claerbout-books, obspy-tutorial, mlreal-paper, obspy-fk
