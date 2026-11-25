# 08 Windowing, tapering and spectral leakage

## Plain-English idea
The FFT quietly assumes your chunk of signal repeats forever. If the chunk does not hold a whole number of cycles, the ends do not join up smoothly. That jump spreads energy into neighbouring frequencies, which is called **spectral leakage**. A strong pump tone can then leak over and hide a weak leak signature next to it.

The fix is to **taper** the chunk so it fades to zero at both ends, by multiplying it by a **window** (Hann, Hamming, Blackman, Tukey/cosine taper). Windows trade **frequency sharpness** (main-lobe width) against **leakage suppression** (side-lobe height). The rectangular window (no taper) has the sharpest peak but the worst leakage.

Seismic practice is to **detrend → taper → filter or FFT** (ObsPy: `trace.detrend()`, `trace.taper()`).

## Key equations
- Hann window: w[n] = 0.5 · (1 − cos(2π n / (N−1)))
- Windowed spectrum = true spectrum convolved with the window's spectrum. Multiplying in time is the same as convolving in frequency.
- Zero-padding (making the FFT longer than the window) adds **interpolated** bins but **not real resolution**. The real resolution is about 1/T_window. [scipy-shorttimefft]

## Typical numbers
- First side lobe: rectangular ≈ −13 dB, Hann ≈ −31 dB, Blackman ≈ −58 dB.
- Main-lobe width (null to null): rectangular 2 bins, Hann 4 bins.

## Why V1 cares
- Every spectrogram (note 12) uses a window. Its type and length change the features your model sees, so fix them once and keep them identical for training and inference.

## Checkable facts
- Zero-padding a 50-sample window to a 200-point FFT oversamples the spectrum by a factor of 4 without improving true resolution. [scipy-shorttimefft]
- A 2 s window gives a native frequency resolution of about 0.5 Hz, whatever FFT length is used. [scipy-shorttimefft]
- The Hann window equals 0 at both endpoints and 1 at its centre. [think-dsp]
- The first side lobe of a rectangular window is about −13 dB, and of a Hann window about −31 dB. [dspguide]
- Multiplication in the time domain is equivalent to convolution in the frequency domain. [mit-6-003]

## Sources
think-dsp, dspguide, scipy-shorttimefft, mit-6-003, seismo-live, obspy-tutorial
