# 05 — DAS data: formats, sizes and tools

## The idea in plain English
DAS produces a 2-D array per time block: **channels × time samples**. Because there are thousands of channels sampled hundreds of times per second, files get huge fast. Most of the practical work in a DAS project is reading files, cutting out the channels and time span you need, and decimating (down-sampling) before analysis.

Common file formats:
- **HDF5** (.h5) — hierarchical container; used by OptaSense, Febus, many archives, and ML datasets (one event per file).
- **TDMS** — National Instruments format used by Silixa iDAS.
- **SEG-Y** — old seismic-industry format; Stanford, FORGE, PoroTomo.
- **.mat** (MATLAB, often HDF5 underneath) and **CSV** for small ML datasets.

Python libraries hide most of this: **DASCore** (Patch = one block, Spool = collection of files; `patch.viz.waterfall()` plots), **xdas** (xarray/dask-style, larger-than-memory), **DASPy** (classic + DAS-specific processing), **lightguide** (Pyrocko based). For V1 (local-only) plan around *subsets*: a few GB, not TB.

## Key equations
- Raw data rate (bytes/s) = n_channels × fs × bytes_per_sample
  - e.g. 10,000 channels × 500 Hz × 4 bytes (float32) = 20 MB/s ≈ 1.7 TB/day
- Decimation by factor q: new fs = fs / q (low-pass first to avoid aliasing)

## Typical real numbers
- A 2 km fibre at 1 m and 2 kHz yields ~650 GB/day.
- FOSSA: 128 TB in first 3 months, ~0.3 PB total; a single interrogator can exceed 20 TB/day at maximum rates.
- One 60 s OOI file (32,600 channels, 200 Hz) ≈ 850 MB.
- PubDAS total ~90 TB; PoroTomo ~172 TB; quakeflow_das 674 GB; DAS4Whale 37.6 GB.

## Checkable facts
- A DAS system at 2000 Hz, 1 m resolution over 2 km produces approximately 650 GB of data per day. [source: shao-2025-ai-das-photonix]
- The FOSSA array generated 128 TB in its first three months and ~0.3 PB in total. [source: ajo-franklin-2019-dark-fiber]
- PubDAS hosts eight datasets totalling about 90 TB, in TDMS, HDF5 and SEG-Y formats. [source: pubdas-spica-2023]
- FORESEE is the largest PubDAS dataset (~29 TB) even after downsampling from 500 to 125 Hz. [source: pubdas-spica-2023]
- In DASCore, a Patch holds contiguous data plus metadata and a Spool is a collection of patches. [source: dascore]
- quakeflow_das stores each event as a 2-D float32 array (channels × time) in microstrain/s with dt_s and dx_m attributes. [source: quakeflow-das-hf]
- A single 60 s OOI DAS file with 32,600 channels at 200 Hz is about 850 MB. [source: das4whales-tutorial]
- 10,000 channels × 500 Hz × 4 bytes ≈ 20 MB/s ≈ 1.7 TB/day. [source: ajo-franklin-2019-dark-fiber]

## Sources
dascore, xdas, daspy, lightguide, pubdas-spica-2023, ajo-franklin-2019-dark-fiber, shao-2025-ai-das-photonix, quakeflow-das-hf, das4whales-tutorial, intro-to-das-data
