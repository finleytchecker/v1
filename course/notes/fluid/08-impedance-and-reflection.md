# 08 - Acoustic impedance, reflection coefficients and the convolutional model

## Plain English
Seismic doesn't measure velocity directly. It records **echoes** from boundaries where rock properties change. How strong an echo is depends on the jump in **acoustic impedance**:

    Z = Ip = rho * Vp

At vertical (normal) incidence the reflection coefficient is

    R0 = (Z2 - Z1) / (Z2 + Z1)   ~   1/2 * (dVp/Vp + drho/rho)

Layer 1 is above and layer 2 below. A positive R0 means the lower layer is "harder". Gas lowers both Vp and rho, so it lowers Z. A gas sand under shale therefore usually gives a **negative** reflection, often strong.

## The convolutional model
A seismic trace is roughly the **wavelet** (the source pulse, ~10-60 Hz) convolved with the **reflectivity series** (one R per boundary), plus noise:

    trace(t) = wavelet(t) * r(t) + noise

This is the forward model inside post-stack inversion (note 14) and inside synthetic seismograms made from well logs (the "well tie").

## Resolution and tuning
A layer thinner than about a quarter wavelength (lambda/4, where lambda = V/f) can't be resolved. Its top and bottom reflections interfere and the amplitude is "tuned". For V = 3000 m/s and f = 30 Hz, lambda = 100 m and tuning thickness is ~25 m. Thin-bed tuning can mimic or hide fluid effects.

## Worked numbers (from note 06's sand under a shale with Vp = 3.0, Vs = 1.4, rho = 2.40, so Z = 7.20)
- Brine sand, Z = 7.25: R0 of about +0.003, nearly invisible.
- Gas sand, Z = 5.99: R0 of about -0.092, a strong negative ("bright") reflection.

## Checkable facts
- R0 = (Z2 - Z1)/(Z2 + Z1) with Z = rho*Vp. [source: wikipedia-zoeppritz]
- The linearised normal-incidence coefficient is R(0) = 1/2(dVp/Vp + drho/rho). [source: wikipedia-zoeppritz]
- For shale Z = 7.20 over gas sand Z = 5.99 (units km/s*g/cc), R0 is about -0.092. [source: wikipedia-zoeppritz]
- The normal-incidence trace is the convolution of the seismic wavelet with the reflectivity function. [source: wikipedia-seismic-inversion]
- Wavelength lambda = V/f, so V = 3000 m/s at 30 Hz gives lambda = 100 m and a quarter-wavelength tuning thickness of 25 m. [source: seg-tutorials-2014]
- Hydrocarbons have lower acoustic impedance than the brine-saturated rock they replace. [source: wikipedia-bright-spot]

## Sources
wikipedia-zoeppritz, wikipedia-seismic-inversion, wikipedia-bright-spot, seg-tutorials-2014, pylops-poststack, welly, bruges
