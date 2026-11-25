# 15 Honest evaluation: train/validation/test, cross-validation and data leakage

## Plain-English idea
A model's score only means something if it was measured on data the model, and you, never learned from. Split the data into three parts:
- **training set:** fit the model
- **validation set** (or cross-validation folds): choose features, hyperparameters and thresholds
- **test / hold-out set:** touch it once, at the end. EQTransformer used 85% / 5% / 10% for train / validation / test on STEAD. [eqtransformer-paper]

**Data leakage** is when information unavailable at prediction time sneaks into training. The result is scores that look great and then collapse on new data. [sklearn-common-pitfalls] Common forms in geophysics:
1. **Preprocessing fitted on all data.** Scalers, PCA or feature selection fitted before the split. Fix: put everything in a scikit-learn `Pipeline`. In scikit-learn's demonstration on pure-noise data, selecting features before splitting gave ~0.76 accuracy instead of the honest ~0.5. [sklearn-common-pitfalls]
2. **Neighbouring samples in both train and test.** Overlapping windows from the same recording, channels a few metres apart on the same event, or depth samples from the same well are near-copies. Fix: split by **group** (event, day, cable segment, well, survey) with `GroupKFold` / `StratifiedGroupKFold`. [sklearn-cross-validation]
3. **Training on the future.** For monitoring over time, use `TimeSeriesSplit` or a strict date cut-off so the test period comes after the training period. [sklearn-cross-validation]
4. **Label or acquisition shortcuts.** If all leak examples come from one test site or one sensor setting, the model can learn the site, not the leak. Check by holding out whole sites.

**Cross-validation** rotates which fold is held out and averages the scores. Use `StratifiedKFold` to keep class ratios in each fold when classes are imbalanced. [sklearn-cross-validation]

## Key equations / rules
- k-fold CV: each sample is tested exactly once. Each model trains on (k−1)/k of the data.
- Report the mean ± standard deviation across folds, not just the best fold.

## Why V1 cares
- **Leak:** split by **event and location**, never by random window. Otherwise two halves of the same leak recording end up on both sides of the split.
- **Fluid:** split by **well or area**. The SEG 2016 contest scored on held-out wells for this reason. [seg-2016-ml-contest]

## Checkable facts
- With 5-fold CV, each model is trained on 80% of the data and tested on 20%. [sklearn-cross-validation]
- In scikit-learn's leakage example (200 samples, 10,000 random features, random labels), selecting features on all data gave ~0.76 accuracy, versus ~0.5 when done correctly. [sklearn-common-pitfalls]
- `GroupKFold` guarantees the same group never appears in both the training and test sets. [sklearn-cross-validation]
- In `TimeSeriesSplit` with 6 samples and 3 splits, the last split trains on samples 0–4 and tests on sample 5. [sklearn-cross-validation]
- EQTransformer split STEAD randomly into 85% training, 5% validation and 10% test. [eqtransformer-paper]
- In scikit-learn's 45:5 imbalanced example with 3 folds, plain `KFold` produced a test fold with no class-1 samples, while `StratifiedKFold` kept 1–2 per fold. [sklearn-cross-validation]

## Sources
sklearn-common-pitfalls, sklearn-cross-validation, eqtransformer-paper, seg-2016-ml-contest, cs231n-notes, cs229-notes
