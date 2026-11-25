# 07 The Fourier transform and the FFT

## Plain-English idea
Any signal can be built by adding sine waves of different frequencies, amplitudes and phases. The **Fourier transform** tells you the recipe: how much of each frequency is present (the **amplitude spectrum**) and how each is shifted (the **phase spectrum**). The **DFT** is the version for sampled, finite signals. The **FFT** is a fast algorithm for computing the DFT. It takes about N log N operations instead of N².

A leak hiss, a pump hum and an earthquake all look like messy wiggles in time, but they often have very different spectra. That makes the spectrum one of the most useful feature sources.

## Key equations
- DFT: X[k] = Σ_{n=0}^{N−1} x[n] · exp(−2πi k n / N)
- Frequency of bin k: f_k = k · fs / N (for k up to N/2).
- For real input, the spectrum is Hermitian, X[−k] = conj(X[k]), so `np.fft.rfft` returns only N/2 + 1 bins. [numpy-fft]
- `np.fft.fft` output order: bin 0 = zero frequency (DC), then positive frequencies, then negative frequencies. For even N, bin N/2 is Nyquist. Use `fftfreq`/`rfftfreq` to get the frequency axis. [numpy-fft]
- NumPy's default normalisation ("backward"): forward is unscaled, inverse is scaled by 1/N. "ortho" scales both by 1/sqrt(N). [numpy-fft]
- Power spectrum ∝ |X[k]|². Parseval: total energy is the same in time and frequency (with the right scaling).

## Typical numbers
- For N = 1,024, an FFT needs on the order of N log2 N ≈ 10,240 operations, versus about 1,048,576 for a direct DFT.

## Why V1 cares
- Band energies, spectral centroid, peak frequency and spectral slope are classic hand-made features for both modules (note 14).
- Spectra also show attenuation (note 5): high-Q and low-Q paths have different high-frequency fall-off.

## Checkable facts
- `np.fft.rfft` of 8 real samples returns 5 complex values (N/2 + 1). [numpy-fft]
- `np.fft.fftfreq(8)` returns [0, 0.125, 0.25, 0.375, −0.5, −0.375, −0.25, −0.125] (cycles per sample). [numpy-fft]
- With fs = 100 Hz and N = 1,000, bin k = 50 corresponds to 5 Hz. [numpy-fft]
- Bin 0 of the FFT equals the sum of the samples (the DC term). [numpy-fft]
- In NumPy's default normalisation, ifft(fft(x)) returns x, because the inverse divides by N. [numpy-fft]
- N log2 N for N = 4,096 is 49,152. [mit-6-341]

## Sources
numpy-fft, think-dsp, dspguide, mit-6-003, mit-6-341, coursera-epfl-dsp1, brunton-fourier-youtube, seismo-live
