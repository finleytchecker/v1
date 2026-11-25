# 10 — How a leak makes noise

## The idea in plain English
Water (or gas) under pressure squirts out through a crack or hole. The escaping **turbulent jet**, plus cavitation and the water/soil being stirred up around the hole, makes broadband noise — a hiss. Some of it goes into the pipe wall and the fluid inside the pipe and travels along the pipe; some radiates into the surrounding soil.

Key properties of leak noise:
- **Steady**: it is on 24/7 as long as the pipe is pressurised (unlike traffic or digging). This is the single most useful feature.
- **Broadband at the source, band-limited at the sensor**: the source spectrum falls off roughly like 1/f up to a cutoff that depends on hole size and jet speed (Papastefanou's thesis; later work says the exact power law varies). Then the pipe, soil and sensor filter it (note 11), so what you measure is a band.
- **Louder with higher pressure and bigger flow**: more pressure → faster jet → more energy and generally more high-frequency content. In a lab MDPE rig, leak energy appeared above ~214 Hz on accelerometers, and its amplitude grew with leak flow rate.
- **Material matters**: metal pipes carry higher frequencies further (hundreds of Hz to ~1.5 kHz is commonly quoted); plastic pipes are dominated by low frequencies (tens of Hz to ~100–200 Hz at practical distances).
- **Gas leaks** in a pressurised steel test pipe produced vibration mainly at 500 Hz–5 kHz on a fibre wrapped around the pipe.

For DAS on a buried telecom cable (not touching the pipe) the fibre feels the leak through the soil, so expect mostly the **low-frequency end** (tens to a few hundred Hz) and sample at ≥1 kHz if you can.

## Key equations
- Source spectrum model: S(f) ∝ f^(−1) for f < f_c (cutoff set by hole size and jet velocity) — an approximation.
- Jet velocity from pressure (Bernoulli/Torricelli): v_jet ≈ sqrt(2·Δp / ρ); 4 bar → v ≈ sqrt(2·4e5/1000) ≈ 28 m/s.

## Typical real numbers
| Situation | Measured band |
|---|---|
| Gas leak on DN100 steel lab pipe, wrapped fibre | 500 Hz–5 kHz |
| MDPE 63 mm lab loop, accelerometers | energy above ~214 Hz |
| Buried plastic pipe field rig, hydrophone/accelerometer at 20–30 m | 10–28 Hz / 10–104 Hz |
| 6-inch cast-iron main (patent example) | ~200–800 Hz |
| Ottawa plastic test site main peak | 55–65 Hz |

## Checkable facts
- In a DAS lab test, leak-induced pipe vibrations were mainly between ~500 Hz and 5 kHz. [source: stajanca-2018-das-leak]
- The smallest leak detected by DAS in that test was 1 mm at 5 bar (~0.14% of volume flow). [source: stajanca-2018-das-leak]
- In an MDPE loop, leak signals began at about 214 Hz and background noise dominated below ~213 Hz. [source: butterfield-2017-backfill-mdpe]
- Backfill type strongly affected leak amplitude but did not change the ~214 Hz cut-on frequency. [source: butterfield-2017-backfill-mdpe]
- Leak noise from water-filled plastic pipe follows roughly an ω^(−1) power law up to a cutoff depending on leak size and flow velocity. [source: papastefanou-2011-thesis]
- A single power law cannot always describe leak noise in buried plastic pipes. [source: scussel-2020-leak-spectrum]
- Correlators failed on plastic pipes mainly because they listened at too-high frequencies; plastic-pipe leak noise is low-frequency. [source: hunaidi-2000-detecting-leaks-plastic]
- A 6-inch cast-iron network may excite a middle band of about 200–800 Hz. [source: subband-leak-patent]

## Sources
stajanca-2018-das-leak, butterfield-2017-backfill-mdpe, papastefanou-2011-thesis, scussel-2020-leak-spectrum, hunaidi-2000-detecting-leaks-plastic, subband-leak-patent, almeida-2014-plastic-pipe-filtering
