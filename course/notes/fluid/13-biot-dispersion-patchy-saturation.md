# 13 - Biot theory, dispersion and patchy saturation

## Plain English
Gassmann (note 06) assumes the wave is slow enough for pore pressure to even out everywhere. **Biot (1956)** extended this to any frequency by letting the fluid move relative to the frame. Two consequences matter for the Fluid module:

1. **Velocity dispersion**: velocity depends on frequency. At high frequency the fluid has no time to flow, so the rock acts stiffer and faster. Lab ultrasonic (~1 MHz) and sonic-log (~20 kHz) velocities can therefore be faster than seismic (10-100 Hz) velocities in the same rock.
2. **Attenuation peaks** where the frequency matches a fluid-flow timescale. That timescale depends on permeability, viscosity and the size of fluid patches. Thicker, more viscous fluids shift the peak.

Biot's own "global flow" mechanism is usually too weak at seismic frequencies. The larger effects come from local flows:
- **Squirt flow**: between soft cracks and stiff pores, at grain scale.
- **Mesoscopic / patchy saturation**: between gas-rich and water-rich patches (cm to m scale).

## Uniform vs patchy saturation
- **Uniform (fine mix)**: mix the fluids with Wood's rule first, then apply Gassmann. A tiny amount of gas gives a big Vp drop (fizz-gas curve).
- **Patchy (coarse mix)**: apply Gassmann separately to brine patches and gas patches, then average the *rock* moduli. Vp falls roughly linearly with gas saturation.
- Real reservoirs lie between these two bounds. This is a large source of uncertainty in estimating saturation from seismic.

## Key relation (Biot characteristic frequency)
    f_c = (phi * eta) / (2 * pi * rho_fl * kappa)
Here eta is viscosity and kappa is permeability. Below f_c you are in the Gassmann regime. Higher viscosity raises f_c, which is one reason heavy oil behaves differently.

## Checkable facts
- Gassmann is the zero-frequency limit of Biot's theory. [source: wikipedia-gassmann]
- At ultrasonic frequencies, the fluid stiffening of both bulk and shear moduli is exaggerated, so lab velocities are contaminated by dispersion. [source: mavko-seismic-velocity-slides]
- rockphypy implements Biot, Geertsma-Smit, squirt-flow and patchy-saturation dispersion and attenuation models. [source: rockphypy]
- Under uniform (Wood-mixed) saturation, 5% gas in the note 06 sand gives Vp of about 2.93 km/s, compared with 3.21 for brine and 2.92 for full gas. [source: seg-tut-petrophysics-2]
- Increasing pore pressure softens the frame (opening cracks) but stiffens the fluid, so these two effects on velocity compete. [source: mavko-seismic-velocity-slides]
- Attenuation in partially saturated media is sensitive to changes in gas saturation. [source: seg-wiki-attenuation]

## Sources
wikipedia-gassmann, mavko-seismic-velocity-slides, rockphypy, seg-wiki-attenuation, dvorkin-2005-attenuation, stanford-rph2-codes
