# 11 — How leak noise travels: pipe material, wave speed and attenuation

## The idea in plain English
Inside a water-filled pipe, leak noise rides mainly on one wave in which the water and the pipe wall move together. How fast it goes, and how quickly it fades, depends on **how stiff the pipe wall is** compared with the water:

- **Stiff walls (steel, cast iron, ductile iron)** barely bulge, so the wave travels fast (close to ~1000–1400 m/s) and fades slowly — leaks can be heard far away and at higher frequencies.
- **Soft walls (PVC, MDPE, HDPE)** bulge a lot, so the wave is slow (~300–500 m/s) and loses energy quickly into the wall (damping) and the soil (radiation). Higher frequencies fade fastest, so **the pipe acts as a low-pass filter whose cutoff drops the further you are from the leak**.

Practical consequences:
- In plastic pipes, usable leak noise at 20–30 m is often below ~100 Hz.
- Plastic wave speed changes with temperature (the plastic stiffens in cold weather) and with pipe size/thickness, so it is uncertain.
- Joints, repairs with different material, diameter changes and side branches reflect energy and shorten detection range.
- The surrounding soil matters less for wave speed (below ~500 Hz) but adds attenuation.
- **Sensor choice is a filter too**: a hydrophone (pressure) favours lower frequencies; an accelerometer (∝ displacement × f²) boosts higher frequencies, giving sharper location but lower SNR.

For DAS on a nearby buried cable, add one more filter: the soil path from pipe to fibre, which removes still more high frequency. Expect the leak to appear in the low tens to low hundreds of Hz on plastic mains.

## Key equations
- Fluid-wave speed in a thin-walled pipe (Korteweg-type): c = c_f · (1 + 2·B·a / (E·h))^(−1/2)
  - c_f free water sound speed (~1500 m/s), B water bulk modulus (2.2 GPa), a pipe mean radius, E Young's modulus of wall, h wall thickness
- Attenuation: loss (dB/m) = 8.67 · β · ω  (from Almeida et al.'s model; grows linearly with frequency)

Worked example (plastic): B = 2.2 GPa, a = 75 mm, E = 2 GPa, h = 9.85 mm → 2Ba/(Eh) ≈ 16.8 → c ≈ 1500/√17.8 ≈ 356 m/s.

## Typical real numbers
- Buried plastic rig: c ≈ 356 m/s; field seasonal range ~350–420 m/s; E ≈ 2.8 GPa gives ~416 m/s.
- At 150 Hz with β = 1.99×10⁻⁴: ~1.6 dB/m → ~32 dB lost over 20 m, ~48 dB over 30 m.
- 170 mm MDPE: ~400 m/s. 63 mm MDPE lab loop: ~331 m/s theoretical.
- Leak noise detected in plastic pipe generally up to about 100 Hz.

## Checkable facts
- The fluid-borne wave speed in a pipe is c = c_f(1 + 2Ba/Eh)^(−1/2); free-field water speed 1500 m/s and bulk modulus 2.2×10⁹ N/m². [source: almeida-2014-plastic-pipe-filtering]
- On the buried plastic test rig the measured leak-noise speed was 356 m/s. [source: almeida-2014-plastic-pipe-filtering]
- Attenuation in that pipe was about 1.6 dB/m at 150 Hz, i.e. ~32 dB over 20 m. [source: almeida-2014-plastic-pipe-filtering]
- Usable strong-leak bandwidth was 10–28 Hz for hydrophones and 10–104 Hz for accelerometers at 20–30 m from the leak. [source: almeida-2014-plastic-pipe-filtering]
- Because amplitude decays with distance and frequency, a plastic pipe behaves like a low-pass filter whose cutoff decreases with distance from the leak. [source: brennan-soton-plastic-leak-article]
- Up to ~500 Hz the surrounding ground has very little effect on the wave speed in a buried plastic pipe. [source: brennan-soton-plastic-leak-article]
- An accelerometer amplifies high frequencies relative to a hydrophone because acceleration ∝ displacement × frequency². [source: brennan-soton-plastic-leak-article]
- The theoretical wave speed for a 63 mm MDPE test loop was 331 m/s. [source: butterfield-2017-backfill-mdpe]

## Sources
almeida-2014-plastic-pipe-filtering, brennan-soton-plastic-leak-article, butterfield-2017-backfill-mdpe, scussel-2023-acoustics-bandwidth, gao-2004-correlation-model, hunaidi-2000-detecting-leaks-plastic
