"""Transcribe the 11 ROSES 2020 lectures (AGU Seismology) into text files. Free, all Python, no AI service.

Run this on YOUR computer (YouTube blocks cloud servers):
    pip install yt-dlp faster-whisper
    python course/roses2020/transcribe.py

How it works, per lecture:
  1. Try YouTube's own captions (fast, a few seconds).
  2. If there are none, download the audio only and transcribe it locally with Whisper
     (an open speech-to-text model that runs on your own computer; ~10-30 min per lecture on a laptop).
Output: course/roses2020/transcripts/unitNN_<topic>.md   (skips lectures already done)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "transcripts"
TMP = HERE / "_tmp"

LECTURES = [  # (unit, topic, speaker, YouTube id) from connect.agu.org/seismology/roses/roses2020materials
    (1, "ObsPy", "Sydney Dybing", "PRECSp2bb20"),
    (2, "Data and Metadata", "Emily Wolin", "tDG8hlWjfkk"),
    (3, "Time Series Analysis", "German Prieto", "-ExS8qX8ORg"),
    (4, "Waveform Cross Correlation", "Elizabeth Berg", "RO0MuvPl9DI"),
    (5, "Array Seismology and Network Analysis", "Stephen Arrowsmith", "TUm79QRJFp8"),
    (6, "Polarization Analysis", "Tolulope Olugboji", "Wf54lhzq9OI"),
    (7, "Machine Learning", "Zachary Ross", "3lLnjhZEaRY"),
    (8, "PyGMT", "Liam Toney", "SSIGJEe0BIk"),
    (9, "Inversion, Bayesian", "Steve Myers", "tz0SNGrSYBg"),
    (10, "Inversion, Kriging", "Tony Lowry", "czKLeHePujs"),
    (11, "Inversion, Gridding and Tomography", "Suzan van der Lee", "jCjTwUl17RY"),
]
# Pairing taken from each unit's own "Click Here for Lecture" link on the AGU page.


def vtt_to_text(vtt: str) -> str:
    lines, last = [], None
    for line in vtt.splitlines():
        if "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")) or not line.strip():
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line != last:          # auto-captions repeat each line; drop the repeats
            lines.append(line)
            last = line
    text = " ".join(lines)
    return re.sub(r"(.{1,90})(?:\s|$)", r"\1\n", text)


def captions(vid: str) -> str | None:
    TMP.mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-m", "yt_dlp", "--skip-download", "--write-subs", "--write-auto-subs",
                    "--sub-langs", "en.*", "--sub-format", "vtt", "-o", str(TMP / vid),
                    f"https://www.youtube.com/watch?v={vid}"], capture_output=True)
    files = sorted(TMP.glob(f"{vid}*.vtt"))
    return vtt_to_text(files[0].read_text(errors="ignore")) if files else None


def whisper(vid: str) -> str:
    from faster_whisper import WhisperModel
    subprocess.run([sys.executable, "-m", "yt_dlp", "-f", "bestaudio", "-o", str(TMP / f"{vid}.%(ext)s"),
                    f"https://www.youtube.com/watch?v={vid}"], check=True)
    audio = next(p for p in TMP.glob(f"{vid}.*") if p.suffix != ".vtt")
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio), vad_filter=True)
    text = "\n".join(s.text.strip() for s in segments)
    audio.unlink()
    return text


def main():
    OUT.mkdir(exist_ok=True)
    for unit, topic, speaker, vid in LECTURES:
        out = OUT / f"unit{unit:02d}_{re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')}.md"
        if out.exists():
            print(f"unit {unit}: already done")
            continue
        print(f"unit {unit}: {topic} ...", flush=True)
        text, how = captions(vid), "YouTube captions"
        if not text:
            text, how = whisper(vid), "transcribed locally with Whisper"
        out.write_text(f"# ROSES 2020 Unit {unit}: {topic}\n\nSpeaker: {speaker}  \n"
                       f"Video: https://www.youtube.com/watch?v={vid}  \nSource: {how}\n\n{text}\n")
        print(f"   saved {out.name} ({len(text.split()):,} words, {how})")


if __name__ == "__main__":
    main()
