# 14 - Seismic inversion: from wiggles back to rock properties

## Plain English
Forward modelling (notes 08-09) goes from rock properties to seismic. **Inversion** goes backwards: from the recorded traces, estimate the impedance (and, with angle data, Vp/Vs and density) of each layer. It turns a boundary property (reflectivity) into a layer property (impedance). That layer property is what you can classify as gas, oil, brine or shale.

Types, from simplest:
1. **Post-stack acoustic impedance inversion**: one stack, one wavelet, solve for Ip. Methods include model-based and constrained sparse-spike. Ip alone mixes up porosity and fluid.
2. **Pre-stack (simultaneous / AVO) inversion**: several angle stacks (e.g. near, mid, far, as in Poseidon) jointly give Ip, Is (or Vp/Vs) and sometimes density. This is the main input to fluid classification.
3. **Geostatistical / Bayesian inversion**: many realisations that honour wells and seismic, giving probabilities ("P(gas)").
4. **Rock-physics / petrophysical inversion**: go one step further, to porosity, Vsh and Sw directly, often with ML (arXiv 2307.07969).

## The maths in one line
    d = W * G * D * m        (PyLops notation)
- m holds log(Vp), log(Vs) and log(rho) at each time sample.
- D takes the time derivative, which gives reflectivity.
- G is the AVO operator (Aki-Richards or Fatti weights per angle).
- W convolves with the wavelet.

Solve with least squares plus regularisation. You need a **low-frequency background model** (from wells) because seismic lacks frequencies below roughly 5-10 Hz. Without it you only recover relative changes.

## Practical gotchas
- Density is the hardest parameter to recover. It needs far angles (>35-40 degrees) and good data, yet it is the best discriminator of fizz vs commercial gas.
- The wavelet must be estimated from a well tie.
- Non-uniqueness: many models fit the data, and regularisation picks one.

## Checkable facts
- Simultaneous pre-stack inversion solves for P-impedance, S-impedance and density using several angle stacks, each with its own wavelet. [source: wikipedia-seismic-inversion]
- Constrained sparse-spike inversion assumes a limited number of large reflection coefficients. [source: wikipedia-seismic-inversion]
- The PyLops pre-stack tutorial models data as d = W G D m, with m the logarithms of Vp, Vs and density. [source: pylops-prestack]
- The PyLops tutorial angle gathers span 0-40 degrees with 21 angles, and the synthetic examples fix Vs/Vp = 0.5. [source: pylops-prestack]
- Inverting without a background model (m0 = None) recovers only relative changes in elastic properties. [source: pylops-prestack]
- Geostatistical inversion quantifies uncertainty through multiple realisations. [source: wikipedia-seismic-inversion]
- The Poseidon open dataset provides near, mid, far and full angle stacks, which is enough for a simultaneous inversion. [source: poseidon-tgs]

## Sources
wikipedia-seismic-inversion, pylops-prestack, pylops-poststack, poseidon-tgs, arxiv-2307-07969-satinv, frontiers-2026-obn-fluid-ml
