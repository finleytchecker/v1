# 01 What is a wave?

## Plain-English idea
A wave is a disturbance that travels through a material while the material itself mostly stays put. Shake one end of a rope and a bump runs along it, but each bit of rope only moves up and down. Sound in air, ripples on water, seismic waves in rock and the vibrations a fibre-optic cable picks up are all waves.

Three numbers describe a simple repeating (sinusoidal) wave:

- **Frequency f** is how many cycles pass a fixed point each second. Unit: hertz (Hz).
- **Period T** is how long one cycle takes. T = 1/f.
- **Wavelength λ** is the distance between two crests.
- **Velocity v** is how fast the disturbance moves.

They are tied together by one equation: v = f λ. One full wavelength passes you in one period.

The **amplitude** is the size of the wiggle (displacement, velocity, strain or pressure, depending on the sensor). The **phase** says where in its cycle the wave is at a given time.

## Key equations
- v = f λ
- T = 1 / f
- Angular frequency ω = 2π f. Wavenumber k = 2π / λ, so v = ω / k.
- A travelling sinusoid: u(x, t) = A cos(k x − ω t + φ)

## Typical numbers
- Sound in air: about 340 m/s. Sound in water: about 1,500 m/s.
- P waves in crustal rock: about 6 km/s. S waves: about 4 km/s. [iris-seismic-wave-motions]
- Exploration seismic data usually contains frequencies of roughly 5–100 Hz. Earthquake records sampled at 100 Hz can hold content up to 50 Hz. [stead-dataset]

## Why V1 cares
- **Leak:** a leak produces vibration at particular frequencies, and the cable records strain along its length. Because v = fλ links time behaviour to space behaviour, a leak signal has a shape in both time and distance.
- **Fluid:** wavelength sets the vertical resolution of seismic data. Thin layers that are much smaller than λ blur together.

## Checkable facts
- A 50 Hz wave travelling at 2,000 m/s has a wavelength of 40 m (λ = v/f). [think-dsp]
- A 10 Hz wave has a period of 0.1 s. [think-dsp]
- A P wave at 6 km/s with frequency 20 Hz has a wavelength of 300 m. [iris-seismic-wave-motions]
- A sound wave in water at 1,500 m/s and 1,500 Hz has a wavelength of 1 m. [dspguide]
- Angular frequency for 5 Hz is 2π × 5 ≈ 31.4 rad/s. [mit-6-003]
- If wavelength doubles at a fixed velocity, frequency halves. [think-dsp]

## Sources
think-dsp, dspguide, mit-6-003, iris-seismic-wave-motions, stead-dataset
