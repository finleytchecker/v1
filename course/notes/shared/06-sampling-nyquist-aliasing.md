# 06 Sampling, Nyquist and aliasing

## Plain-English idea
A computer cannot store a continuous wiggle. It measures the signal at regular instants, which is called **sampling**. The number of samples per second is the **sampling rate fs**, and the gap between samples is Δt = 1/fs.

The **Nyquist theorem**: a sampled signal can only represent frequencies up to **fs/2**, the **Nyquist frequency**. Anything faster is not lost. It is **disguised as a lower frequency**, which is called **aliasing**. It is like a filmed wagon wheel that seems to spin backwards. Once a signal has aliased, it cannot be untangled. So real recorders apply an analogue **anti-alias low-pass filter** before sampling, and software applies a digital one before **downsampling** (decimation).

## Key equations
- Δt = 1 / fs. Nyquist frequency f_N = fs / 2.
- A tone at f > f_N appears at the alias frequency |f − n·fs| (choose the integer n that brings it into 0…f_N).
- Record length T with N samples: T = N Δt. Frequency resolution of a plain FFT: Δf = 1/T = fs/N.
- Spatial sampling works the same way: channel spacing Δx gives a Nyquist wavenumber k_N = 1/(2Δx) cycles per metre. This matters for DAS channels and for f-k analysis (note 13).

## Typical numbers
- STEAD and INSTANCE traces: 100 Hz sampling, so Nyquist is 50 Hz. [stead-dataset] [instance-dataset]
- EQTransformer input: 60 s at 100 Hz = 6,000 samples. [eqtransformer-paper]

## Why V1 cares
- **Leak:** leak noise can contain high frequencies. If the interrogator's sampling rate is too low, or you decimate without filtering, the leak energy aliases into the wrong band and your features lie to you.
- **Both:** when mixing datasets with different sampling rates, resample them properly (with anti-alias filtering) before training.

## Checkable facts
- A signal sampled at 1,000 Hz can only represent frequencies up to 500 Hz. [think-dsp]
- Sampled at 100 Hz, a 70 Hz tone aliases to 30 Hz. [think-dsp]
- Sampled at 100 Hz, a 130 Hz tone aliases to 30 Hz. [dspguide]
- A 60 s window at 100 Hz contains 6,000 samples. [eqtransformer-paper]
- 2,048 samples at 1,000 Hz span 2.048 s, giving FFT bin spacing of about 0.488 Hz. [numpy-fft]
- Decimating 1,000 Hz data by a factor of 4 gives 250 Hz, so you must first low-pass below 125 Hz. [mit-6-341]
- Channel spacing of 2 m gives a spatial Nyquist of 0.25 cycles/m (shortest unaliased wavelength 4 m). [obspy-fk]

## Sources
think-dsp, dspguide, mit-6-003, mit-6-341, numpy-fft, seismo-live, stead-dataset, instance-dataset, eqtransformer-paper, obspy-fk
