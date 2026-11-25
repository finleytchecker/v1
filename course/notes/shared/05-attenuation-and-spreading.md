# 05 Why waves get weaker: geometric spreading and attenuation

## Plain-English idea
A wave's amplitude falls with distance for three reasons: [seg-wiki-attenuation]

1. **Geometric spreading.** The same energy is spread over a growing wavefront. A spherical front's area grows as r², so energy per area falls as 1/r² and amplitude falls as 1/r. Surface waves and waves guided along a line spread over a circle instead, so amplitude falls as 1/sqrt(r).
2. **Intrinsic attenuation (absorption).** Friction in the rock and fluid turns wave energy into heat. The **quality factor Q** measures this: high Q means little loss. Loss per cycle is roughly constant, so **high frequencies die out faster** (they complete more cycles over the same distance).
3. **Scattering and transmission loss.** Energy is redirected at small heterogeneities and interfaces. [seg-wiki-seismic-attenuation]

## Key equations
- Spherical spreading: A(r) ∝ 1/r. Cylindrical (surface/guided): A ∝ 1/sqrt(r).
- Absorption: A(x) = A0 · exp(−α x), with α = π f / (Q v). [seg-wiki-attenuation]
- Equivalently, over travel time t: A = A0 · exp(−π f t / Q).
- Decibels for amplitude: dB = 20 log10(A/A0).

## Typical numbers
- Q in the crust and mantle ranges from about 10 to 1,000. Weathered near-surface rock can be as low as 10–20. [seg-wiki-seismic-attenuation]
- Fluid-saturated, unconsolidated or gas-bearing rock tends to have low Q.

## Why V1 cares
- **Fluid:** extra high-frequency loss beneath a reservoir (low Q) is a classic gas indicator. It also lowers the dominant frequency of deeper reflections.
- **Leak:** a leak's vibration fades with distance along and away from the cable. High-frequency parts fade first, so a far-away leak looks "duller" than a near one. Spreading also explains why the strongest response sits closest to the source.

## Checkable facts
- Doubling distance under spherical spreading halves the amplitude (−6 dB). [seg-wiki-attenuation]
- Doubling distance under cylindrical spreading reduces amplitude by a factor of 1/sqrt(2) ≈ 0.707 (−3 dB). [seg-wiki-attenuation]
- With f = 50 Hz, Q = 50 and travel time t = 1 s: A/A0 = exp(−π·50·1/50) = exp(−π) ≈ 0.043. [seg-wiki-attenuation]
- With Q = 100, v = 2,000 m/s and f = 20 Hz: α = π·20/(100·2000) ≈ 3.14e-4 per metre. [seg-wiki-attenuation]
- An amplitude ratio of 0.1 equals −20 dB. [dspguide]
- At the same Q and travel time, a 100 Hz component loses twice as many nepers as a 50 Hz component. [seg-wiki-seismic-attenuation]

## Sources
seg-wiki-attenuation, seg-wiki-seismic-attenuation, stein-earth324-slides, dspguide, mit-12-510
