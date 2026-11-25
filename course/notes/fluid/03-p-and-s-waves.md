# 03 - P-waves and S-waves

## Plain English
- A **P-wave** (primary, compressional) pushes and pulls the material along the travel direction, like a slinky being shoved. It feels both the bulk modulus and the shear modulus.
- An **S-wave** (secondary, shear) wiggles the material sideways. It needs the material to resist shearing, so **an S-wave cannot travel through a liquid or gas**. In a rock, the S-wave travels through the grain skeleton, and the pore fluid only affects it by adding weight.

P-waves are always faster than S-waves in the same material.

## The two key equations
    Vp = sqrt( (K + 4/3 * mu) / rho )
    Vs = sqrt( mu / rho )

The reverse direction is how you get moduli from well logs:

    mu = rho * Vs^2
    K  = rho * (Vp^2 - 4/3 * Vs^2)

Units: if rho is in g/cc and V in km/s, the moduli come out in GPa.

## What happens when fluid changes
- Brine to gas: K drops a lot and rho drops a little, so **Vp drops**. mu is unchanged and rho drops, so **Vs rises slightly**.
- This opposite movement of Vp and Vs is the fingerprint of gas. It is why Vp/Vs (note 05) is such a strong fluid indicator.

## Typical velocities (m/s)
| Material | Vp | Vs |
|---|---|---|
| Water | 1450-1500 | 0 |
| Oil | 1200-1250 | 0 |
| Dry sand (unconsolidated) | 400-1200 | 100-500 |
| Wet sand (unconsolidated) | 1500-2000 | 400-600 |
| Porous saturated sandstone | 2000-3500 | 800-1800 |
| Saturated shale/clay | 1100-2500 | 200-800 |
| Limestone | 3500-6000 | 2000-3300 |
| Salt | 4500-5500 | 2500-3100 |
| Quartz crystal (computed from K=37, mu=44, rho=2.65) | ~6000 | ~4080 |

## Checkable facts
- Vs in any pure fluid is 0 because mu = 0. [source: wikipedia-gassmann]
- Vp = sqrt((K + 4/3 mu)/rho) and Vs = sqrt(mu/rho). [source: wikipedia-gassmann]
- Water has Vp of 1450-1500 m/s and oil has Vp of 1200-1250 m/s. [source: mavko-seismic-velocity-slides]
- Limestones have Vp of 3500-6000 m/s and Vs of 2000-3300 m/s. [source: mavko-seismic-velocity-slides]
- Wet unconsolidated sands have Vp of 1500-2000 m/s, while dry sands have Vp of 400-1200 m/s. [source: mavko-seismic-velocity-slides]
- Quartz with K = 37 GPa, mu = 44 GPa and rho = 2.65 g/cc has Vp of about 6.0 km/s and Vs of about 4.1 km/s. [source: seg-tut-petrophysics-2]
- A fluid's sound speed is sqrt(K/rho). For brine (2.8 GPa, 1.09 g/cc) that is about 1600 m/s. For gas (0.06 GPa, 0.25 g/cc) it is about 490 m/s. [source: seg-tut-petrophysics-2]
- Going from dry to water-saturated, the rock bulk modulus almost always increases, but Vp can go up or down because density also increases. [source: mavko-seismic-velocity-slides]

## Sources
mit-12-510-seismology, mavko-seismic-velocity-slides, wikipedia-gassmann, seg-tut-petrophysics-2
