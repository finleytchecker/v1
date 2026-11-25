# 13 Arrays, apparent velocity and the f-k transform

## Plain-English idea
With many sensors along a line, such as a seismic spread or the thousands of channels along a DAS fibre, you can study waves in **space and time together**. Arrange the data as an image: channels (distance x) on one axis, time on the other. A wave crossing the array shows up as a sloping line. The slope gives its **apparent velocity**, and its direction gives which way it travels.

A **2-D Fourier transform** of that (time, distance) image gives the **f-k domain** (frequency, wavenumber). Every straight line in x-t becomes a straight line through the origin in f-k, with slope equal to velocity: v = f / k. That lets you:
- **filter by velocity** (f-k or "fan" filtering). For example, remove slow surface waves or traffic while keeping fast waves, or keep only energy in a given velocity range.
- **separate directions**: waves moving toward +x and toward −x land in different quadrants.
- **beamform**: for a 2-D array, scan slowness and back-azimuth to find where energy comes from (ObsPy FK example). [obspy-fk]

**Spatial aliasing:** if channels are too far apart for the wavelength (Δx > λ/2), steep events wrap around in k, just like time aliasing (note 6).

## Key equations
- Apparent velocity: v_app = Δx / Δt. Slowness s = 1/v_app.
- f-k: v = f / k (k in cycles per metre).
- Spatial Nyquist: k_N = 1 / (2 Δx).
- The highest unaliased frequency for velocity v and spacing Δx: f_max = v / (2 Δx).

## Typical numbers
- ObsPy FK example: slowness grid from −3 to 3 s/km in steps of 0.03, 1 s windows, 1–8 Hz band. [obspy-fk]

## Why V1 cares
- **Leak:** a leak is a **stationary** source. Energy spreads outward in both directions from one point and persists in time. A vehicle or person is a **moving** source. f-k patterns and channel-to-channel correlation help tell them apart and help localise the leak. DAS-specific processing is covered elsewhere.
- **Fluid:** surface seismic gathers are routinely f-k filtered to suppress ground roll before amplitude analysis.

## Checkable facts
- A wave crossing 100 m of channels in 0.05 s has an apparent velocity of 2,000 m/s. [obspy-fk]
- A slowness of 0.5 s/km corresponds to 2 km/s. [obspy-fk]
- With 1 m channel spacing, the spatial Nyquist is 0.5 cycles/m. [mit-6-341]
- With 10 m spacing and v = 1,500 m/s, frequencies above 75 Hz are spatially aliased. [madagascar]
- In the f-k domain, a 10 Hz event with k = 0.005 cycles/m has velocity 2,000 m/s. [pylops]
- The ObsPy FK tutorial uses a slowness grid from −3.0 to 3.0 s/km. [obspy-fk]

## Sources
obspy-fk, obspy-tutorial, mit-6-341, madagascar, pylops, claerbout-books
