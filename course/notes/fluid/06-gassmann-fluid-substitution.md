# 06 - Gassmann fluid substitution

## Plain English
**Fluid substitution** answers this question: "This well log was recorded in a brine sand. What would Vp, Vs and density be if the same rock held gas or oil instead?" Gassmann's 1951 equation does it by
1. stripping the current fluid out mathematically to get the **dry-frame** modulus K_dry,
2. putting the new fluid in, and
3. leaving the shear modulus alone, since fluids can't resist shear.

This is the engine behind AVO modelling, rock-physics templates and synthetic training data for the Fluid ML model.

## Equations
Saturated bulk modulus from the dry frame:

    K_sat = K_dry + (1 - K_dry/K0)^2 / ( phi/K_fl + (1-phi)/K0 - K_dry/K0^2 )

Inverse step (dry frame from the measured saturated rock):

    K_dry = ( K_sat1*(phi*K0/K_fl1 + 1 - phi) - K0 ) / ( phi*K0/K_fl1 + K_sat1/K0 - 1 - phi )

Other rules:

    mu_sat = mu_dry          (shear unchanged)
    rho_2  = rho_1 + phi*(rho_fl2 - rho_fl1)

Recipe:
1. From logs, get mu = rho*Vs^2 and K_sat1 = rho*(Vp^2 - 4/3 Vs^2).
2. Get K0 (mineral mix, VRH average) and K_fl1 (in-situ fluid, Reuss mix).
3. Invert for K_dry.
4. Forward model with K_fl2 to get K_sat2, update density, and recompute Vp and Vs.

## Assumptions (and when it breaks)
- The rock is isotropic and homogeneous, with a single mineral (Brown-Korringa generalises this).
- All pores are connected and pore pressure equalises during the wave cycle. This is the **low-frequency** limit of Biot theory. It is fine at seismic frequencies (10-100 Hz) but can be wrong at sonic-log frequencies (~20 kHz).
- The fluid does not chemically alter the frame, and porosity does not change.
- It is poor for shales and very tight rocks, where the pores don't communicate.

## Worked example (computed for this course)
Quartz sand with phi = 0.25, K0 = 37 GPa, K_dry = 8 GPa, mu_dry = 7 GPa, mineral density 2.65:

| Fluid | K_sat (GPa) | rho | Vp (km/s) | Vs (km/s) | Vp/Vs | Ip |
|---|---|---|---|---|---|---|
| Brine (2.8, 1.09) | 13.92 | 2.260 | 3.21 | 1.76 | 1.82 | 7.25 |
| Oil (0.94, 0.78) | 10.19 | 2.183 | 2.99 | 1.79 | 1.67 | 6.53 |
| Gas (0.06, 0.25) | 8.15 | 2.050 | 2.92 | 1.85 | 1.58 | 5.99 |

**Fizz gas**: with Sw = 0.95 (only 5% gas) Vp is already 2.93 km/s, almost the same as 100% gas (2.92). Vp cannot tell commercial gas from a trace of gas. Density can, because it changes linearly with saturation, which is why density from far-angle AVO or inversion matters.

## Checkable facts
- Under Gassmann, the saturated shear modulus equals the dry shear modulus. [source: wikipedia-gassmann]
- Gassmann assumes porosity does not change between fluid scenarios. [source: wikipedia-gassmann]
- Gassmann is the low-frequency limit of Biot theory. Seismic is 10-100 Hz, while sonic logs run at about 20 kHz, where the assumptions may be violated. [source: wikipedia-gassmann]
- Density after substitution follows rho2 = rho1 + phi*(rho_fl2 - rho_fl1). [source: wikipedia-gassmann]
- For phi = 0.25, K0 = 37, K_dry = 8 and K_fl = 2.8 GPa, Gassmann gives K_sat of about 13.9 GPa. [source: seg-tut-petrophysics-2]
- Replacing brine (K 2.8) with gas (K 0.06) in that sand drops Vp from about 3.21 to 2.92 km/s (-9%) and raises Vs from 1.76 to 1.85 km/s. [source: seg-tut-petrophysics-2]
- In the same sand, 5% gas saturation (Sw = 0.95, Wood mix) already lowers Vp to about 2.93 km/s. [source: seg-tut-petrophysics-2]
- The fluid effect on rock modulus is largest for soft, low-velocity rock. [source: mavko-seismic-velocity-slides]
- Gassmann's equation was published in 1951, and Brown and Korringa generalised it in 1975. [source: wikipedia-gassmann]

## Sources
wikipedia-gassmann, seg-tut-petrophysics-2, smith-2003-gassmann-tutorial, mavko-seismic-velocity-slides, seg-wiki-gassmann, bruges, rockphypy
