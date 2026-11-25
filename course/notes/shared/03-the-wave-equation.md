# 03 The wave equation

## Plain-English idea
The wave equation is the rule every small piece of material obeys. Its acceleration is proportional to how sharply the displacement around it is curved in space. Where the shape bends a lot, the material is pushed hard back toward flat, and that push makes the disturbance travel. The constant in front is the velocity squared.

It is worth learning because:

1. It explains why v = fλ holds for any frequency in a simple (non-dispersive) material.
2. Solving it numerically (finite differences) is how you **make synthetic training data**. Devito does this for seismic wavefields, and the same idea can model vibration along a pipe or cable.

## Key equations
- 1-D: ∂²u/∂t² = v² ∂²u/∂x²
- 3-D acoustic (pressure p): ∂²p/∂t² = v² ∇²p
- Any shape f(x − vt) solves the 1-D equation. It moves right at speed v without changing shape.
- Finite-difference stability (CFL condition, 1-D explicit scheme): v Δt / Δx ≤ 1.
- Rule of thumb against numerical dispersion: use at least ~5–10 grid points per shortest wavelength (depends on the scheme's order).

## Typical numbers
- With a 2 m grid, v = 3,000 m/s and the CFL limit 1, the time step must be Δt ≤ 2/3000 ≈ 0.67 ms.
- At 10 points per wavelength, a 2 m grid resolves wavelengths down to 20 m. At 3,000 m/s that is 150 Hz.

## Why V1 cares
- Synthetic-to-real transfer (note 16) starts with forward modelling of the wave equation.
- The equation shows that velocity contrasts (fluid changes) alter how waves travel and reflect.

## Checkable facts
- In the 1-D wave equation, the coefficient of ∂²u/∂x² is v². [coursera-computers-waves-simulations]
- For v = 3,000 m/s and Δx = 2 m, the 1-D CFL limit (Courant number 1) gives Δt_max ≈ 0.000667 s. [coursera-computers-waves-simulations]
- If velocity doubles on a fixed grid, the maximum stable time step halves. [coursera-computers-waves-simulations]
- Devito generates finite-difference stencil code from symbolic equations and is licensed MIT. [devito-github]
- At 10 points per wavelength, a 5 m grid supports wavelengths ≥ 50 m. At 2,000 m/s that is ≤ 40 Hz. [devito-project]

## Sources
coursera-computers-waves-simulations, devito-project, devito-github, seg-wiki-wave-equation, mit-12-510, seismo-live
