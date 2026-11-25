# 12 — Locating leaks with correlators

## The idea in plain English
The classic water-industry tool is the **leak noise correlator**. Put two sensors on the pipe (often at hydrants or valves) on either side of a suspected leak, distance d apart. The leak hiss reaches the nearer sensor first. **Cross-correlate** the two recordings: the lag at which they match best is the arrival-time difference Δt. With the wave speed c you can solve for where the leak is.

Why this matters for DAS: a fibre gives you thousands of "sensors" for free. Cross-correlating pairs of DAS channels (or beamforming) along a cable that runs beside a pipe can locate a stationary source the same way, and the peak sharpness tells you how well it is localised. It is also the basis of **ambient noise interferometry** in seismology.

What spoils it:
- Wrong wave speed c → wrong position (plastic pipe c is uncertain, see note 11).
- Low-pass filtering by the pipe makes the peak broad → poorer location. Higher frequency content gives a sharper peak.
- If the sensors are at very different distances from the leak, their signals pass through different "filters" and correlate poorly. Worst case: one sensor at the leak, one far away.
- Other steady noise (pumps, traffic) correlated at both sensors creates false peaks. Pre-whitening estimators (e.g. SCOT, PHAT) help.

## Key equations
- Define d1, d2 = distances from the leak to sensors 1 and 2 (d1 + d2 = d), and T0 = t1 − t2 = (d1 − d2) / c (positive if the leak is nearer sensor 2).
- Then d2 = (d − c·T0) / 2 and d1 = (d + c·T0) / 2. Other texts flip the sign of the delay; always state your convention.
- Correlation coefficient: ρ(τ) = R_x1x2(τ) / sqrt(R_x1x1(0) · R_x2x2(0)), ranging −1…+1
- Time delay from cross-spectrum phase: τ ≈ −φ(ω)/ω (slope of phase vs frequency)

Worked example: d = 50 m, c = 356 m/s, measured lag 25.8 ms → d2 = (50 − 356×0.0258)/2 ≈ 20.4 m.

## Typical real numbers
- Test rig: sensors 20 m and 30 m from the leak; delays ~24–26 ms; location errors ~0.4–0.7 m.
- Measurement time: minutes; SNR gains ~3 dB per doubling of record length.

## Checkable facts
- The leak position is d2 = (d − c·T0)/2, where d is the sensor separation, c the wave speed and T0 the time delay. [source: almeida-2014-plastic-pipe-filtering]
- On the buried plastic rig a strong leak gave a hydrophone time delay of 25.8 ms and an estimated d2 of 20.41 m against a true 20 m. [source: almeida-2014-plastic-pipe-filtering]
- For a weak leak, the hydrophone gave no usable correlation peak while geophone and accelerometer still located it. [source: almeida-2014-plastic-pipe-filtering]
- A correlation peak value of 1 only occurs with no background noise and sensors equidistant from the leak. [source: brennan-soton-plastic-leak-article]
- The worst sensor arrangement is one sensor at the leak and the other far away. [source: brennan-soton-plastic-leak-article]
- Cross-correlation works reasonably well on metal pipes but has been problematic on plastic pipes. [source: brennan-soton-plastic-leak-article]
- Professional correlator crews rarely located leaks in plastic pipe because the frequency range selected was usually too high. [source: hunaidi-2000-detecting-leaks-plastic]

## Sources
almeida-2014-plastic-pipe-filtering, brennan-soton-plastic-leak-article, gao-2004-correlation-model, hunaidi-2000-detecting-leaks-plastic, ajo-franklin-2019-dark-fiber
