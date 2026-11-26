"""Stream-and-shrink: pull huge public datasets file by file, keep only small features, delete the raw file.

This is how V1 learns from terabytes without buying terabytes of disk:
  * several files download at the same time (parallel connections use more of your internet line)
  * each file is turned into features (~9 KB from 288 MB) and the raw file is deleted straight away
  * progress is remembered, so it can be stopped and restarted any time

Usage:
    python -m engine.data.stream forge --max-files 200            # files around catalogued events + quiet ones
    python -m engine.data.stream forge --max-files 200 --workers 8
    python -m engine.data.stream forge --plan                     # just show how much would be streamed

Tip: the FORGE files live on Amazon in the us-west-2 region. Running this on a small Amazon computer
in that region instead of at home makes the download near-instant and free of internet limits.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import tempfile
import time
from pathlib import Path

import numpy as np
import requests

from engine.config import PROJECT_ROOT, database_path, load_settings
from engine.data.downloader import human, s3_list
from engine.db import Logbook

FORGE_PREFIX = "https://gdr-data-lake.s3.amazonaws.com/FORGE/DAS/april_2024/Neubrex/"
KEYS_CACHE = PROJECT_ROOT / "data" / "features" / "forge_keys.json"


def forge_keys():
    if KEYS_CACHE.exists():
        return json.loads(KEYS_CACHE.read_text())
    files = [f for f in s3_list(FORGE_PREFIX, max_keys=10 ** 7) if f["key"].endswith(".sgy")]
    KEYS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    KEYS_CACHE.write_text(json.dumps(files))
    return files


def forge_plan(max_files, seed=0):
    """Half the files contain a catalogued event (answer = event), half are quiet (answer = no event)."""
    from modules.leak.forge_das import catalog_times, start_time
    times = catalog_times()
    files = forge_keys()
    starts = np.array([start_time(f["key"]).timestamp() for f in files])
    has_event = np.array([((times >= s) & (times < s + 12)).any() for s in starts])
    # only use quiet files from the same days as the catalogue, so 'quiet' is comparable
    in_span = (starts >= times.min() - 3600) & (starts <= times.max() + 3600)
    ev = np.where(has_event)[0]
    quiet = np.where(~has_event & in_span)[0]
    rng = np.random.default_rng(seed)
    k = max_files // 2
    pick = list(rng.choice(ev, min(k, len(ev)), replace=False)) + list(rng.choice(quiet, min(k, len(quiet)), replace=False))
    return [files[i] for i in sorted(pick)], times, dict(total_files=len(files), event_files=int(has_event.sum()),
                                                        total_bytes=int(sum(f["size"] for f in files)))


def _one(f, times, tmp):
    from modules.leak.forge_das import FEAT_DIR, shrink_file
    out = FEAT_DIR / (Path(f["key"]).stem + ".npz")
    if out.exists():
        return f, "skip", 0, 0.0
    t0 = time.time()
    local = Path(tmp) / Path(f["key"]).name
    for attempt in range(4):
        try:
            with requests.get(f["url"], stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(local, "wb") as fh:
                    for block in r.iter_content(1 << 22):
                        fh.write(block)
            break
        except requests.RequestException:
            time.sleep(2 ** attempt)
    else:
        return f, "failed", 0, time.time() - t0
    try:
        shrink_file(str(local), times)
        status = "done"
    except Exception as e:  # noqa: BLE001
        status = f"failed: {e}"
    finally:
        local.unlink(missing_ok=True)          # raw file never stays on disk
    return f, status, f["size"], time.time() - t0


def stream_forge(max_files=200, workers=6, plan_only=False, log=print):
    book = Logbook(database_path(load_settings()))
    files, times, info = forge_plan(max_files)
    todo_bytes = sum(f["size"] for f in files)
    log(f"FORGE continuous DAS: {info['total_files']:,} files ({human(info['total_bytes'])}), "
        f"{info['event_files']:,} contain a catalogued event.")
    log(f"This run: {len(files)} files, {human(todo_bytes)} streamed, about {human(len(files) * 9500)} kept.")
    if plan_only:
        return
    run_id = book.start_run("leak", "stream", notes=f"stream forge {len(files)} files", data_source="real")
    done = moved = 0
    t_start = time.time()
    with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "data") as tmp, cf.ThreadPoolExecutor(workers) as pool:
        for f, status, nbytes, secs in pool.map(lambda f: _one(f, times, tmp), files):
            done += 1
            moved += nbytes
            book.log_download(f"stream:{Path(f['key']).name}", "forge-das-stream", nbytes, status, secs, "features only")
            rate = moved / max(1e-9, time.time() - t_start)
            log(f"  {done}/{len(files)} {status:6s} {Path(f['key']).name}  ({human(rate)}/s overall)")
    book.finish_run(run_id, "finished")
    log(f"Streamed {human(moved)} in {(time.time() - t_start) / 60:.1f} min.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset", choices=["forge"])
    ap.add_argument("--max-files", type=int, default=200)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--plan", action="store_true")
    a = ap.parse_args()
    stream_forge(a.max_files, a.workers, a.plan)
