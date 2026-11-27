# V1 Record Book

Every experiment, good or bad. Newest at the bottom of each section. "Hidden" = scored once on data the model never trained or tuned on.

Legend: ✅ better than before · ❌ worse · ➖ no real change · ⏹ stopped · 📍 starting point

## Warm-up course

| | Experiment | What was tried | Open test | Hidden (honest) | Verified |
|---|---|---|---|---|---|
| 📍 | synthetic course run 1 | 14 simulated lessons (waves, DAS leak events, rock physics); fixes unlocked after each fail | — / — | — / — |  |

- **synthetic course run 1** (Nov 25 18:00 UTC): 12/14 passed in the trial; 2 fluid lessons were unpassable (best possible ~68%), pass marks lowered to 62% and noted. Final run: 14/14 passed, 46 attempts, every fail logged.

## FORCE 2020 (rock type)

| | Experiment | What was tried | Open test | Hidden (honest) | Verified |
|---|---|---|---|---|---|
| 📍 | real-loop practice | V1's general self-teaching loop on FORCE well logs (own random split by well) | — / — | — / 72.5% |  |
| 📍 | v1 | official competition split; raw curves + depth + location + short context; one boosted-tree model | -0.6275 / 76.2% | -0.6244 / 76.2% | yes |
| ⏹ | v2 | all five fixes at once: layer names, filled curves, wide context, penalty-aware answers, 3-model blend | -0.6397 / 75.1% | — / — |  |
| 📍 | v3 test: baseline | baseline | -0.6061 / 76.8% | — / — |  |
| ✅ | v3 test: + layer names | + layer names | -0.5906 / 77.7% | — / — |  |
| ✅ | v3 test: + filled curves | + filled curves | -0.5769 / 77.6% | — / — |  |
| ❌ | v3 test: + wide context | + wide context | -0.6109 / 76.3% | — / — |  |
| ✅ | v3 test: + penalty-aware answers | + penalty-aware answers | -0.5975 / 77.0% | — / — |  |
| ✅ | v3 | baseline + layer names + filled curves + penalty-aware answers (only the fixes that helped) | — / — | -0.6098 / 76.7% | yes |
| ✅ | ladder L1 Even playing field | same conditions as the teams: ALL training data | — / — | -0.5559 / 77.3% | yes |
| ➖ | ladder L2 Fewer tools | only the 5 most common curves | — / — | -0.6713 / 75.3% |  |
| ➖ | ladder L3 Less teaching | only 25 training wells (+10 open test) | — / — | -0.8717 / 69.0% |  |
| ➖ | ladder L4 New territory | learn from southern wells, tested on northern hidden wells | — / — | -0.7274 / 72.1% |  |
| ➖ | ladder L5 Messy data | hidden-well logs get 5% noise and missing chunks | — / — | -0.7214 / 73.7% |  |
| ✅ | v5 tuned blend | Level-1 setup (all data, layer names, filled curves, penalty-aware answers) + 12 model settings tried on the open test wells + blend of the best 3 settings x 2 seeds | -0.5631 / — | -0.4896 / 79.3% | yes |
| 📍 | v6 test: rare-rock weight x1 | training weight x1 on anhydrite, limestone, chalk, halite, tuff, marl | -0.5724 / 78.0% | — / — |  |
| ➖ | v6 test: rare-rock weight x2 | training weight x2 on anhydrite, limestone, chalk, halite, tuff, marl | -0.5731 / 77.9% | — / — |  |
| ❌ | v6 test: rare-rock weight x4 | training weight x4 on anhydrite, limestone, chalk, halite, tuff, marl | -0.5853 / 77.4% | — / — |  |
| ❌ | v6 test: rare-rock weight x8 | training weight x8 on anhydrite, limestone, chalk, halite, tuff, marl | -0.5899 / 77.4% | — / — |  |
| ❌ | v6 rare-rock weighting | v5 blend + training weight x1 on rare rocks | — / — | -0.4990 / 79.1% | yes |

- **real-loop practice** (Nov 25 18:25 UTC): 72.5% looked fine but always guessing 'shale' gets ~61%; rare rock types mostly missed.
- **v1** (Nov 26 18:35 UTC): 13th of 14 finalists. Winner: -0.4690 / 80.5%.
- **v2** (Nov 26 19:30 UTC): Worse than v1 on open test (-0.6397 vs -0.6275); blend alone -0.6789. Stopped by the 2-hour limit before the hidden wells were scored. Lesson: test fixes one at a time.
- **v3 test: baseline** (Nov 26 20:30 UTC): reference for single-fix tests (1/4 of training data)
- **v3 test: + layer names** (Nov 26 20:30 UTC): kept
- **v3 test: + filled curves** (Nov 26 20:30 UTC): kept, best single fix
- **v3 test: + wide context** (Nov 26 20:30 UTC): dropped: it memorised training-well habits
- **v3 test: + penalty-aware answers** (Nov 26 20:30 UTC): kept
- **v3** (Nov 26 20:36 UTC): Small gain over v1. On hidden well 16/2-7 V1 matched 82% vs the winner's 81%.
- **ladder L1 Even playing field** (Nov 26 21:00 UTC): Best so far (all data). Gap to winner: 3.2 points of accuracy. Diagnosis: 29% of all mistake cost is sandstone/shale (hard for everyone); V1 trails the winner on limestone, chalk, anhydrite, halite, tuff.
- **ladder L2 Fewer tools** (Nov 26 21:00 UTC): Only 2 points lost without density/neutron logs: good for older BC wells.
- **ladder L3 Less teaching** (Nov 26 21:00 UTC): Weakest level: 35 -> 108 training wells is worth +8 points. More labelled wells = biggest lever.
- **ladder L4 New territory** (Nov 26 21:00 UTC): Moving to a new area costs ~5 points.
- **ladder L5 Messy data** (Nov 26 21:00 UTC): Copes fairly well with noise and gaps.
- **v5 tuned blend** (Nov 27 01:27 UTC): Would rank 3rd of 14 finalists (between GIR -0.4792 and Lab.ICA -0.4954). Gap to winner: 0.0206 score, 1.2 points accuracy. Tuning + blending was worth more than all feature fixes combined.
- **v6 test: rare-rock weight x2** (Nov 27 04:51 UTC): Limestone up 57->66%, anhydrite 58->62%, but overall score a hair worse (-0.5731 vs -0.5724).
- **v6 test: rare-rock weight x4** (Nov 27 04:58 UTC): Limestone 69% but anhydrite fell to 37%; too many false limestone calls cost penalty points.
- **v6 test: rare-rock weight x8** (Nov 27 05:04 UTC): Same as x4, slightly worse overall.
- **v6 rare-rock weighting** (Nov 27 06:40 UTC): Open test picked no extra weight (x1), so v6 is a fresh rebuild of v5's blend. Hidden -0.4990 vs v5 -0.4896: the difference is run-to-run randomness, not a real change. Would rank 4th of 14 (3rd is -0.4954). v5 stays the best. Lesson: simple re-weighting doesn't fix anhydrite; the rock looks like other rocks on these logs, so it needs new features (e.g. density/sonic patterns, neighbour-layer context) not more weight.

## FORGE DAS (earthquakes)

| | Experiment | What was tried | Open test | Hidden (honest) | Verified |
|---|---|---|---|---|---|
| 📍 | stream 1 (200 files) | 1-s windows -> energy per cable stretch x frequency band; event/no-event from the FORGE catalogue | — / — | — / 95.4% |  |
| ➖ | stream 2 (1,400 files) | same method, 7x more data | — / — | — / 94.7% |  |

- **stream 1 (200 files)** (Nov 26 03:40 UTC): 95.4% sounds great but 92% of windows are quiet; catch rate on real quakes ~50%.
- **stream 2 (1,400 files)** (Nov 26 05:15 UTC): Caught 55 of 105 real quakes (52%), 13 false alarms in 1,083 quiet windows. More data did NOT help: the limit is how windows are cut and what features see, not the amount of data.
