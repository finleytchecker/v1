# 14 Feature engineering, classification and class imbalance

## Plain-English idea
Before deep learning, and still often better with little data: turn each window of signal into a **row of numbers (features)** and train a standard classifier (logistic regression, random forest, gradient boosting, SVM). Useful signal features:
- **time domain:** RMS, peak amplitude, kurtosis (spikiness), zero-crossing rate, STA/LTA ratio [obspy-tutorial], duration above threshold
- **frequency domain:** energy in fixed bands, spectral centroid, peak frequency, bandwidth, spectral slope (attenuation, note 5)
- **space/array (DAS):** how many neighbouring channels light up, apparent velocity, coherence between channels
- **seismic attributes (Fluid):** amplitude, impedance contrasts, Vp/Vs, amplitude versus angle (module-specific notes).

Start with a **simple baseline**. Hall's 2016 facies tutorial is a gentle worked example: an SVM on well-log features. [seg-2016-ml-contest]

**Class imbalance:** leaks are rare, and gas sands are rare. A model that always says "no leak" can be 99.9% accurate and useless. Remedies:
- use the right **metrics** (below), not accuracy
- set `class_weight="balanced"` or weight the loss
- **resample**: over-sample the rare class (e.g. SMOTE) or under-sample the common one, with imbalanced-learn, and **only inside training folds** [imbalanced-learn]
- **tune the decision threshold** on validation data instead of using 0.5.

## Key equations
- Precision = TP / (TP + FP): of the alarms, how many were real?
- Recall = TP / (TP + FN): of the real leaks, how many did we catch?
- F1 = 2 · P · R / (P + R)
- Balanced accuracy = mean of per-class recall. Chance level is 1/n_classes. [sklearn-model-evaluation]
- Average precision (area under the precision-recall curve). A random classifier's AP equals the positive-class fraction. [sklearn-model-evaluation]

## Why V1 cares
- **Leak:** a false alarm sends a crew out, and a missed leak costs product and causes damage. Decide the precision/recall trade-off explicitly.
- **Fluid:** classes (water/oil/gas/dry) are unbalanced and overlap in feature space. Report per-class recall and a confusion matrix.

## Checkable facts
- With 990 negatives and 10 positives, always predicting negative scores 99% accuracy but 0 recall. [sklearn-model-evaluation]
- TP = 8, FP = 2, FN = 2 gives precision 0.8, recall 0.8, F1 0.8. [sklearn-model-evaluation]
- In scikit-learn's example y_true = [0,1,0,1], y_pred = [0,1,0,0]: precision 1.0, recall 0.5, F1 ≈ 0.667. [sklearn-model-evaluation]
- If 2% of samples are positive, a random classifier's average precision is about 0.02. [sklearn-model-evaluation]
- Binary balanced accuracy for a constant-majority predictor is 0.5. [sklearn-model-evaluation]
- imbalanced-learn is MIT-licensed and builds on scikit-learn. [imbalanced-learn]
- In the SEG 2016 contest, the top median F1-micro score was about 0.64. [seg-2016-ml-contest]

## Sources
sklearn-model-evaluation, imbalanced-learn, seg-2016-ml-contest, obspy-tutorial, cs229-notes, fastai-course, convnetquake-paper
