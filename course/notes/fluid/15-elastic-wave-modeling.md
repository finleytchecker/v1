# 15 - Elastic wave modelling with finite differences (Devito)

## Plain English
To train or test a Fluid detector you need seismic where **you know the answer**. The cleanest way is to build an earth model (Vp, Vs, rho grids, with a gas sand placed wherever you like) and simulate the waves. **Finite differences (FD)** chop space and time into a grid and step the wave equation forward. Devito lets you write the PDE symbolically in Python and generates fast C code for you.

- **Acoustic** modelling (P only) is cheap but blind to Vs, so it can't produce real AVO.
- **Elastic** modelling (P + S + conversions) gives true AVO and converted waves.
- **Visco-elastic / visco-acoustic** modelling adds Q, to reproduce the attenuation shadows from note 12.

## Velocity-stress elastic equations (2D, isotropic)
    rho * dv/dt = div(tau)
    d(tau)/dt   = lambda * tr(grad v) * I + mu * (grad v + grad v^T)
Here v is particle velocity, tau is the stress tensor, lambda = rho*(Vp^2 - 2Vs^2) and mu = rho*Vs^2. These are solved on a **staggered grid**: velocities and stresses live at half-cell offsets.

Fluids are handled automatically: put mu = 0 (Vs = 0) in a water layer and S-waves simply can't enter it.

## Rules of thumb for stable, accurate runs
- **Stability (CFL)**: the time step must satisfy dt <= C * dx / Vmax, with C below 1 (about 0.5-0.7 depending on scheme and dimension).
- **Dispersion**: the grid needs enough points per *minimum* wavelength, lambda_min = Vs_min / f_max. Slow shear velocities in soft sediments set the grid size, so elastic is far more expensive than acoustic.
- **Boundaries**: absorbing layers (damping/PML) stop fake reflections from the model edges.

## Devito notebooks to work through (in order)
1. `01_modelling.ipynb`: acoustic forward modelling, sources and receivers
2. `05_staggered_acoustic.ipynb`: the staggered-grid idea
3. `06_elastic.ipynb` and `06_elastic_varying_parameters.ipynb`: the elastic equation above
4. `07.1_dispersion_relation.ipynb`: why grid spacing matters
5. `09_viscoelastic.ipynb` and `11_viscoacoustic.ipynb`: adding Q

Free models to load: AGL Elastic Marmousi (Marmousi2, with Vp, Vs and rho, which includes hydrocarbon sands) and the SEAM Phase I elastic model.

## Checkable facts
- Lame's first parameter is lambda = rho(Vp^2 - 2Vs^2) and the shear modulus is mu = rho*Vs^2. [source: wikipedia-gassmann]
- For Vs_min = 500 m/s and f_max = 50 Hz, the minimum shear wavelength is 10 m. [source: devito-tutorials]
- Devito's tutorial set includes 06_elastic, 09_viscoelastic and 11_viscoacoustic notebooks. [source: devito-tutorials]
- Devito is MIT-licensed and generates optimised finite-difference code from symbolic equations. [source: devito-project]
- The AGL Elastic Marmousi model provides density, P-wave and S-wave velocity models plus processed data sets. [source: agl-elastic-marmousi]
- The SEAM Phase I elastic earth model uses a 20 m x 20 m x 10 m grid. [source: seam-phase1-netl]

## Sources
devito-tutorials, devito-project, agl-elastic-marmousi, seam-phase1-netl, mit-12-510-seismology, wikipedia-gassmann
