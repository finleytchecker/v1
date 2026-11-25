# V1

V1 teaches itself to read ground vibrations. It has two parts that share one engine:

- **Leak**: finds leaks in fiber-optic (DAS) vibration recordings.
- **Fluid**: works out what's underground (water, oil, gas or dry rock) from seismic recordings.

All training runs on your own computers with free Python tools. It never calls Claude or any paid AI service.

## Set up (once)

    pip install -r requirements.txt

## Choose your region

Open `config/region.yaml` and fill in a name, a bounding box (latitude and longitude limits) and any data sources. Every script reads the region from this file.

## Run the tests

    pytest

## Open the dashboard

    streamlit run dashboard/app.py

Then open the link it prints. To check it from your phone, run
`streamlit run dashboard/app.py --server.address 0.0.0.0`
and visit `http://<your-computer's-IP>:8501` while you're on the same Wi-Fi.

## Where things live

| Folder | What's in it |
|---|---|
| `config/` | `region.yaml` (your region) and `settings.yaml` (loop limits, database path) |
| `data/` | `synthetic/` for generated examples, `real/` for downloaded public data |
| `engine/` | Shared parts: config loading, the SQLite logbook, and later the self-teaching loop |
| `modules/leak`, `modules/fluid` | The two detectors |
| `dashboard/` | The web dashboard |
| `runs/` | The logbook database and every saved round |
| `tests/` | Automatic checks |

## Progress

- [x] Phase 1: project, config, logbook, empty dashboard
- [ ] Phase 2: Leak simulator and self-teaching loop
- [ ] Phase 3: Fluid simulator and self-teaching loop
- [ ] Phase 4: Connect both modules to the dashboard
- [ ] Phase 5: Downloaders for real data
- [ ] Phase 6: One command to run everything, plus jobs on other computers
