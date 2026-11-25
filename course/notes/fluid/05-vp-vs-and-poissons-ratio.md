# 05 - Vp/Vs ratio and Poisson's ratio

## Plain English
Because gas lowers Vp but not Vs (Vs even rises a little), the **ratio Vp/Vs** drops sharply in gas sands. This works whatever the absolute velocity is, which makes it a cleaner fluid indicator than Vp alone. **Poisson's ratio (nu)** is the same information in a different form. It measures how much a material bulges sideways when squeezed.

## Equations
    nu = (Vp^2 - 2 Vs^2) / (2 (Vp^2 - Vs^2))
    Vp/Vs = sqrt( (2 - 2 nu) / (1 - 2 nu) )

Special values:
- Vp/Vs = sqrt(2) = 1.414 gives nu = 0. This is the physical lower limit for normal rocks.
- Vp/Vs = sqrt(3) = 1.732 gives nu = 0.25. This is a "Poisson solid", close to many consolidated rocks.
- Vp/Vs = 2.0 gives nu = 0.333.
- A fluid has Vs = 0, so Vp/Vs is infinite and nu = 0.5.

## Typical ranges
| Rock | Vp/Vs | nu |
|---|---|---|
| Gas sand | ~1.5-1.7 | ~0.1-0.2 |
| Oil sand | ~1.65-1.8 | ~0.2-0.27 |
| Brine sand | ~1.8-2.2 | ~0.28-0.37 |
| Shale | ~1.9-2.5+ | ~0.3-0.4 |
| Very soft, shallow wet sediment | 3-10+ | >0.45 |

A worked example from note 06 (phi = 0.25 sand) gives Vp/Vs of 1.82 for brine, 1.67 for oil and 1.58 for gas.

## Other useful elastic combinations (rock-physics templates)
- P-impedance Ip = rho*Vp, S-impedance Is = rho*Vs
- Lambda-rho = Ip^2 - 2 Is^2. This is sensitive to fluid and very low in gas.
- Mu-rho = Is^2. This is sensitive to the rock frame, not the fluid.
- The **Ip vs Vp/Vs crossplot** is the workhorse plot. Shales sit at high Vp/Vs, brine sands in the middle and gas sands at low Vp/Vs and low Ip.

## Checkable facts
- nu = (Vp^2 - 2Vs^2)/(2(Vp^2 - Vs^2)). [source: wikipedia-poisson]
- When Vp/Vs = sqrt(3), Poisson's ratio is exactly 0.25. [source: wikipedia-poisson]
- When Vp/Vs = 2, Poisson's ratio is 1/3. [source: wikipedia-poisson]
- When Vp/Vs = sqrt(2), Poisson's ratio is 0. [source: wikipedia-poisson]
- A low Vp/Vs is typical of gas sand. [source: dvorkin-2005-attenuation]
- The TLE tutorial computes VPVS = VP/VS and uses Ip vs Vp/Vs crossplots coloured by litho-fluid class. [source: seg-tut-petrophysics-1]
- An ML prospecting study on Poseidon used Lambda-Rho, impedances and Vp/Vs as inputs. [source: arxiv-2410-21960-poseidon-ml]

## Sources
wikipedia-poisson, seg-tut-petrophysics-1, seg-tut-petrophysics-2, dvorkin-2005-attenuation, aadm-geophysical-notes, arxiv-2410-21960-poseidon-ml
