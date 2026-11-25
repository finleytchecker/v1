# 16 - Machine learning for fluid and lithology prediction

## Plain English
ML in this module has two jobs:
1. **Logs to labels**: predict lithology or fluid at each depth from well logs. Labels are plentiful (FORCE 2020, SEG 2016), so this is the easiest place to start.
2. **Seismic to fluid**: predict gas/oil/brine/shale away from wells from seismic attributes (intercept, gradient, Ip, Vp/Vs and frequency attributes) or raw gathers. Labels are scarce, so you **augment with physics**: take real logs, run Gassmann to make gas, oil and brine versions (note 06), forward model the AVO (note 09) or full waveforms (note 15), and train on those synthetic examples.

## Recommended progression for V1
1. SEG 2016 contest: an SVM or gradient-boosting baseline on 9 facies (small, fast).
2. FORCE 2020: lithology from about 118 wells. Learn about well-wise splits, missing curves and the cost-matrix score.
3. Volve logs: predict missing sonic or shear sonic (the regression version).
4. Physics-augmented classifier: Gassmann-substituted log blocks, then Shuey A/B, then a classifier for {brine, oil, gas} x {sand, shale}.
5. Apply it to Poseidon angle stacks (seismic) and check against NOPIMS wells.

## Pitfalls
- **Leakage**: neighbouring depth samples are almost identical. Always split by *well*, never by random rows.
- **Class imbalance**: gas is rare, so use class weights and look at per-class F1, not accuracy.
- **Fizz gas**: physics says low-saturation gas looks like commercial gas on Vp. A model can't learn a difference the inputs don't contain, so add density or attenuation features.
- **Domain shift**: synthetic data is too clean. Add noise, wavelet variation and tuning.

## Checkable facts
- The SEG 2016 training data is 9 wells (4149 samples) with 7 predictors and 9 core-based facies, from the Panoma/Council Grove gas field in Kansas. [source: seg-2016-ml-contest]
- The SEG 2016 contest data is not openly licensed and is for contest use only. [source: seg-2016-ml-contest]
- The FORCE 2020 dataset has 118 wells, is licensed CC BY 4.0 and is about 170 MB. [source: force-2020-zenodo]
- 329 teams signed up for FORCE 2020 and 148 submitted predictions on the open test set. [source: force-2020-github]
- In the SEG 2016 tutorial, dolomite (facies 7) is the rarest class, with 81 training examples. [source: seg-2016-ml-contest]
- A physics-guided 4D network computed AVO gradients explicitly because gas-saturation changes are rare in training data and risk being treated as outliers. [source: arxiv-1904-02254-physics-dl-4d]
- On Volve, gradient boosting predicted missing P-sonic with an average R^2 of about 0.95. [source: volve-ml-repo]
- The F3 facies benchmark was built from 3D seismic plus 26 well logs. [source: alaudah-2019-f3-benchmark]

## Sources
seg-2016-ml-contest, hall-2016-facies-ml, force-2020-zenodo, force-2020-github, volve-ml-repo, alaudah-2019-f3-benchmark, f3-facies-benchmark, arxiv-1904-02254-physics-dl-4d, arxiv-2307-07969-satinv, arxiv-2410-21960-poseidon-ml, frontiers-2026-obn-fluid-ml, andymcd-petrophysics-python
