# PRD — BrewLine: Smart Coffee Capsule Manufacturing & Monitoring System

## Original problem statement
University project — modern, dark-themed, responsive website that simulates a coffee-capsule production line and demonstrates industrial software practices (SCADA, CMMS, Quality Control, Analytics). Stack: HTML / CSS / JS frontend, Python simulator, InfluxDB time-series, Grafana dashboards, Git + GitHub Pages.

## Architecture
- 100% static site, deployable on GitHub Pages.
- Browser-side simulator (`Brew` singleton) ticks at 1 Hz and persists to `localStorage`.
- Parallel Python simulator + InfluxDB writer included for real-plant deployment.
- Grafana dashboard provisioning JSON committed.

## Personas
- Operator (uses SCADA + Production controls)
- Maintenance engineer (CMMS)
- Quality engineer (QC defect breakdown)
- Faculty grader (Docs + About)

## Core requirements (static)
- 8 pages: Landing, About, Production, SCADA, Quality, CMMS, Analytics, Docs
- 5-stage animated production: load → fill → seal → pack → inspect
- Controls: Start, Stop, Reset, Emergency Stop
- Live KPIs: produced, defective, efficiency, speed, runtime
- 5 defect classes: underfill, overfill, seal, shell, pack
- CMMS: 5 machines with health degradation + repair log
- InfluxDB + Grafana integration plan
- Dark charcoal / espresso / cream / copper theme

## Delivered (2026-02)
- All 8 pages, responsive + animated.
- Functional simulator with capsule animation, KPI counters, defect injection.
- SCADA HMI: gauges, PV table, alarm bus, runtime, E-Stop.
- Quality donut + defect breakdown + history.
- CMMS health cards, schedule, repair log, MTBF/MTTR.
- Analytics: 4 sparkline canvases + InfluxDB line-protocol example + Grafana JSON.
- Documentation (9 sections) + editable About page.
- Python simulator (`simulation/simulator.py`) + InfluxDB writer.
- README.md + .gitignore + folder structure as per spec.

## Bug fixes (iteration 1)
- Fixed `produced` counter not incrementing at low speeds (proper fractional accumulator).
- Added `data-testid="qc-yield"` for donut center.
- Verified CMMS repair log appends correctly.

## Prioritised backlog
- P1 — WebSocket live bridge between Python simulator and static UI.
- P1 — TensorFlow.js vision QC (real defect classifier on capsule images).
- P2 — OPC-UA gateway to a real PLC.
- P2 — Multi-line tenancy + recipe management.
- P2 — Charts library (Chart.js / D3) for richer time-series panels.
- P3 — Shift report PDF export.

## Files of interest
- `/app/frontend/public/index.html` (landing)
- `/app/frontend/public/pages/*.html` (modules)
- `/app/frontend/public/assets/js/main.js` (Brew singleton — simulator)
- `/app/frontend/public/simulation/simulator.py`
- `/app/frontend/public/dashboard/grafana_dashboard.json`

## Deployment
GitHub Pages from `/app/frontend/public/` root (push contents to a repo, enable Pages on `main` / `/`).
