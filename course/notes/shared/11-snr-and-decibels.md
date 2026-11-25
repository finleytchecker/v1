# 11 Signal-to-noise ratio and decibels

## Plain-English idea
**SNR** compares how strong the thing you want is with how strong everything else is. Seismic and DAS data are noisy (traffic, wind, pumps, ocean microseisms, instrument noise). Most detection problems really mean "find the weak signal at low SNR".

SNR is usually given in **decibels (dB)**, a log scale where every factor of 10 in power adds 10 dB. Because power ∝ amplitude², an amplitude factor of 10 is 20 dB.

Ways to raise SNR:
- **filter** to the band where the signal lives (note 10)
- **stack** (average) repeated or neighbouring records. Random noise partly cancels and the signal adds.
- **matched filtering / cross-correlation** with a known template (note 9).

## Key equations
- SNR (power) = P_signal / P_noise. In dB: 10 log10(P_s / P_n) = 20 log10(A_s / A_n) for RMS amplitudes.
- RMS amplitude: sqrt(mean(x²)).
- Stacking N records with independent random noise improves amplitude SNR by sqrt(N).
- A common window-based seismic SNR: RMS (or max) in a window after the pick divided by RMS in a window before it.

## Typical numbers
- Benchmark sets such as STEAD store an SNR value per earthquake trace. Many ML studies split results into low- and high-SNR bins. EQTransformer reports especially good performance in high-noise conditions. [eqtransformer-paper] [stead-dataset]

## Why V1 cares
- **Leak:** leaks are often small, so test the model per SNR bin, not just overall. Track how recall drops as SNR falls.
- **Both:** making synthetic examples harder by adding real noise at controlled SNR is a cheap, effective augmentation (note 16).

## Checkable facts
- A power ratio of 100 is 20 dB. [dspguide]
- An amplitude ratio of 10 is 20 dB. An amplitude ratio of 2 is about 6.02 dB. [dspguide]
- 0 dB SNR means signal and noise have equal power. [think-dsp]
- Stacking 16 traces with independent noise improves amplitude SNR by a factor of 4 (about 12 dB). [claerbout-books]
- Stacking 100 traces improves amplitude SNR by 10 (20 dB). [claerbout-books]
- The RMS of a sine wave with peak amplitude 1 is 1/sqrt(2) ≈ 0.707. [think-dsp]

## Sources
dspguide, think-dsp, claerbout-books, eqtransformer-paper, stead-dataset, iris-ssbw-course
