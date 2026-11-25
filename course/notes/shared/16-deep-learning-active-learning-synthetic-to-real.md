# 16 Deep learning on seismic signals: CNNs, hard examples, active learning, synthetic-to-real

## Plain-English idea
**CNNs** learn their own features. A convolutional layer is a bank of small learned filters (note 9) slid across the input. Stack layers with pooling and the network builds up from simple edges to complex patterns. [cs231n-notes] Inputs for V1 can be:
- **raw waveforms (1-D CNN):** ConvNetQuake, PhaseNet [convnetquake-paper] [phasenet-paper]
- **spectrograms (2-D CNN), treated as images:** CRED learns time-frequency patterns [cred-paper]
- **DAS channel × time patches (2-D CNN):** the same idea, with distance as one image axis.

Landmarks to read: ConvNetQuake (detection as classification; ~20× more Oklahoma events than the catalogue) [convnetquake-paper], PhaseNet (P/S picking as segmentation) [phasenet-paper], EQTransformer (CNN + LSTM + attention, trained on STEAD) [eqtransformer-paper]. SeisBench packages many of these models and datasets behind one API. [seisbench-paper]

**Transfer learning:** start from a network trained on something else and fine-tune it. With a small dataset similar to the original, train only a linear classifier on extracted features. With a large dataset, fine-tune everything. [cs231n-transfer-learning] fast.ai teaches this top-down in PyTorch. [fastai-course] [pytorch-basics]

**Hard-example mining:** most training windows are easy noise. Online hard example mining (OHEM) builds each batch from the highest-loss examples, so the model spends its effort on confusing cases. [ohem-paper] For V1, mine hard negatives, such as pumps, traffic and footsteps that look leak-like, and add them to training.

**Active learning:** labels are expensive (a person has to inspect the data or dig up the pipe). Let the model pick which unlabelled examples a person should label next, usually the ones it is **least sure about** (uncertainty sampling) or where an ensemble **disagrees** (query-by-committee). [settles-active-learning]

**Synthetic-to-real:** you can generate unlimited labelled synthetics (wave equation, note 3; Devito, bruges), but real data differs in noise, coupling and wavelet. Mitigations:
- add **real noise** to synthetics at a range of SNRs (note 11)
- randomise wavelet, velocity and geometry (domain randomisation)
- apply the same normalisation to both
- **fine-tune** on a small labelled real set
- use explicit domain-adaptation transforms such as MLReal. [mlreal-paper]

Always **test on real data only**.

## Key equations
- Conv layer output length (1-D, no padding): L_out = floor((L_in − K) / S) + 1 for kernel K and stride S.
- Cross-entropy loss for class probability p of the true class: −log p. Class-weighted loss multiplies by w_class.
- Uncertainty sampling (binary): choose the samples whose predicted probability is closest to 0.5.

## Why V1 cares
Both modules have few real labels and many unlabelled hours. The intended loop is: baseline features (note 14), then a small CNN on spectrograms, then hard-negative mining plus active learning, then synthetic pre-training with real fine-tuning. Evaluate with grouped hold-out sets throughout (note 15).

## Checkable facts
- A 1-D conv with input length 6,000, kernel 11 and stride 1 (no padding) outputs length 5,990. [cs231n-notes]
- With stride 2 and kernel 3 on length 100 (no padding), output length is 49. [cs231n-notes]
- ConvNetQuake detected about 20 times more earthquakes than the Oklahoma Geological Survey catalogue. [convnetquake-paper]
- EQTransformer takes 1-minute, 100 Hz, 3-component windows (6,000 samples per component). [eqtransformer-paper]
- OHEM with other improvements reached 78.9% mAP on PASCAL VOC 2007. [ohem-paper]
- Cross-entropy for a true-class probability of 0.5 is ln 2 ≈ 0.693. [cs229-notes]
- The fast.ai course has 9 lessons of about 90 minutes each. [fastai-course]
- Settles lists three active-learning scenarios: membership query synthesis, stream-based selective sampling and pool-based sampling. [settles-active-learning]

## Sources
cs231n-notes, cs231n-transfer-learning, fastai-course, pytorch-basics, convnetquake-paper, phasenet-paper, eqtransformer-paper, cred-paper, seisbench-paper, ohem-paper, settles-active-learning, mlreal-paper, devito-project, bruges, synthoseis, stead-dataset, instance-dataset, seisbench-datasets, cs229-notes
