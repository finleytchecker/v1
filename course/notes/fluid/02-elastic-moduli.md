# 02 - Elastic moduli: bulk, shear and the numbers that matter

## Plain English
An **elastic modulus** measures how hard it is to deform something.
- **Bulk modulus K** is resistance to being squeezed uniformly from all sides, i.e. changing volume. A big K means hard to compress. Its inverse, 1/K, is the **compressibility**.
- **Shear modulus mu** is resistance to being twisted or sheared, i.e. changing shape without changing volume.

Fluids flow when you shear them, so **mu = 0 for every fluid**: water, oil and gas alike. Fluids do have a bulk modulus, and it differs hugely between water and gas. That difference is the main reason seismic can detect gas.

Moduli are measured in pascals. In rock physics we use **GPa** (10^9 Pa).

## Mixing rules (how to combine materials)
- **Voigt** (upper bound, an arithmetic average): `M_V = sum(f_i * M_i)`
- **Reuss** (lower bound, a harmonic average): `1/M_R = sum(f_i / M_i)`
- **Voigt-Reuss-Hill**: the average of the two. It is used for the modulus of a mineral mixture.
- **Wood's / Reuss rule for fluids**: a mix of fluids in the pores behaves like the Reuss average, `1/K_fl = Sw/K_brine + (1-Sw)/K_gas`. This is valid when the fluids are finely mixed (see note 13).

## Typical values (GPa)
| Material | K | mu |
|---|---|---|
| Quartz | 37 (36-38 in the literature) | 44 |
| Clay (TLE tutorial value) | 15 | 5 |
| Brine | 2.8 (pure water ~2.2-2.25) | 0 |
| Oil (medium) | ~0.9-1.0 | 0 |
| Gas (reservoir) | ~0.02-0.15 | 0 |

Brine is roughly 40 times stiffer than gas. Quartz is roughly 13 times stiffer than brine.

## Why one bubble matters (Wood's rule example)
With K_brine = 2.8 and K_gas = 0.06 GPa:
- Sw = 1.00 gives K_fl = 2.80
- Sw = 0.99 gives K_fl = 1.92
- Sw = 0.95 gives K_fl = 0.85
- Sw = 0.90 gives K_fl = 0.50
- Sw = 0.50 gives K_fl = 0.12

Just 5% gas removes about 70% of the fluid's stiffness. This is the root of the "fizz gas" problem (note 06): low-saturation gas looks almost like commercial gas.

## Checkable facts
- The shear modulus of any fluid is 0. [source: wikipedia-gassmann]
- In the TLE tutorial constants, quartz has K = 37 GPa and mu = 44 GPa, and clay has K = 15 GPa and mu = 5 GPa. [source: seg-tut-petrophysics-2]
- In the TLE tutorial constants, brine K = 2.8 GPa, oil K = 0.94 GPa and gas K = 0.06 GPa. [source: seg-tut-petrophysics-2]
- Mavko's Gassmann examples use K_mineral = 36 GPa, K_water = 2.2 GPa and K_oil = 1 GPa. [source: mavko-seismic-velocity-slides]
- Dvorkin et al. assume formation water K = 2.85 GPa (density 1.01) and gas K = 0.14 GPa (density 0.26) for a Gulf of Mexico well. [source: dvorkin-2005-attenuation]
- Under Wood's rule with K_brine = 2.8 and K_gas = 0.06 GPa, a mix with Sw = 0.9 has K_fl of about 0.50 GPa. [source: seg-tut-petrophysics-2]
- The TLE tutorial computes the fluid-mix bulk modulus with the Reuss (lower-bound) average. [source: seg-tut-petrophysics-2]
- Isothermal (PVT-lab) fluid moduli can be about 20% too low for oil and about a factor of 2 too low for gas, compared with the adiabatic moduli needed for waves. [source: mavko-seismic-velocity-slides]

## Sources
seg-tut-petrophysics-2, mavko-seismic-velocity-slides, dvorkin-2005-attenuation, wikipedia-gassmann, rockphypy
