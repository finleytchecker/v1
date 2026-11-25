import time

import yaml

from engine.config import load_region, load_settings, region_is_set
from engine.db import Logbook


def test_region_starts_empty():
    region = load_region()
    assert region["name"] == ""
    assert region["data_sources"] == []
    assert not region_is_set(region)


def test_region_is_set_when_filled(tmp_path):
    (tmp_path / "region.yaml").write_text(yaml.safe_dump({
        "name": "Test", "bounding_box": {"min_lat": 1, "max_lat": 2, "min_lon": 3, "max_lon": 4},
        "data_sources": []}))
    assert region_is_set(load_region(tmp_path))


def test_settings_have_loop_limits():
    loop = load_settings()["loop"]
    assert loop["max_rounds"] > 0
    assert 0 < loop["holdout_fraction"] < 1


def test_logbook_full_cycle(tmp_path):
    book = Logbook(tmp_path / "t.sqlite")
    assert book.module_status("leak") == "idle"
    run = book.start_run("leak", "laptop")
    assert book.module_status("leak") == "running"
    assert [r["id"] for r in book.running()] == [run]
    book.log_round(run, 1, 0.8, 0.7, 0.9, n_mistakes=1)
    book.log_round(run, 2, 0.9, 0.85, 0.95)
    book.log_mistakes(run, 1, [{"example_id": 7, "true_label": "leak", "pred_label": "traffic"}])
    assert [r["accuracy"] for r in book.rounds(run)] == [0.8, 0.9]
    assert book.latest_mistakes("leak")[0]["pred_label"] == "traffic"
    book.finish_run(run, holdout_accuracy=0.88)
    assert book.module_status("leak") == "finished"
    assert book.running() == []
    assert book.runs("leak")[0]["holdout_accuracy"] == 0.88


def test_credits_and_compute(tmp_path):
    book = Logbook(tmp_path / "t.sqlite")
    book.add_credits(2.5)
    book.add_credits(1.5, "phase 1")
    assert book.total_credits() == 4.0
    run = book.start_run("fluid", "pc")
    time.sleep(0.05)
    book.finish_run(run)
    assert book.total_compute_seconds() > 0
