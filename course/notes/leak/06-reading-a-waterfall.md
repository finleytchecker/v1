# 06 — Reading a DAS waterfall

## The idea in plain English
A **waterfall** is an image of DAS data: one axis is **distance along the cable** (channel), the other is **time**, colour is strain-rate amplitude (or energy in a band). Learning to read one is the core skill of this module because the shape of a pattern tells you what made it:

| Pattern in the waterfall | Meaning |
|---|---|
| **Straight line fixed at one position, lasting a long time** | stationary source: a **leak**, a pump, a fan, a transformer hum |
| **Diagonal straight streak** | something moving at constant speed: a car, train, walker |
| **Steep V or fan from one point** | a wave spreading out from an impact (hammer, dig, explosion) |
| **Nearly horizontal line across many channels at once** | very fast wave (earthquake) or common-mode noise hitting all channels |
| **Speckle with no structure** | random/instrument noise, wind, rain |

The **slope** of a streak = distance / time = **apparent speed**. A car streak with slope 15 m/s is a car at ~54 km/h. If you plot time on the vertical axis, a fast thing looks nearly horizontal and a stationary thing looks vertical — always check which axis is which.

A leak is the opposite of traffic: **zero slope, infinite duration, narrow frequency band**. A useful trick is to make an "energy waterfall": for each channel and each time window, compute band power (e.g. in the leak band) instead of raw amplitude. Leaks become a steady bright column; traffic becomes thin diagonal lines that pass through.

## Key equations
- Apparent speed from a streak: v = Δx / Δt (positive = moving away from interrogator, negative = toward)
- Band energy per channel per window: E(x, t) = Σ_{f in band} |S(x, t, f)|²

## Typical real numbers
- Car streaks: 5–30 m/s (Sand Hill Road cars ~15 m/s under a 15.65 m/s limit).
- Expressway search window in one paper: 60–120 km/h (16.7–33.3 m/s).
- Fin-whale calls cross the cable at ~1500 m/s; seismic waves at 200 m/s–several km/s.

## Checkable facts
- On a waterfall, a vehicle trajectory is approximately a straight line and the absolute value of its slope is the vehicle speed. [source: wang-2024-traffic-das]
- Vehicles on Sand Hill Road were measured at about 15 m/s, under a 15.65 m/s (35 mph) limit. [source: lindsey-2020-covid-traffic]
- Each car produces a localized strain wavelet that migrates along the fibre at road speed. [source: lindsey-2020-covid-traffic]
- A streak covering 300 m of cable in 20 s indicates an apparent speed of 15 m/s (54 km/h). [source: wang-2024-traffic-das]
- Stajanca et al. localized a leak by integrating 500–5000 Hz spectral power per fibre bin — an energy waterfall concept. [source: stajanca-2018-das-leak]
- DASCore plots a waterfall in one call: patch.viz.waterfall(). [source: dascore]

## Sources
wang-2024-traffic-das, lindsey-2020-covid-traffic, stajanca-2018-das-leak, dascore, das4whales-tutorial, xenaki-das-overview-2025
