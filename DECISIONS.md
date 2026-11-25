# V1 decision log
Kept here because Brain 2.0 (on the Mac) was out of reach from the cloud session. Copy these in with Brain 2.0/bin/add.py.

## Phase 1 (2026-11-25)
- Project named **V1** (it was "Tremor" in the brief). It lives in its own repo for now and moves into Brain 2.0/projects later.
- Run logs go to one SQLite file (`runs/v1.sqlite`) with 4 tables: runs, rounds, mistakes, credits.
- A module's status is the status of its latest run: idle (never run), running, finished or failed.
- Compute time = the sum of each run's wall-clock time. Claude credits are entered by hand on the dashboard.
- Loop limits live in `config/settings.yaml`: max 10 rounds, stop after 3 rounds without improvement, 15% final hold-out that the loop never sees.
- Dashboard: Streamlit with a black background, white text, base font 22px, for reading on a phone.
