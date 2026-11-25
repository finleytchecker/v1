# 01 - Rocks, pores and fluids

## The picture to keep in your head
A reservoir rock such as sandstone is a skeleton of mineral grains, mostly quartz. The gaps between the grains are the **pores**. The pores are always full of something: salty water (brine), oil, gas, or a mix. "Dry rock" in the Fluid module's sense means the pores hold brine but no hydrocarbons. Truly empty pores only happen in the lab.

Three numbers describe the rock for our purposes:

- **Porosity (phi)**: the fraction of the volume that is pore space. Reservoir sands are typically 0.15 to 0.35, tight rocks below 0.10.
- **Water saturation (Sw)**: the fraction of the pore space filled with water. The rest (1 - Sw) is hydrocarbon. A water-wet sand with no hydrocarbons has Sw = 1.
- **Shale volume (Vsh)**: how much clay is mixed in. Clay-rich rock (shale) is usually the seal above a reservoir, not the reservoir itself.

## Why seismic can "see" fluids at all
A seismic wave is a tiny squeeze-and-shake travelling through the rock. How fast it goes depends on how stiff the rock is and how heavy it is. The fluid in the pores changes both:
- Water is fairly stiff, so it resists being squeezed. Gas is very soft. Swapping water for gas makes the rock easier to compress, and the P-wave slows down.
- Gas is light, so the rock gets lighter.
- No fluid can resist being sheared, so fluids don't change the rock's shear stiffness. They only change its density a little.

Everything else in this module builds on these three effects.

## Density of a fluid-filled rock
Bulk density is just a volume-weighted average:

    rho_bulk = (1 - phi) * rho_mineral + phi * rho_fluid
    rho_fluid = Sw * rho_brine + (1 - Sw) * rho_hc

## Typical numbers
| Material | Density (g/cc) |
|---|---|
| Quartz | 2.65 |
| Calcite | 2.71 |
| Clay (as used in the TLE tutorial) | 2.81 |
| Brine | ~1.0-1.1 (1.09 in the tutorial) |
| Oil | 0.6-0.9 (0.78 in the tutorial) |
| Gas (reservoir conditions) | ~0.1-0.3 (0.25 in the tutorial) |

## Checkable facts
- Quartz grain density is 2.65 g/cc and calcite is 2.71 g/cc. [source: mavko-seismic-velocity-slides]
- Oil density is in the range 0.6-0.9 g/cc and water is about 1.0 g/cc. [source: mavko-seismic-velocity-slides]
- Wet sands have bulk density 1.9-2.1 g/cc, while dry sands are 1.5-1.7 g/cc. [source: mavko-seismic-velocity-slides]
- For a quartz sand with phi = 0.25 and brine density 1.09 g/cc, bulk density = 0.75*2.65 + 0.25*1.09 = 2.26 g/cc. [source: seg-tut-petrophysics-2]
- The same sand filled with gas of density 0.25 g/cc has bulk density 2.05 g/cc, about 9% lighter. [source: seg-tut-petrophysics-2]
- In the TLE tutorial, a sand is flagged "brine sand" when Vsh <= 0.20 and Sw >= 0.9, and "oil sand" when Vsh <= 0.20 and Sw < 0.9. [source: seg-tut-petrophysics-2]

## Sources
mavko-seismic-velocity-slides, seg-tut-petrophysics-1, seg-tut-petrophysics-2, glover-petrophysics-notes
