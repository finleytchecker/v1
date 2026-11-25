# 07 - How well logs show oil, water and gas

## Plain English
A well log is a record of measurements taken by tools lowered down a borehole, plotted against depth. Wells are where we get **ground truth** for the Fluid module: the logs tell us which layers hold water, oil or gas, and seismic is then calibrated against that.

The main logs:
| Log | Measures | Fluid clue |
|---|---|---|
| Gamma ray (GR) | natural radioactivity (clay) | separates sand (low GR) from shale (high GR); not a fluid tool |
| Resistivity (deep, e.g. RDEP/ILD) | how hard it is to pass current | brine conducts and hydrocarbons don't, so **high resistivity in a clean, porous sand = hydrocarbons** |
| Density (RHOB) | bulk density from gamma-ray scattering | gas lowers density, so density porosity reads too high |
| Neutron (NPHI) | hydrogen content | gas has little hydrogen, so neutron porosity reads too low |
| Sonic (DTC, DTS) | P and S slowness (us/ft) | gas slows the P-wave (higher DTC). This is the direct link to seismic. |
| PEF | photoelectric factor | mineralogy (quartz ~1.8, calcite ~5) |

## The classic gas signature: neutron-density crossover
Plot neutron and density porosity on the same scale. In a water sand they track each other. In a gas sand the density porosity swings high and the neutron porosity swings low, so the curves cross with a big separation. Shale produces the opposite separation.

## Archie's law: water saturation from resistivity
    Sw^n = a * Rw / ( phi^m * Rt )
- Rt is the true formation resistivity and Rw is the formation water resistivity.
- Typical values: a ~ 0.6-1, m ~ 2 (1.8-2.0 consolidated sands, ~1.3 unconsolidated), n ~ 2.
- Sw well below 1 in a clean sand means hydrocarbons. Resistivity alone cannot tell oil from gas. You need neutron-density or sonic for that.

## Slowness and velocity
    V (m/s) = 304800 / DT (us/ft)
For example, DT = 100 us/ft gives 3048 m/s.

## Checkable facts
- Archie's law: Rt = a*Rw*phi^(-m)*Sw^(-n), with n usually close to 2. [source: wikipedia-archie]
- The cementation exponent m is about 1.8-2.0 for consolidated sandstones and about 1.3 for unconsolidated sands. [source: wikipedia-archie]
- Gas lowers neutron porosity (low hydrogen) and raises density porosity, producing a crossover distinct from the shale effect. [source: slb-defining-porosity]
- With a = 1, m = n = 2, Rw = 0.05 ohm-m, phi = 0.25 and Rt = 20 ohm-m, Archie gives Sw = sqrt(0.05/(0.0625*20)) = 0.20. [source: wikipedia-archie]
- The SEG 2016 contest logs are GR, ILD_log10 (resistivity), PE, DeltaPHI and PHIND (neutron-density difference and average), sampled every half foot. [source: seg-2016-ml-contest]
- A sonic reading of 100 us/ft equals a velocity of 3048 m/s (1 ft = 0.3048 m). [source: glover-petrophysics-notes]
- In the Dvorkin study, gas saturation was computed from the resistivity curve and clay content by linearly scaling GR between its minimum and maximum. [source: dvorkin-2005-attenuation]

## Sources
wikipedia-archie, slb-defining-porosity, glover-petrophysics-notes, seg-2016-ml-contest, force-2020-zenodo, lasio, welly, andymcd-petrophysics-python, dvorkin-2005-attenuation
