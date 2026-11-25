# 04 - Fluid properties: brine, oil and gas (Batzle-Wang)

## Plain English
To model a reservoir you need the density and bulk modulus of each pore fluid **at reservoir pressure and temperature**. These can be very different from surface values. Gas at 300 bar is hundreds of times denser than gas at the surface. Batzle and Wang (1992) fitted empirical equations to lab data so you can compute them from:

- **Brine**: temperature, pressure, salinity (ppm NaCl)
- **Oil**: temperature, pressure, API gravity, gas-oil ratio (GOR, the dissolved gas), gas gravity
- **Gas**: temperature, pressure, gas gravity (relative to air, ~0.56 for methane)

You don't need to memorise the polynomials. Use a library (rockphypy has a BW module, and Equinor's open_petro_elastic also implements it). What matters is understanding the trends.

## Trends to remember
- Higher pressure makes fluids denser and stiffer.
- Higher temperature makes fluids lighter and softer.
- Saltier brine is denser and stiffer.
- Lighter oil (higher API) and more dissolved gas (higher GOR) give a softer, lighter oil. Very light, gassy oil can look seismically almost like gas.
- The gap between gas and brine shrinks with depth, but it is always large.

## API gravity
    API = 141.5 / rho_oil(g/cc at 60F) - 131.5
Water is 10 API. Light oil is 35-45 API, heavy oil below about 20 API.

## Adiabatic vs isothermal
Waves are fast, so there is no time for heat exchange, and the correct modulus is **adiabatic**. Lab PVT reports usually give **isothermal** compressibility. Using that underestimates oil K by about 20% and gas K by about 2 times.

## Typical reservoir values (order of magnitude, ~2-3 km depth)
| Fluid | rho (g/cc) | K (GPa) |
|---|---|---|
| Brine | 1.01-1.10 | 2.4-3.0 |
| Oil (medium) | 0.7-0.85 | 0.6-1.2 |
| Gas | 0.1-0.3 | 0.02-0.15 |

## Checkable facts
- API gravity = 141.5/rho - 131.5, so oil of density 0.85 g/cc has API of about 35. [source: mavko-seismic-velocity-slides]
- The density and bulk modulus of most reservoir fluids increase with pore pressure and decrease with temperature. [source: mavko-seismic-velocity-slides]
- Batzle-Wang bulk moduli are adiabatic, while standard PVT data are isothermal. [source: mavko-seismic-velocity-slides]
- The Batzle-Wang paper is in Geophysics volume 57, issue 11 (1992), pages 1396-1408. [source: batzle-wang-1992]
- One published Gulf of Mexico study used gas density 0.26 g/cc and gas K 0.14 GPa at reservoir conditions. [source: dvorkin-2005-attenuation]
- rockphypy includes a Batzle-Wang (BW) fluid-properties module. [source: rockphypy]

## Sources
batzle-wang-1992, mavko-seismic-velocity-slides, rockphypy, dvorkin-2005-attenuation, crewes-zoeppritz-explorer
