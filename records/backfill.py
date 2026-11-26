"""One-time backfill of every experiment run before the record book existed (numbers copied from the run logs
in runs/*.txt and the result files in benchmarks/force2020/). Safe to re-run: entries are replaced, not duplicated."""
import datetime as dt
import json
from pathlib import Path

from engine.records import record

PC = json.loads(Path("/tmp/claude-0/perclass.json").read_text()) if Path("/tmp/claude-0/perclass.json").exists() else {}
F, G, W = "FORCE 2020 (rock type)", "FORGE DAS (earthquakes)", "Warm-up course"


def t(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp()


record(W, "synthetic course run 1", created_at=t("2026-11-25T18:00"),
       tried="14 simulated lessons (waves, DAS leak events, rock physics); fixes unlocked after each fail",
       why="learn the basics on unlimited free practice data before real data",
       data="physics simulator, 300 practice + 300 quiz examples per try",
       outcome="baseline", hidden_accuracy=None,
       lesson="12/14 passed in the trial; 2 fluid lessons were unpassable (best possible ~68%), pass marks lowered "
              "to 62% and noted. Final run: 14/14 passed, 46 attempts, every fail logged.")

record(F, "real-loop practice", created_at=t("2026-11-25T18:25"),
       tried="V1's general self-teaching loop on FORCE well logs (own random split by well)",
       why="first contact with real data", data="118 wells, every 8th depth sample; 18 wells locked away",
       hidden_accuracy=0.725, outcome="baseline",
       lesson="72.5% looked fine but always guessing 'shale' gets ~61%; rare rock types mostly missed.")

record(F, "v1", created_at=t("2026-11-26T18:35"),
       tried="official competition split; raw curves + depth + location + short context; one boosted-tree model",
       why="first fair head-to-head with the 2020 competition teams",
       data="98 training wells (every 2nd sample), tuned on 10 open test wells, scored once on 10 hidden wells",
       open_score=-0.6275, open_accuracy=0.762, hidden_score=-0.6244, hidden_accuracy=0.762,
       verified="re-scored with the organizers' own code and files: -0.6229 / 76.3% on 99.2% of official rows",
       per_class=PC.get("v1"), outcome="baseline", minutes=1.9,
       lesson="13th of 14 finalists. Winner: -0.4690 / 80.5%.")

record(F, "v2", created_at=t("2026-11-26T19:30"),
       tried="all five fixes at once: layer names, filled curves, wide context, penalty-aware answers, 3-model blend",
       why="copy what the top teams did",
       data="same as v1", open_score=-0.6397, open_accuracy=0.751, outcome="stopped",
       lesson="Worse than v1 on open test (-0.6397 vs -0.6275); blend alone -0.6789. Stopped by the 2-hour limit "
              "before the hidden wells were scored. Lesson: test fixes one at a time.")

for name, s, a, keep, why in [
        ("v3 test: baseline", -0.6061, 0.768, "baseline", "reference for single-fix tests (1/4 of training data)"),
        ("v3 test: + layer names", -0.5906, 0.777, "better", "kept"),
        ("v3 test: + filled curves", -0.5769, 0.776, "better", "kept, best single fix"),
        ("v3 test: + wide context", -0.6109, 0.763, "worse", "dropped: it memorised training-well habits"),
        ("v3 test: + penalty-aware answers", -0.5975, 0.770, "better", "kept")]:
    record(F, name, created_at=t("2026-11-26T20:30"), tried=name.split(": ", 1)[1], why="one fix at a time",
           data="1/4 of training samples, judged on the 10 open test wells only",
           open_score=s, open_accuracy=a, outcome=keep, lesson=why)

record(F, "v3", created_at=t("2026-11-26T20:36"),
       tried="baseline + layer names + filled curves + penalty-aware answers (only the fixes that helped)",
       why="combine the winners of the one-at-a-time tests",
       data="training + open test wells (every 2nd sample); hidden scored once",
       hidden_score=-0.6098, hidden_accuracy=0.767,
       verified="organizers' code and files, 100% of official rows", per_class=PC.get("v3"),
       outcome="better", minutes=5.3,
       lesson="Small gain over v1. On hidden well 16/2-7 V1 matched 82% vs the winner's 81%.")

ladder = json.loads(Path("benchmarks/force2020/ladder_results.json").read_text())
desc = {"1": "same conditions as the teams: ALL training data", "2": "only the 5 most common curves",
        "3": "only 25 training wells (+10 open test)", "4": "learn from southern wells, tested on northern hidden wells",
        "5": "hidden-well logs get 5% noise and missing chunks"}
for k, r in sorted(ladder.items()):
    record(F, f"ladder L{k} {r['name']}", created_at=t("2026-11-26T21:00") + int(k),
           tried=desc[k], why="even playing field first, then harder levels",
           data=f"{r['train_wells']} training wells, {r['hidden_wells']} hidden wells",
           hidden_score=r["score"], hidden_accuracy=r["accuracy"],
           verified="organizers' code and files, 100% of official rows" if k == "1" else None,
           per_class=PC.get("v4") if k == "1" else None,
           outcome="better" if k == "1" else "same", minutes=r["minutes"],
           lesson={"1": "Best so far (all data). Gap to winner: 3.2 points of accuracy. Diagnosis: 29% of all mistake "
                        "cost is sandstone/shale (hard for everyone); V1 trails the winner on limestone, chalk, "
                        "anhydrite, halite, tuff.",
                   "2": "Only 2 points lost without density/neutron logs: good for older BC wells.",
                   "3": "Weakest level: 35 -> 108 training wells is worth +8 points. More labelled wells = biggest lever.",
                   "4": "Moving to a new area costs ~5 points.",
                   "5": "Copes fairly well with noise and gaps."}[k])

record(G, "stream 1 (200 files)", created_at=t("2026-11-26T03:40"),
       tried="1-s windows -> energy per cable stretch x frequency band; event/no-event from the FORGE catalogue",
       why="first real fibre-optic data", data="200 continuous files (53.6 GB streamed, 2 MB kept); 19 hours locked away",
       hidden_accuracy=0.954, outcome="baseline",
       lesson="95.4% sounds great but 92% of windows are quiet; catch rate on real quakes ~50%.")
record(G, "stream 2 (1,400 files)", created_at=t("2026-11-26T05:15"),
       tried="same method, 7x more data", why="see if more data raises the catch rate",
       data="16,570 windows; same 19 locked hours", hidden_accuracy=0.947, outcome="same",
       lesson="Caught 55 of 105 real quakes (52%), 13 false alarms in 1,083 quiet windows. More data did NOT help: "
              "the limit is how windows are cut and what features see, not the amount of data.")
print("backfilled")
