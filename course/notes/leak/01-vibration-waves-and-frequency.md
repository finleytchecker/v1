# 01 — Vibration, waves and frequency

## The idea in plain English
Everything the Leak module looks at is **vibration**: tiny back-and-forth motion of the ground, a pipe wall, or the water inside a pipe. When a vibration travels from place to place it is a **wave**. Three numbers describe a simple wave:

- **Frequency f** — how many wiggles per second, in hertz (Hz). A car rumbling past a fibre gives a few to a few tens of Hz; a pressurised gas leak hiss is hundreds to thousands of Hz.
- **Wavelength λ** — the distance between two crests, in metres.
- **Speed v** — how fast the crest moves, in m/s. Different waves travel at very different speeds: sound in open water ~1500 m/s, leak noise inside a plastic water pipe ~350–420 m/s, a car on a road 5–30 m/s (the "wave" here is the car itself squashing the road as it drives).

Real signals are never one pure tone. We describe them by their **spectrum**: how much energy sits at each frequency. A leak is a *broadband hiss* in principle, but the pipe and soil filter it so that what you actually measure is energy concentrated in a fairly narrow band — this is why the project brief calls a leak a "steady narrow-band hiss".

**Loudness** is usually given in **decibels (dB)**: a ratio on a log scale. +10 dB = 10× more power; +3 dB ≈ 2× power; +20 dB = 10× larger amplitude.

## Key equations
- v = f · λ  (speed = frequency × wavelength)
- Period T = 1/f
- Power ratio in dB: L = 10·log10(P1/P0); amplitude ratio: L = 20·log10(A1/A0)
- Attenuation in dB/m adds up linearly with distance: total loss = (dB/m) × distance.

## Typical real numbers
| Thing | Value |
|---|---|
| Sound speed in water | ~1500 m/s |
| Leak-noise speed in buried plastic (MDPE/PVC) water pipe | ~350–420 m/s |
| Car speeds seen by roadside fibre | 5–30 m/s |
| Traffic surface-wave energy | ~3–30 Hz |
| Fin-whale call (narrow-band tone in DAS) | 15–20 Hz |
| Gas-pipe leak vibration seen by DAS | ~500 Hz–5 kHz |

## Checkable facts
- Sound travels at about 1500 m/s in sea water; fin-whale calls recorded by DAS move along the cable at that apparent speed. [source: xenaki-das-overview-2025]
- Leak noise in a buried plastic water pipe test rig travelled at ~356 m/s; seasonal field values ranged ~350–420 m/s. [source: almeida-2014-plastic-pipe-filtering]
- In a 170 mm MDPE water pipe the leak-carrying wave travels at roughly 400 m/s, much slower than in a metal pipe. [source: brennan-soton-plastic-leak-article]
- Vehicles in urban DAS studies drive at 5–30 m/s. [source: liu-2024-vehicle-das]
- A 20 Hz wave travelling at 400 m/s has a wavelength of 20 m (λ = v/f). [source: think-dsp]
- 3 dB corresponds to roughly a doubling of power. [source: think-dsp]

## Sources
think-dsp, xenaki-das-overview-2025, almeida-2014-plastic-pipe-filtering, brennan-soton-plastic-leak-article, liu-2024-vehicle-das, lindsey-2020-covid-traffic
