"""Reads the two config files. Every script gets the region and settings from here."""
from __future__ import annotations

import os
import socket
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file missing: {path}")
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_region(config_dir: Path = CONFIG_DIR) -> dict:
    """Return the region config. An empty name means 'not set yet'."""
    region = _read_yaml(Path(config_dir) / "region.yaml")
    region.setdefault("name", "")
    region.setdefault("bounding_box", {})
    region.setdefault("data_sources", [])
    region["name"] = region["name"] or ""
    region["data_sources"] = region["data_sources"] or []
    return region


def region_is_set(region: dict) -> bool:
    box = region.get("bounding_box") or {}
    return bool(region.get("name")) and all(
        box.get(k) is not None for k in ("min_lat", "max_lat", "min_lon", "max_lon")
    )


def load_settings(config_dir: Path = CONFIG_DIR) -> dict:
    settings = _read_yaml(Path(config_dir) / "settings.yaml")
    settings.setdefault("database", "runs/v1.sqlite")
    settings.setdefault("loop", {})
    return settings


def database_path(settings: dict | None = None) -> Path:
    if os.environ.get("V1_DB"):          # lets tests / trial runs use a separate logbook
        return Path(os.environ["V1_DB"])
    settings = settings or load_settings()
    p = Path(settings["database"])
    return p if p.is_absolute() else PROJECT_ROOT / p


def machine_name(settings: dict | None = None) -> str:
    settings = settings or load_settings()
    return settings.get("machine_name") or socket.gethostname()
