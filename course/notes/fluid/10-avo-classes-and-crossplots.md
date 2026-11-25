# 10 - AVO classes and intercept-gradient crossplots

## Plain English
Rutherford and Williams (1989) sorted gas-sand responses into classes by the sand's impedance relative to the shale above. Castagna and co-workers later added Class IV. The class tells you what a gas sand will *look like* on stacks and gathers, i.e. what to hunt for.

| Class | Sand vs shale impedance | Intercept A | Gradient B | What you see |
|---|---|---|---|---|
| I | sand harder | positive | negative | positive peak that **dims** with offset, may reverse polarity at far offsets; "dim spot" on full stack |
| II (IIp) | about equal | near zero (II: small +, IIp: phase reversal) | negative | weak near, **strong far**; polarity reversal common |
| III | sand much softer | negative | negative | strong trough that **brightens** with offset; classic bright spot |
| IV | sand much softer, but overlain by a very hard/fast unit (low gradient) | negative | positive (or ~0) | bright trough that **dims** with offset |

For the Class III gas sand in note 09, A = -0.09 and B = -0.25. The brine-sand case (A of about 0, B = -0.17) sits near the background trend.

## Intercept-gradient crossplot
Plot B (y) against A (x) for every sample of a horizon or window. Brine sands and shales fall along a **background trend**, a line through the origin with negative slope that depends on Vp/Vs. Hydrocarbon sands plot **off** that trend. Tops of gas sands fall in the lower-left quadrant (A<0, B<0), and bases in the upper-right.

Simple fluid attributes built from A and B:
- A*B (product): positive for Class III top-and-base pairs
- "Fluid factor" / scaled Poisson reflectivity ~ A + B
- Projections (chi-angle / EEI) that rotate the crossplot to isolate fluid

## Caveats
- A Class I gas sand can look like a wet sand on a full stack.
- Wet sands with low Vp/Vs, or coals, can mimic gas.
- Processing (NMO stretch, amplitude balancing) and tuning distort the gradient.

## Checkable facts
- Rutherford and Williams (1989) defined AVO classes 1, 2 and 3 for gas sands. [source: rutherford-williams-1989]
- For classes I-III the AVO gradient is negative, while Class IV has a positive or near-zero gradient. [source: rutherford-williams-1989]
- Class 4 sands are low-impedance reservoirs whose amplitude magnitude decreases with offset. [source: seg-dict-avo]
- The intercept is the normal-incidence reflection coefficient, and the gradient is the slope of amplitude against sin^2(theta). [source: wikipedia-avo]
- On an AVO crossplot, intercept P is plotted against gradient G for every time sample. [source: wikipedia-avo]
- An AVO anomaly most often shows as amplitude rising with offset, where a soft reservoir lies under shale. [source: wikipedia-avo]
- A gas sand with A = -0.09 and B = -0.25 is Class III. [source: seg-wiki-avo-attributes]

## Sources
rutherford-williams-1989, seg-dict-avo, seg-wiki-avo-attributes, wikipedia-avo, aadm-geophysical-notes, aadm-avo-explorer, seg-tutorials-2014
