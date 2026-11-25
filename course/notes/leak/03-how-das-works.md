# 03 — How DAS works: light, backscatter and phase

## The idea in plain English
An ordinary telecom optical fibre is glass with microscopic, random density flaws frozen in. A **DAS interrogator** fires a short **laser pulse** (tens to hundreds of nanoseconds) into the fibre. As the pulse travels, every flaw reflects a tiny bit of light back — **Rayleigh backscatter**. Because light travels at a known speed in glass, the arrival *time* of the backscatter tells you *where* along the fibre it came from (this is "optical time-domain reflectometry", OTDR). The phase-sensitive version is called **φ-OTDR**, which is what most DAS is.

When the fibre is still, the backscatter pattern is constant. When a wave stretches or squeezes a bit of fibre, the light path there changes length by nanometres, which shifts the **phase** of the backscattered light. The interrogator measures this phase change between two points a set distance apart and converts it to **strain** (fractional stretch) or **strain rate** (how fast the strain changes). Repeat the pulse hundreds or thousands of times per second and every few metres of fibre becomes a vibration sensor. A 50 km fibre gives tens of thousands of "virtual sensors".

Limits: the next pulse cannot be sent until the previous one's echo has returned from the far end, so **longer fibres allow lower pulse rates** and therefore lower maximum frequencies. Light also fades: ~0.2 dB/km each way at 1550 nm, so range is typically 40–50 km (some systems >100 km; up to ~171 km commercially).

Note that DAS mostly senses strain **along** the fibre axis. Waves arriving broadside to the fibre produce little signal ("limited angular sensitivity").

## Key equations
- Light speed in fibre: c_n = c / n, with n ≈ 1.46 (≈ 2.05×10^8 m/s)
- Position of a backscatter point: z = c_n · t / 2 (two-way travel)
- Max pulse repetition rate: f_r ≤ c_n / (2·L_fibre); max acoustic frequency = f_r / 2
- Phase to strain: ε = λ_p · ΔΦ / (4π · n · ξ · L_g), where λ_p ≈ 1550 nm, ξ ≈ 0.79 (strain-optic factor), L_g = gauge length

## Typical real numbers
- Laser wavelength 1550 nm; attenuation ~0.2 dB/km one way (~0.4 dB/km round trip).
- Pulse width 10–1000 ns → pulse length ~2–200 m in fibre.
- For 100 km fibre, f_r ≤ ~1 kHz; for 50 km, Nyquist ~1 kHz (per Wikipedia's numbers).
- Fast-time digitiser sampling ~0.1 GHz; slow-time output 200–500 Hz in the OOI dataset.

## Checkable facts
- Single-mode fibre has minimum attenuation of about 0.2 dB/km at 1550 nm. [source: xenaki-das-overview-2025]
- The refractive index of fibre is about 1.46, so light moves at roughly c/1.46 in the glass. [source: xenaki-das-overview-2025]
- The pulse repetition rate is limited to f_r = c_n/(2·L_f); for a 100 km fibre this is at most ~1 kHz. [source: xenaki-das-overview-2025]
- In the phase-to-strain formula the strain-optic (Pockels) coefficient ξ is ~0.79 for single-mode fibre. [source: xenaki-das-overview-2025]
- Typical DAS range on single-mode fibre is ~40–50 km, with round-trip loss ~0.4 dB/km. [source: wikipedia-das]
- A 100 ns pulse gives a typical spatial resolution of about 10 m. [source: wikipedia-das]
- Commercial DAS reaches up to ~171 km; subsea repeaters (every 40–100 km) block backscatter. [source: xenaki-das-overview-2025]
- In a short 250 m lab rig, an 80 kHz pulse repetition rate was used, supporting ~1.25 km maximum distance. [source: stajanca-2018-das-leak]

## Sources
xenaki-das-overview-2025, wikipedia-das, pubdas-spica-2023, lindsey-martin-2021-review, stajanca-2018-das-leak, das-rcn-resources
