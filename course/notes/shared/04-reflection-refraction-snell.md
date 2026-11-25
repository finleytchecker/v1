# 04 Reflection, refraction and Snell's law

## Plain-English idea
When a wave hits a boundary between two materials, some of its energy **bounces back** (reflection) and some **passes through but bends** (refraction). How much bounces back depends on the contrast in **acoustic impedance** (density × velocity) across the boundary. How much the wave bends depends on the velocity ratio, and Snell's law describes it.

If the wave passes from slow rock into fast rock, it bends away from the vertical. At a certain **critical angle**, the transmitted wave skims along the boundary as a head wave. Beyond that angle, all the energy is reflected.

## Key equations
- Snell's law: sin θ1 / v1 = sin θ2 / v2 = p, where p is the ray parameter (horizontal slowness). [seg-wiki-reflection-refraction]
- Critical angle (v2 > v1): θc = arcsin(v1 / v2)
- Acoustic impedance: Z = ρ v
- Normal-incidence reflection coefficient: R = (Z2 − Z1) / (Z2 + Z1). Transmission coefficient: T = 1 − R (for pressure amplitude, T = 2Z2/(Z1+Z2)).
- The share of energy reflected at normal incidence is R².
- Angle-dependent reflection (AVO) is covered in the Fluid-specific notes. bruges implements the Zoeppritz and Aki-Richards formulas. [bruges]

## Typical numbers
- Shale over gas sand often has a negative R (impedance drops), which produces a "bright spot".
- Typical sedimentary reflection coefficients are small, roughly |R| < 0.2.

## Why V1 cares
- **Fluid:** the sign and size of R, and how R changes with angle, are the core observables for telling fluids apart.
- **Leak:** the ground around a cable has layers too. Reflections and guided waves make the recorded signal messier than a single direct wave.

## Checkable facts
- v1 = 2,000 m/s, v2 = 4,000 m/s: critical angle = arcsin(0.5) = 30°. [seg-wiki-reflection-refraction]
- A ray at 30° in a 2,000 m/s layer entering a 3,000 m/s layer refracts to arcsin(0.75) ≈ 48.6°. [seg-wiki-reflection-refraction]
- Z1 = 4.0e6 and Z2 = 6.0e6 kg/(m²·s) give R = 2/10 = 0.2. [mit-12-510]
- If Z2 < Z1, R is negative (the reflected wave's polarity flips). [mit-12-510]
- With R = 0.2, 4% of the energy is reflected at normal incidence. [mit-12-510]
- Ray parameter for θ = 30°, v = 2,000 m/s: p = 0.5/2000 = 0.00025 s/m (0.25 s/km). [mit-12-510]

## Sources
seg-wiki-reflection-refraction, mit-12-510, mit-12-510-syllabus, bruges, claerbout-books
