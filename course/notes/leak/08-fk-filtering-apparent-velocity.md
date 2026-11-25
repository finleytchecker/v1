# 08 — f-k filtering: separating signals by speed

## The idea in plain English
The 1-D FFT turns time into frequency. Do the FFT along **both** axes of a waterfall (time → frequency f, distance → wavenumber k = 1/wavelength) and you get the **f-k spectrum**. Its key property: every wave travelling at apparent speed v lands on the straight line **f = v·k** through the origin. With f on the vertical axis, slow things (cars, 10–30 m/s) lie on shallow lines close to the k-axis; fast things (earthquakes, sound in water, km/s) lie on steep lines close to the f-axis. Waves moving one way along the cable and waves moving the other way land in opposite quadrants.

So you can **filter by speed**: keep a wedge ("fan") of velocities and zero the rest, then inverse-FFT back to a waterfall. This is called f-k, dip, fan or slope filtering.

Why it matters for leaks: a leak is a **stationary** source. In the waterfall it is a steady oscillation at frequency f0 confined to a few channels. Something narrow in space is broad in wavenumber, so in f-k a leak shows up as a **horizontal band at f ≈ ±f0 spread across many k**, not as a line through the origin. A moving car, by contrast, sits on its own velocity line. Removing the slow traffic fan (say 3–40 m/s) therefore strips out most car energy, while a leak band at a fixed frequency mostly survives (only the small part of it that overlaps the fan is lost). Removing everything outside a seismic fan is the same idea used to clean earthquake records.

Pitfalls: (1) sharp mask edges cause ringing — taper them; (2) **spatial aliasing** — waves shorter than 2 channel spacings fold to wrong k; (3) the speeds are *apparent* (along the cable), which are ≥ the true speed when waves arrive at an angle.

## Key equations
- Apparent velocity: v_app = f / k  (k in cycles per metre)
- Spatial Nyquist: k_N = 1 / (2·Δx); e.g. Δx = 2 m → k_N = 0.25 cycles/m
- Minimum unaliased wavelength: λ_min = 2·Δx
- A wave at frequency f with speed v is unaliased if f/v < 1/(2Δx), i.e. f < v/(2Δx)

## Typical real numbers
- DASCore example slope filter for seismic waves: pass 2200–8000 m/s with tapers to 2000 and 9000 m/s; S-wave emphasis 2300–3000 m/s.
- das4whales: keep 1400–3500 m/s, 10–30 Hz to isolate whale calls.
- Ocean dataset C: 1–30 Hz Butterworth then f-k keep 1.4–3 km/s.
- Car at 20 m/s and Δx = 2 m: unaliased only below f = 20/(2·2) = 5 Hz.

## Checkable facts
- In the f-k domain, signals are separated by apparent velocity = frequency / wavenumber. [source: xenaki-das-overview-2025]
- DASCore's slope_filter takes four velocities [va, vb, vc, vd]; vb–vc passes, va–vb and vc–vd are tapered. [source: dascore-fk-recipe]
- The DASCore recipe cites ~4500 m/s for P waves and ~2700 m/s for S waves. [source: dascore-fk-recipe]
- The das4whales f-k fan filter keeps 1400–3500 m/s in the 10–30 Hz band to preserve 20 Hz fin-whale song. [source: das4whales-tutorial]
- With 2 m channel spacing the spatial Nyquist wavenumber is 0.25 cycles/m (wavelengths shorter than 4 m alias). [source: seg-wiki-fk]
- Using directional=True in DASCore's slope_filter separates waves moving toward vs away from the interrogator. [source: dascore-fk-recipe]
- f-k filtering removes ground roll from seismic shot gathers by masking its slow-velocity fan. [source: pestoseis-fk-tutorial]

## Sources
xenaki-das-overview-2025, dascore-fk-recipe, das4whales-tutorial, pestoseis-fk-tutorial, seg-wiki-fk, lightguide
