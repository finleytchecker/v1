# 02 — Sampling, the FFT and spectrograms

## The idea in plain English
A computer cannot store a continuous wiggle; it stores **samples** taken at a fixed rate, the **sampling rate fs** (samples per second, Hz). The fastest wiggle you can represent is half the sampling rate — the **Nyquist frequency**. Anything faster "folds back" and pretends to be a lower frequency (**aliasing**). So a DAS system sampling at 500 Hz can only see vibrations up to 250 Hz.

The **Fourier transform (FFT)** turns a chunk of samples into a spectrum (energy vs frequency). If you take an FFT of a short window, slide the window along, and stack the results, you get a **spectrogram**: time on one axis, frequency on the other, colour = energy. A leak shows up in a channel's spectrogram as a **horizontal stripe**: the same frequency band, on all the time. A passing car is a short vertical smear; an earthquake is a brief broadband flash.

There is a trade-off: a longer window gives finer frequency resolution (Δf = fs/N) but blurs timing. Averaging many windows (Welch's method) makes a steady signal like a leak stand out from random noise.

## Key equations
- Nyquist frequency: f_N = fs / 2
- Frequency resolution of an N-point FFT: Δf = fs / N
- Window duration: T = N / fs
- Averaging K independent noise windows reduces noise variance by ~K; for cross-correlation of uncorrelated noise, SNR improves ~3 dB per doubling of record length.

## Typical real numbers
- DAS slow-time (per-channel) sampling: 50 Hz (Stanford-1 archive), 125–500 Hz (FORESEE, FOSSA), 1–10 kHz (Fairbanks, borehole FORGE), 80 kHz pulse rate in a short lab rig.
- scipy.signal.spectrogram default segment length is 256 samples with nperseg//8 overlap.
- Stajanca et al. used 8192-point FFT windows and averaged 30 s of data.

## Checkable facts
- A DAS channel sampled at 500 Hz can represent vibrations only up to 250 Hz (Nyquist). [source: think-dsp]
- The maximum observable acoustic frequency in DAS is half the pulse repetition rate, f_r/2. [source: xenaki-das-overview-2025]
- scipy.signal.spectrogram uses nperseg = 256 by default when the window is given by name, and noverlap = nperseg // 8. [source: scipy-spectrogram]
- With fs = 1000 Hz and N = 8192, the FFT frequency spacing is ~0.12 Hz. [source: think-dsp]
- For uncorrelated background noise, doubling the acquisition time raises the cross-correlation SNR by about 3 dB. [source: brennan-soton-plastic-leak-article]
- Stajanca et al. computed short-time FFTs with 8192-point windows, averaged over 30 s, and subtracted the median spectrum as a noise floor. [source: stajanca-2018-das-leak]

## Sources
think-dsp, scipy-spectrogram, xenaki-das-overview-2025, stajanca-2018-das-leak, brennan-soton-plastic-leak-article, pubdas-spica-2023
