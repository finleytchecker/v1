# 12 - Attenuation and Q: fluids eat high frequencies

## Plain English
Beyond simple geometric spreading, real rocks turn a bit of wave energy into heat every cycle. This is **intrinsic attenuation**. It is measured by the **quality factor Q**: the number of cycles it takes to lose a set fraction of energy. **High Q means little loss** (hard, dry rock). **Low Q means strong loss** (soft, fluid-rich, partially gas-saturated rock). Because loss happens per cycle, **high frequencies die faster** than low ones. Below a gas zone the seismic looks lower-frequency, the "low-frequency shadow".

The mechanism in reservoirs is mainly **wave-induced fluid flow**. The passing wave squeezes pores differently, fluid sloshes between them, and friction converts the motion to heat. It is strongest when the rock is partially gas-saturated (note 13), and stronger for viscous fluids at the right frequencies.

## Equations
Definition:

    1/Q = (energy lost per cycle) / (2*pi * peak stored energy)

Amplitude decay for frequency f after travel time t:

    A(f, t) = A0(f) * exp( -pi * f * t / Q )

Spectral-ratio method: ln(A2/A1) plotted against f is a straight line with slope -pi * dt / Q. Fit it to measure Q.

## Typical values (approximate)
| Rock | Qp | Qs |
|---|---|---|
| Shale | ~30 | ~10 |
| Sandstone | ~58 | ~31 |
| Granite | ~250 | 70-250 |
| Gas sand | can be well below 30 | similar to wet rock |

Dvorkin, Mavko and Walls modelled a Gulf of Mexico well and found that **1/Qp is significant only in the gas sand**, while 1/Qs stays small everywhere. The ratio (1/Qp)/(1/Qs) is about 1 in wet rock and large in gas, and it lines up with low Vp/Vs.

## Worked numbers
- Q = 50, f = 40 Hz, t = 0.5 s: exp(-pi*40*0.5/50) = 0.285, so 72% of the amplitude is lost.
- Same path at 10 Hz: 0.730.
- Q = 20 at 40 Hz: 0.043.

## Checkable facts
- Q is defined from the fraction of energy lost per cycle. Higher Q means less loss. [source: wikipedia-q]
- Amplitude after travel time t at frequency f decays as exp(-pi f t / Q). [source: wikipedia-q]
- With Q = 50, f = 40 Hz and t = 0.5 s, the amplitude falls to about 0.285 of its starting value. [source: wikipedia-q]
- In a log-spectral-ratio plot, the gradient against frequency gives Q (assuming Q does not depend on frequency). [source: wikipedia-q]
- Typical values are Qp of about 30 and Qs of about 10 for shale, and Qp of about 58 and Qs of about 31 for sandstone. [source: seg-wiki-attenuation]
- In the Gulf of Mexico well study, P-wave inverse Q was significant only in the gas reservoir, and S-wave inverse Q was small everywhere. [source: dvorkin-2005-attenuation]
- The Qp^-1/Qs^-1 ratio is about 1 in wet rock and large in gas, so it is proposed as a hydrocarbon indicator. [source: dvorkin-2005-attenuation]
- A DOE study concluded that seismic attenuation can be related to gas-bearing reservoirs and used for reconnaissance. [source: netl-nt42243-report]

## Sources
wikipedia-q, seg-wiki-attenuation, dvorkin-2005-attenuation, netl-nt42243-report, devito-tutorials, rockphypy
