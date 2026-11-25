# 09 - Zoeppritz, Aki-Richards and Shuey: amplitude vs angle

## Plain English
When a P-wave hits a boundary at an angle, part of it reflects as P, part converts to S, and part transmits. The exact split is given by the four **Zoeppritz equations** (1919), which depend on Vp, Vs and rho on both sides. The key idea: **at normal incidence only impedance matters, but at larger angles the S-wave contrast enters too.** Since fluids change Vp and rho but not mu, watching amplitude change with angle (AVO/AVA) lets us separate fluid effects from rock effects.

## Approximations
**Aki-Richards** (small contrasts): a sum of three terms in dVp/Vp, dVs/Vs and drho/rho.

**Shuey three-term**:

    R(theta) = A + B sin^2(theta) + C (tan^2(theta) - sin^2(theta))
    A (intercept) = 1/2 (dVp/Vp + drho/rho)
    B (gradient)  = 1/2 dVp/Vp - 2 (Vs/Vp)^2 (drho/rho + 2 dVs/Vs)
    C (curvature) = 1/2 dVp/Vp

**Two-term Shuey**, R = A + B sin^2(theta), is good below about 30 degrees. Plot amplitude against sin^2(theta) and fit a straight line: the intercept is A and the slope is B.

Other variants you'll meet: Fatti (in terms of Ip, Is and rho, used by PyLops) and elastic impedance (EI).

## Worked numbers (shale Vp 3.0, Vs 1.4, rho 2.40 over the note 06 sands)
| Sand | A | B | R at 30 deg |
|---|---|---|---|
| Brine | +0.004 | -0.17 | -0.039 |
| Gas | -0.092 | -0.25 | -0.155 |

The gas sand starts negative and gets more negative with angle: its amplitude magnitude grows with offset. That is a Class III AVO response (note 10).

## Critical angle
When V2 > V1, beyond sin(theta_c) = V1/V2 the P-wave can't transmit and the reflection coefficient becomes complex. The linear approximations fail well before this.

## Checkable facts
- The Zoeppritz equations date from 1919 and involve six elastic parameters (Vp, Vs and rho on each side). [source: wikipedia-avo]
- Shuey's three-term form is R(theta) = R(0) + G sin^2(theta) + F(tan^2(theta) - sin^2(theta)). [source: wikipedia-zoeppritz]
- The third Shuey term can be dropped for incidence angles below about 30 degrees. [source: wikipedia-zoeppritz]
- In Shuey's equation, F = 1/2(dVp/Vp). [source: wikipedia-zoeppritz]
- Shuey's approximation was published in 1985, and Ostrander showed the first practical gas-sand AVO case (published 1984). [source: wikipedia-avo]
- For the shale over gas-sand example, A is about -0.092 and B about -0.25, giving R(30 deg) of about -0.155. [source: wikipedia-zoeppritz]
- PyLops pre-stack modelling supports the 'akirich', 'fatti' and 'ps' linearisations. [source: pylops-prestack]
- bruges implements Zoeppritz and Aki-Richards reflectivity. [source: bruges]

## Sources
wikipedia-zoeppritz, wikipedia-avo, seg-wiki-avo-equations, seg-wiki-yilmaz-avo, bruges, pylops-prestack, crewes-zoeppritz-explorer, aadm-avo-explorer
