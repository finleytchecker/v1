# 07 — What else is in the data: traffic, trains, wind, rain, digging, earthquakes

## The idea in plain English
A leak detector is really a "everything-else rejector". Each competing source has a typical **frequency band**, **duration** and **spatial footprint**:

- **Traffic (cars, trucks)** — two parts: (1) a slow *quasi-static* squeeze of the road as the axle load passes (0.1–1 Hz), moving at vehicle speed; (2) faster *surface waves* radiated by tyres (≈3–30 Hz). Heavier vehicles → bigger amplitude. Strain decays roughly as 1/r² with distance from the fibre, so the far lane is weaker.
- **Trains** — the most energetic broadband source near rail lines; a few passes per day.
- **Human activity (walking, running)** — short repeated impacts at a fixed cadence, low speed (1–3 m/s).
- **Digging / excavators** — repeated impulsive events at one spot; excavator energy concentrates at 1–10 Hz (especially 2–4 Hz) in one pipeline-protection study. Dangerous because it is also *stationary* like a leak — but it is intermittent and impulsive, not steady.
- **Wind and rain** — incoherent noise across many channels, strongest where the cable is shallow or aerial.
- **Machinery (pumps, fans, transformers)** — steady and narrow-band *and* fixed in space: the hardest false alarm for a leak detector. Mains-related hum appears at 50/60 Hz and harmonics.
- **Earthquakes** — brief, cover many channels almost simultaneously (fast apparent speed), low frequency for distant events (0.01–1 Hz).

## Key equations
- Quasi-static strain from a moving load is roughly a fixed shape translated at the vehicle speed: ε(x, t) ≈ g(x − v·t)
- Geometric decay of car strain with offset r: amplitude ∝ 1/r² (approximate)

## Typical real numbers
| Source | Band | Notes |
|---|---|---|
| Car quasi-static | 0.1–1 Hz | 5–10 nε peak |
| Car/truck surface waves | 3–30 Hz | infrastructure noise 2–30 Hz |
| Anthropogenic noise generally | 5–30 Hz dominates urban DAS | |
| Excavator | 1–10 Hz (2–4 Hz strongest) | intermittent |
| Regional earthquakes | 0.1–0.4 Hz filtered | teleseisms 0.01–0.1 Hz |
| Ship noise (ocean) | 40–60 Hz | |

## Checkable facts
- Vehicles produce surface waves at roughly 3–30 Hz, while their quasi-static road-loading signal occupies ~0.1–1 Hz. [source: lindsey-2020-covid-traffic]
- Car strain amplitude falls off roughly with 1/r² from the fibre, so far-lane traffic is weaker. [source: lindsey-2020-covid-traffic]
- In urban dark-fibre DAS, anthropogenic signals usually dominate the 5–30 Hz band. [source: ajo-franklin-2019-dark-fiber]
- Freight trains were the most energetic broadband noise source on the FOSSA array, passing 2–6 times per day. [source: ajo-franklin-2019-dark-fiber]
- Excavator vs no-excavator differences are largest at 1–10 Hz, especially 2–4 Hz. [source: bublin-2021-event-detection]
- Heavier vehicles produce higher-SNR surface waves; vehicles can be grouped light/mid/heavy by quasi-static amplitude. [source: liu-2024-vehicle-das]
- The BJTU phi-OTDR dataset has six classes: background, digging, knocking, watering, shaking, walking. [source: bjtu-phi-otdr-dataset]
- Ship noise in ocean DAS appears at 40–60 Hz. [source: xenaki-das-overview-2025]

## Sources
lindsey-2020-covid-traffic, ajo-franklin-2019-dark-fiber, liu-2024-vehicle-das, bublin-2021-event-detection, bjtu-phi-otdr-dataset, mendeley-das-power-cable, xenaki-das-overview-2025, pubdas-foresee
