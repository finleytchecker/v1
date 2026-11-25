"""Downloads the real public datasets listed in config/datasets.yaml.

Safety rules:
  * The size is checked BEFORE downloading (HTTP HEAD or the public S3 listing).
  * Anything bigger than settings.download.ask_above_gb (5 GB) is refused unless you pass --approve.
  * Downloads resume where they stopped, and every one is logged in the SQLite logbook.

Usage:
    python -m engine.data.downloader plan                 # list everything, sizes, what's already here
    python -m engine.data.downloader fetch <id> [<id>..]  # download (small ones only)
    python -m engine.data.downloader fetch <id> --approve # you said OK to a big one
    python -m engine.data.downloader fetch --priority 1   # all small, labeled starter pieces
"""
from __future__ import annotations

import argparse
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
import yaml

from engine.config import CONFIG_DIR, PROJECT_ROOT, database_path, load_settings
from engine.db import Logbook

GB = 1024 ** 3
S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"


def load_catalog(path: Path = CONFIG_DIR / "datasets.yaml") -> list[dict]:
    if not path.exists():
        return []
    return yaml.safe_load(open(path)) or []


def human(n):
    if n is None:
        return "unknown size"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024


# ------------------------------------------------------------------ listing files

def _s3_split(url):
    """https://bucket.s3.amazonaws.com/prefix/  or  s3://bucket/prefix  ->  (endpoint, prefix)."""
    if url.startswith("s3://"):
        bucket, _, prefix = url[5:].partition("/")
        return f"https://{bucket}.s3.amazonaws.com", prefix
    p = urllib.parse.urlparse(url)
    return f"{p.scheme}://{p.netloc}", p.path.lstrip("/")


def s3_list(url, max_keys=100000):
    endpoint, prefix = _s3_split(url)
    files, token = [], None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        r = requests.get(endpoint + "/", params=q, timeout=60)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        for c in root.iter(S3_NS + "Contents"):
            key = c.find(S3_NS + "Key").text
            if not key.endswith("/"):
                files.append(dict(url=f"{endpoint}/{urllib.parse.quote(key)}", key=key,
                                  size=int(c.find(S3_NS + "Size").text)))
        token_el = root.find(S3_NS + "NextContinuationToken")
        if token_el is None or len(files) >= max_keys:
            return files
        token = token_el.text


def files_for(entry) -> list[dict]:
    """Every file an entry covers, with sizes."""
    method = entry.get("method", "http")
    url = entry["url"]
    if method == "s3-public":
        return s3_list(url)
    if method == "http":
        urls = url if isinstance(url, list) else [url]
        out = []
        for u in urls:
            try:
                h = requests.head(u, allow_redirects=True, timeout=60)
                size = int(h.headers["Content-Length"]) if "Content-Length" in h.headers else None
            except requests.RequestException:
                size = None
            out.append(dict(url=u, key=Path(urllib.parse.urlparse(u).path).name, size=size))
        return out
    return []   # globus / manual-login: can't be fetched by script


def total_size(entry, files=None):
    files = files if files is not None else files_for(entry)
    if files and all(f["size"] is not None for f in files):
        return sum(f["size"] for f in files)
    return entry.get("size_bytes")


# ------------------------------------------------------------------ downloading

def _download_one(url, dest: Path, expected=None, chunk=1 << 20):
    dest.parent.mkdir(parents=True, exist_ok=True)
    have = dest.stat().st_size if dest.exists() else 0
    if expected is not None and have == expected:
        return have
    headers = {"Range": f"bytes={have}-"} if have else {}
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        if r.status_code == 416:      # already complete
            return have
        r.raise_for_status()
        mode = "ab" if r.status_code == 206 else "wb"
        with open(dest, mode) as f:
            for block in r.iter_content(chunk):
                f.write(block)
    return dest.stat().st_size


def safe_name(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def fetch(entry, approve=False, log=print, book: Logbook | None = None):
    settings = load_settings()
    limit = settings.get("download", {}).get("ask_above_gb", 5) * GB
    root = PROJECT_ROOT / settings.get("download", {}).get("folder", "data/real")
    method = entry.get("method", "http")
    if method in ("globus", "manual-login") or entry.get("needs_login"):
        log(f"[{entry['id']}] needs a login or Globus; can't be fetched by script. See notes: {entry.get('notes','')}")
        return "skipped"
    files = files_for(entry)
    size = total_size(entry, files)
    if size is None and not approve:
        log(f"[{entry['id']}] size unknown, so not downloading without your OK (--approve).")
        return "needs_approval"
    if size is not None and size > limit and not approve:
        log(f"[{entry['id']}] is {human(size)}, over the {human(limit)} limit. Ask the owner, then run with --approve.")
        return "needs_approval"
    dest_dir = root / safe_name(entry.get("dataset", "other")) / safe_name(entry["id"])
    log(f"[{entry['id']}] downloading {len(files)} file(s), {human(size)} -> {dest_dir.relative_to(PROJECT_ROOT)}")
    t0, got = time.time(), 0
    try:
        for f in files:
            got += _download_one(f["url"], dest_dir / f["key"].replace("/", "__"), f["size"])
        status = "done"
    except Exception as e:  # noqa: BLE001 - logged and reported
        status = f"failed: {e}"
        log(f"[{entry['id']}] {status}")
    if book:
        book.log_download(entry["id"], entry.get("dataset", ""), got, status, time.time() - t0, str(dest_dir))
    return status


def plan(log=print):
    settings = load_settings()
    limit = settings.get("download", {}).get("ask_above_gb", 5) * GB
    cat = load_catalog()
    if not cat:
        log("config/datasets.yaml is empty.")
    for e in sorted(cat, key=lambda e: (e.get("priority", 9), e["id"])):
        try:
            size = total_size(e) if e.get("method") in ("http", "s3-public") else e.get("size_bytes")
        except requests.RequestException:
            size = e.get("size_bytes")
        flag = "ASK FIRST" if size is None or size > limit else "ok"
        if e.get("needs_login") or e.get("method") in ("globus", "manual-login"):
            flag = "LOGIN"
        log(f"p{e.get('priority', '?')}  {e['id']:40s} {human(size):>12s}  {flag:9s} {e.get('module', '')}: {e.get('labels', '')[:70]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["plan", "fetch"])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--approve", action="store_true", help="the owner OK'd downloading over the size limit")
    ap.add_argument("--priority", type=int, help="fetch every entry with this priority")
    a = ap.parse_args()
    if a.action == "plan":
        plan()
    else:
        book = Logbook(database_path())
        cat = {e["id"]: e for e in load_catalog()}
        ids = a.ids or [i for i, e in cat.items() if a.priority is not None and e.get("priority") == a.priority]
        for i in ids:
            fetch(cat[i], approve=a.approve, book=book)
