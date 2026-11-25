# 02 Seismic wave types: P, S and surface waves

## Plain-English idea
Solid rock can carry two kinds of wave through its interior (body waves):

- **P waves (primary, compressional)** push and pull the material along the direction of travel, like a Slinky being pushed. They are the fastest wave and travel through solids, liquids and gases. [iris-seismic-wave-motions]
- **S waves (secondary, shear)** shake the material sideways, across the direction of travel. A fluid has no resistance to shearing, so S waves **cannot travel through liquids or gases**. [iris-seismic-wave-motions]

Near a free surface, the two combine into slower **surface waves**:

- **Rayleigh waves** roll the ground in an ellipse (vertical plus horizontal motion).
- **Love waves** shake the ground side to side, horizontally only.

Surface waves often carry most of the energy in a record. Along a buried cable they can be a strong source of "noise" that has to be filtered out.

## Key equations
For an isotropic elastic rock with bulk modulus K, shear modulus μ and density ρ:

- Vp = sqrt((K + 4μ/3) / ρ)
- Vs = sqrt(μ / ρ)
- In a fluid, μ = 0, so Vs = 0 and Vp = sqrt(K/ρ).
- The Vp/Vs ratio is often about 1.7 (sqrt(3) ≈ 1.73 for a "Poisson solid").

## Typical numbers
- Crustal rock: Vp ≈ 6 km/s, Vs ≈ 4 km/s. [iris-seismic-wave-motions]
- Water: Vp ≈ 1.5 km/s, Vs = 0.

## Why V1 cares
- **Fluid:** pore fluid changes K (and so Vp) but barely changes μ (and so Vs). Gas makes the rock much easier to compress, so Vp drops sharply while Vs stays almost the same, and Vp/Vs falls. This is the physical root of fluid detection. Rock-physics details are covered elsewhere.
- **Leak:** a DAS cable mostly senses strain along its own axis, so different wave types and arrival angles show up with different strengths.

## Checkable facts
- S waves cannot propagate through liquids such as water or the outer core. [iris-seismic-wave-motions]
- P waves are the fastest seismic waves and arrive first. [iris-seismic-wave-motions]
- With Vp = 6 km/s and Vs = 4 km/s, Vp/Vs = 1.5. [iris-seismic-wave-motions]
- In a Poisson solid (λ = μ), Vp/Vs = sqrt(3) ≈ 1.73. [mit-12-510]
- Water with K = 2.25 GPa and ρ = 1,000 kg/m³ has Vp = sqrt(2.25e9/1000) = 1,500 m/s. [mit-12-510]
- Love waves produce only horizontal motion. Rayleigh waves produce both vertical and horizontal motion. [iris-seismic-wave-motions]
- 10 km at 6 km/s takes about 1.67 s, and at 4 km/s it takes 2.5 s, so the S-minus-P time is about 0.83 s. [stein-earth324-slides]

## Sources
iris-seismic-wave-motions, mit-12-510, stein-earth324-slides, iris-ssbw-course
