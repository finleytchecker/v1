# 04 — Gauge length, channel spacing, strain and strain rate

## The idea in plain English
Two numbers decide how "sharp" a DAS image is along the cable:

- **Gauge length (L_g)** — the stretch of fibre over which the phase difference (and hence strain) is measured. It is the **spatial resolution**: two events closer than about one gauge length blur together. It is usually about equal to the pulse length.
- **Channel spacing (Δx)** — how far apart the output channels are. This is **sampling density**, not resolution. Channels often overlap: e.g. a 10 m gauge reported every 2 m.

Trade-off: a long gauge averages more fibre so it has better signal-to-noise, but it smears short-wavelength signals. Worse, a gauge acts like a box-car average, which completely cancels waves whose wavelength equals the gauge length (or L_g/2, L_g/3 …): the response has **notches** at those wavenumbers. For a leak — a point source — the signal will appear spread over at least one gauge length (several channels).

**Strain** ε is dimensionless (m/m); typical DAS signals are nano- to micro-strain. Many interrogators output **strain rate** (dε/dt, units 1/s), which emphasises higher frequencies (it is the time derivative). Strain rate of a plane wave is related to particle velocity u̇ by ε̇ = u̇ / v_apparent, which DASPy and others use for strain-to-velocity conversion.

## Key equations
- Gauge response for a wave of along-fibre wavenumber k: amplitude × sinc(k·L_g/2) → zeros where k·L_g = 2πm, i.e. wavelength λ = L_g/m
- Strain from velocity (plane wave): ε = u / v_app;  ε̇ = u̇ / v_app
- Number of channels = cable length / Δx

## Typical real numbers
| Dataset | Gauge | Spacing | Rate |
|---|---|---|---|
| FOSSA (Sacramento) | 10 m | 2 m | 500 Hz |
| FORESEE (Penn State) | 10 m | 2 m | 500 → 125 Hz |
| Fairbanks | 10 m | 1 m | 1 kHz |
| OOI RCA (ocean) | ~51 m | 2.04 m | 200 Hz |
| DAS4Whale (Svalbard) | — | ~4 m | 645 Hz |
| Stanford-1 | 7.14 m | 8.16 m | 50 Hz |
General range quoted by PubDAS: gauge ~5–40 m, spacing ~0.25–20 m.

## Checkable facts
- Gauge length typically ranges ~5–40 m and channel spacing ~0.25–20 m; channels overlap when gauge > spacing. [source: pubdas-spica-2023]
- Gauge length produces zero-response notches at wavelengths that are integer fractions of the gauge length. [source: pubdas-spica-2023]
- The OOI dataset used 2.042 m channel spacing with 32,600 channels over 66.57 km. [source: xenaki-das-overview-2025]
- FOSSA used a 10 m gauge, 2 m spacing and 500 Hz sampling on a Silixa iDAS. [source: ajo-franklin-2019-dark-fiber]
- The DAS strain-rate response contains the factor sinc(k_z·L_g/2), where k_z is the along-fibre wavenumber. [source: xenaki-das-overview-2025]
- Shorter gauge lengths give better spatial resolution but lower SNR; longer gauges give higher SNR but poorer resolution. [source: xenaki-das-overview-2025]
- Peak car-induced quasi-static strain in a roadside fibre is ~5–10 nanostrain. [source: lindsey-2020-covid-traffic]
- With a 10 m gauge, a wave of 10 m wavelength gives (ideally) zero DAS response. [source: pubdas-spica-2023]

## Sources
pubdas-spica-2023, xenaki-das-overview-2025, ajo-franklin-2019-dark-fiber, lindsey-2020-covid-traffic, daspy, das4whale-zenodo
