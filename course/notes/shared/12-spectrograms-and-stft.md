# 12 Spectrograms and the short-time Fourier transform (STFT)

## Plain-English idea
One FFT of a whole record tells you which frequencies occur, but not **when**. A **spectrogram** chops the signal into short, overlapping, windowed pieces, takes an FFT of each, and stacks the results. You get a picture with time on the x-axis, frequency on the y-axis, and colour showing energy. Earthquakes look like a sudden broadband smear that fades. Machinery looks like steady horizontal lines. A leak may look like persistent broadband or band-limited hiss.

A spectrogram is effectively an image, so image CNNs can classify it (note 16). [cred-paper]

**The trade-off (uncertainty principle):** a long window gives fine frequency detail but blurry timing. A short window gives sharp timing but coarse frequency.

## Key equations
- Time step between columns: Δt = hop / fs. [scipy-shorttimefft]
- Frequency bin width: Δf = fs / mfft, where mfft is the FFT length (≥ window length). [scipy-shorttimefft]
- Number of frequency rows (one-sided): mfft/2 + 1.
- Overlap = window length − hop. 50–75% overlap is common.
- Use a log (dB) colour scale: 10 log10(|STFT|²).

## Typical numbers
- At fs = 100 Hz with a 256-sample window and hop 64: Δt = 0.64 s, Δf ≈ 0.39 Hz, 129 frequency rows.
- The ObsPy tutorial has a ready-made `Trace.spectrogram()` example. [obspy-tutorial]

## Why V1 cares
- **Leak:** spectrograms per channel, or "frequency-band energy versus distance" maps, are the natural input for detecting persistent leak noise against transient events.
- **Both:** choose window, hop, scaling and normalisation once, save them in config, and reuse them everywhere. Changing them silently between train and test is a classic bug.

## Checkable facts
- With fs = 1,000 Hz and hop = 250 samples, spectrogram columns are 0.25 s apart. [scipy-shorttimefft]
- With fs = 1,000 Hz and mfft = 1,024, the frequency bin width is about 0.977 Hz. [scipy-shorttimefft]
- A 512-point one-sided FFT has 257 frequency bins. [numpy-fft]
- A window of 400 samples with hop 100 has 75% overlap. [scipy-shorttimefft]
- Halving the window length roughly doubles the frequency bin width (coarser frequency) and halves the time smearing. [mit-6-341]
- CRED learns time-frequency features of 3-component seismograms and was trained on 500,000 seismograms (half earthquake, half noise). [cred-paper]

## Sources
scipy-shorttimefft, numpy-fft, obspy-tutorial, think-dsp, mit-6-341, iris-ssbw-course, cred-paper, brunton-fourier-youtube
