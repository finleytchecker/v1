# FORCE 2020 Lithology Competition: leaderboard, well splits, scoring

Primary source: the organisers' GitHub repo, still at its original name and location:
https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition (cloned 2026-11-26, commit `c8d01ee92c1c8e1ecba36f96cca6ea7b689338a1`).
Citation from the repo README: Bormann P., Aursand P., Dilib F., Dischington P., Manral S. 2020. *FORCE Machine Learning Competition.* Data DOI: https://doi.org/10.5281/zenodo.4351156

## 1. Confirmed facts

### 1.1 Participation
From the [repo README](https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition/blob/master/readme.md) and the [technical retrospective PDF](https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition/blob/master/technical_retrospective_force%202020%20lithofacies%20competition.pdf) (a mirror is on sodir.no: https://sodir.no/globalassets/2-force/2020/seminars/contest-machine-learning/technical_retrospective_force-2020-lithofacies-competition.pdf):
- **329 teams signed up.**
- **148 teams submitted predictions** on the open test set, which put them on the open leaderboard.
- The top 30 teams on the leaderboard were invited to submit pre-trained models for scoring on the hidden wells.
- **13 teams** submitted code the organisers could run easily. These 13 make up the whole final ranking.

### 1.2 Final leaderboard on the 10 hidden wells
This is the official table from the [repo README](https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition/blob/master/readme.md). Scores are the penalty-matrix score: negative, and closer to 0 is better.

| Final rank | Team | Final (hidden) score | Open-leaderboard score | Open-leaderboard rank |
|---|---|---|---|---|
| 1 | Olawale Ibrahim | **-0.4690** | -0.5118 | 24 |
| 2 | GIR Team | -0.4792 | -0.5037 | 11 |
| 3 | Lab.ICA-Team / Smith A. | -0.4954 | -0.4943 | 6 |
| 4 | H3G (Zhang, Brandsen, Barrere, Formentin) | -0.5045 | -0.509 | 17 |
| 5 | ISPL Team | -0.5084 | -0.4885 | 2 |
| 6 | Jiampiers C. | -0.5087 | -0.5014 | 9 |
| 7 | José Bermúdez | -0.5091 | -0.5052 | 14 |
| 8 | Bohdan Pavlyshenko | -0.5171 | -0.5112 | 22 |
| 9 | Jeremy Zhao | -0.5173 | -0.5264 | 31 |
| 10 | Campbell Hutcheson | -0.5221 | -0.505 | 13 |
| 11 | David P. | -0.5256 | -0.4775 | 1 |
| 12 | SoftServe Team | -0.5263 | -0.4936 | 3 |
| 13 | Dapo Awolayo | -0.9441 | -0.5121 | 25 |

- The organisers do not state a median. Computed from the table: the **median of the 13 final scores is -0.5091** (José Bermúdez, rank 7). Ranks 1 to 12 all fall between -0.469 and -0.526.
- The README gives no accuracy figures. The retrospective mentions a figure of "the top six teams' accuracy on the blind test data", but it is an image and the text layer has no numbers.

### 1.3 Recomputed scores and accuracy (from the repo's per-team hidden-well predictions)
`lithology_competition/final_scoring/<team>/<well>.csv` holds each finalist's predictions for every sample of the 10 hidden wells: 122,397 rows, with columns `WELL, DEPTH_MD, FORCE_2020_LITHOFACIES_LITHOLOGY, prediction, correct`, labels as class indices 0 to 11. I checked that the true labels in these files match `data/hidden_test.csv`. Both columns below are my own calculation (score = -mean(A[true,pred]); accuracy = mean(true==pred)):

| Team folder | Recomputed score | Recomputed accuracy |
|---|---|---|
| Olawale | -0.4698 | 0.8053 |
| GIR | -0.4792 | 0.8034 |
| ICA | -0.4967 | 0.8038 |
| H3G | -0.5045 | 0.7962 |
| ISPL | -0.5084 | 0.7848 |
| JiampiersC | -0.5089 | 0.7979 |
| JoseB | -0.5091 | 0.8026 |
| JeremyZhao | -0.5156 | 0.7972 |
| BohdanP | -0.5171 | 0.7844 |
| CampbellH | -0.5221 | 0.7867 |
| DavidP | -0.5256 | 0.7858 |
| Softserve | -0.5263 | 0.7855 |
| DapoA | -0.9443 | 0.6853 |

Eight of the 13 recomputed scores match the README to 4 decimals. The rest differ slightly: Olawale (-0.4698 vs -0.4690), ICA (-0.4967 vs -0.4954), JeremyZhao (-0.5156 vs -0.5173), JiampiersC (-0.5089 vs -0.5087) and DapoA (-0.9443 vs -0.9441). The stored CSVs may be a slightly different run from the one scored. The README values are the official ones. **Top-team accuracy on the hidden wells is about 80%.**

### 1.4 Well splits (read directly from the repo data files)
- **Training: 98 wells**, 1,170,511 samples, from `lithology_competition/data/train.zip` → `train.csv`, column `WELL`. The full list is in `train_wells.txt`:
  15/9-13, 15/9-15, 15/9-17, 16/1-2, 16/1-6 A, 16/10-1, 16/10-2, 16/10-3, 16/10-5, 16/11-1 ST3, 16/2-11 A, 16/2-16, 16/2-6, 16/4-1, 16/5-3, 16/7-4, 16/7-5, 16/8-1, 17/11-1, 25/11-15, 25/11-19 S, 25/11-5, 25/2-13 T4, 25/2-14, 25/2-7, 25/3-1, 25/4-5, 25/5-1, 25/5-4, 25/6-1, 25/6-2, 25/6-3, 25/7-2, 25/8-5 S, 25/8-7, 25/9-1, 26/4-1, 29/6-1, 30/3-3, 30/3-5 S, 30/6-5, 31/2-1, 31/2-19 S, 31/2-7, 31/2-8, 31/2-9, 31/3-1, 31/3-2, 31/3-3, 31/3-4, 31/4-10, 31/4-5, 31/5-4 S, 31/6-5, 31/6-8, 32/2-1, 33/5-2, 33/6-3 S, 33/9-1, 33/9-17, 34/10-19, 34/10-21, 34/10-33, 34/10-35, 34/11-1, 34/11-2 S, 34/12-1, 34/2-4, 34/3-1 A, 34/4-10 R, 34/5-1 A, 34/5-1 S, 34/7-13, 34/7-20, 34/7-21, 34/8-1, 34/8-3, 34/8-7 R, 35/11-1, 35/11-10, 35/11-11, 35/11-12, 35/11-13, 35/11-15 S, 35/11-6, 35/11-7, 35/12-1, 35/3-7 S, 35/4-1, 35/8-4, 35/8-6 S, 35/9-10 S, 35/9-2, 35/9-5, 35/9-6 S, 36/7-3, 7/1-1, 7/1-2 S
- **Open test (leaderboard) wells: 10**, 136,786 samples, from `data/leaderboard_test_features.csv` / `leaderboard_test_target.csv`. Saved as `open_test_wells.txt`:
  15/9-14, 25/10-10, 25/11-24, 25/5-3, 29/3-1, 34/10-16 R, 34/3-3 A, 34/6-1 S, 35/6-2 S, 35/9-8
- **Hidden / blind test wells: 10**, 122,397 samples, from `data/hidden_test.csv`, which includes the true labels. The `final_scoring/` file names confirm the same list. Saved as `hidden_test_wells.txt`:
  15/9-23, 16/2-7, 16/7-6, 17/4-1, 25/10-9, 31/2-10, 31/2-21 S, 34/3-2 S, 35/11-5, 35/9-7
- That gives 98 + 10 + 10 = 118 wells, matching the retrospective's "118 curated and consistently interpreted well logs". The repo's `las_files_Lithostrat_data/` folder has 119 entries, which I did not reconcile.
- Hidden-well label counts: 65000 Shale 71,827; 30000 Sandstone 14,045; 65030 Sst/Shale 12,283; 70000 Limestone 8,374; 88000 Halite 6,498; 80000 Marl 4,396; 70032 Chalk 2,905; 99000 Tuff 941; 86000 Anhydrite 597; 74000 Dolomite 287; 90000 Coal 244; 93000 Basement 0. None of the hidden wells has basement.

### 1.5 Scoring function
Sources: `lithology_competition/data/test_code.py`, `starter_notebook.ipynb` and `penalty_matrix.npy`, all in the repo. Copies of `penalty_matrix.npy` and `test_code.py` are in this folder.

Class order (index → code), from `lithology_numbers` in test_code.py and `lithology_keys` in the starter notebook. **This confirms the order you gave:**
0 30000 Sandstone · 1 65030 Sandstone/Shale · 2 65000 Shale · 3 80000 Marl · 4 74000 Dolomite · 5 70000 Limestone · 6 70032 Chalk · 7 88000 Halite · 8 86000 Anhydrite · 9 99000 Tuff · 10 90000 Coal · 11 93000 Basement

Formula (test_code.py): `S -= A[y_true[i], y_pred[i]]` summed over all samples, then `S / N`. That is, **score = -(1/N) Σ A[true_i, pred_i]**. The notebook writes it as `S = -1/N Σ A_{ŷ_i y_i}` and says rows = guessed, columns = true. The matrix is **symmetric** (A == A.T, checked), so the orientation does not matter.

Penalty matrix A (12x12 float64, `penalty_matrix.npy`). It is identical to the Zenodo spreadsheet `scoring_matrix.xlsx` already in this folder, which labels rows "reality" and columns "interpreted"; checked cell by cell:
```
        Sst   SsSh  Sh    Marl  Dol   Lst   Chk   Hal   Anh   Tuff  Coal  Bsmt
Sst    0     2     3.5   3     3.75  3.5   3.5   4     4     2.5   3.875 3.25
SsSh   2     0     2.375 2.75  4     3.75  3.75  3.875 4     3     3.75  3
Sh     3.5   2.375 0     2     3.5   3.5   3.75  4     4     2.75  3.25  3
Marl   3     2.75  2     0     2.5   2     2.25  4     4     3.375 3.75  3.25
Dol    3.75  4     3.5   2.5   0     2.625 2.875 3.75  3.25  3     4     3.625
Lst    3.5   3.75  3.5   2     2.625 0     1.375 4     3.75  3.5   4     3.625
Chk    3.5   3.75  3.75  2.25  2.875 1.375 0     4     3.75  3.125 4     3.75
Hal    4     3.875 4     4     3.75  4     4     0     2.75  3.75  3.75  4
Anh    4     4     4     4     3.25  3.75  3.75  2.75  0     4     4     3.875
Tuff   2.5   3     2.75  3.375 3     3.5   3.125 3.75  4     0     2.5   3.25
Coal   3.875 3.75  3.25  3.75  4     4     4     3.75  4     2.5   0     4
Bsmt   3.25  3     3     3.25  3.625 3.625 3.75  4     3.875 3.25  4     0
```
Note: the hidden test CSV uses `sep=';'`.

## 2. Files saved in this folder
- `penalty_matrix.npy`: copied from the repo's `lithology_competition/data/`
- `test_code.py`: the official scoring snippet from the repo. It has no `import numpy`, as in the original.
- `technical_retrospective.pdf`: the organisers' technical retrospective
- `train_wells.txt` (98), `open_test_wells.txt` (10), `hidden_test_wells.txt` (10)
- These were already present and I left them alone: `run.py`, `scoring_matrix.xlsx`, `__init__.py`
- The full repo clone, which includes `hidden_test.csv` with labels and the per-team `final_scoring/` predictions, is at `/home/user/bolgebrygg/force-2020-machine-learning-competition/`

## 3. Uncertain / not confirmed
- **Official accuracy numbers** for the finalists were not found as text, only as an image in the retrospective. The ~80% figures above are my recomputation from the stored predictions.
- Small mismatches (up to 0.0017) between the recomputed and official scores for 5 of the 13 teams. The cause is unknown.
- The sodir.no results page (https://www.sodir.no/en/force/Previous-events/2020/results-of-the-FORCE-2020-lithology-competition/) returned 403, so I could not read it.
- I did not find a separate peer-reviewed competition paper in Petrophysics or The Leading Edge. The README citation, Bormann et al. 2020, points to the GitHub repo itself.
- The open-leaderboard scores of the other ~135 teams are not in the repo, so there is no median for all 148 teams.
- `run.py` in this folder says "~330 teams". That is the sign-up count (329). Only 148 were on the leaderboard and 13 were in the final hidden-well ranking.
