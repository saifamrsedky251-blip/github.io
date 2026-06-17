# [ Your Name ] — Portfolio

A personal portfolio site hosting two featured projects, built as a 100% static bundle deployable to **GitHub Pages**.

> Stack: **HTML · CSS · JavaScript** (browser) + **Python** (Magic Survival game + BrewLine simulator) + **InfluxDB v2** + **Grafana** (for BrewLine's analytics path).

---

## Featured projects

### 1. BrewLine — Smart Coffee Capsule Factory  
A simulated end-to-end manufacturing line for single-serve coffee capsules.

- 5-stage animated production line (load → fill → seal → pack → inspect)
- Industrial **SCADA HMI** with gauges, alarms, PV table
- **Quality Control** module: 5-class defect classifier with pass/reject reporting
- **CMMS** (Computerised Maintenance Management) with health cards, scheduled tasks, repair log, MTBF/MTTR
- **Analytics**: InfluxDB line-protocol example + Grafana dashboard JSON (provisioning included)
- Live simulator runs in-browser at 1 Hz and persists to `localStorage`

→ Project hub: [`pages/brewline.html`](pages/brewline.html)

### 2. Magic Survival — Pygame bullet-heaven roguelite  
A solo Python game I designed and coded from scratch.

- 3 character classes (Wizard / Knight / Archer) with distinct stat profiles
- 2 scaling abilities (Firebreath, Lightning chain) with 7 upgrade levels each
- 15-minute survival timer ending in an 8-eyed final boss
- Includes 5 real sound effects (playable directly from the showcase page)
- Downloadable clean bundle: [`downloads/magic-survival.zip`](downloads/magic-survival.zip)

→ Project page: [`pages/magic-survival.html`](pages/magic-survival.html)

---

## Repository structure

```
/
├── index.html                                ← Portfolio landing
├── assets/
│   ├── css/
│   │   ├── style.css                          ← Portfolio + BrewLine theme
│   │   ├── animations.css
│   │   └── magic.css                          ← Magic Survival theme (purple/cyan/gold)
│   ├── js/
│   │   ├── main.js                            ← shared BrewLine simulator
│   │   ├── home.js · production.js · scada.js · quality.js · cmms.js · analytics.js
│   │   └── magic.js                           ← Magic Survival page interactions
│   └── audio/                                 ← real game SFX (5 .wav files)
├── pages/
│   ├── brewline.html                          ← BrewLine project hub
│   ├── magic-survival.html                    ← Game showcase
│   ├── about.html                             ← Personal About (editable placeholders)
│   ├── production.html · scada.html · quality.html · cmms.html · analytics.html · docs.html
├── simulation/
│   ├── simulator.py                           ← Python replica of BrewLine simulator
│   └── influx_writer.py
├── dashboard/
│   └── grafana_dashboard.json                 ← Grafana provisioning
├── downloads/
│   └── magic-survival.zip                     ← Game source + audio + guides
├── docs/
│   └── ARCHITECTURE.md
├── screenshots/
├── README.md
└── .gitignore
```

---

## Running locally

```bash
# any static server works
python -m http.server 8080
# then open http://localhost:8080
```

For the Python BrewLine simulator (optional — for streaming to a real InfluxDB):

```bash
pip install influxdb-client
export INFLUX_URL="http://localhost:8086"
export INFLUX_TOKEN="<your token>"
export INFLUX_ORG="university"
export INFLUX_BUCKET="brewline"
python simulation/simulator.py --speed 12 --defect-rate 0.03
```

For Magic Survival (the game), download `downloads/magic-survival.zip`, then:

```bash
pip install pygame pillow
python setup_assets.py
python MSG.py
```

Full player guide is inside the zip (`PLAYER_GUIDE.txt`).

---

## Deploying to GitHub Pages

```bash
git init
git add .
git commit -m "Portfolio v1"
git branch -M main
git remote add origin https://github.com/<your-handle>/<repo>.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Source → Deploy from a branch → `main` / `/ (root)`**.

---

## About

Edit [`pages/about.html`](pages/about.html) to add your name, student ID, university, course details. Most fields use `contenteditable` so you can edit them inline in the browser, then paste the result back into source.

## License

Released for academic / portfolio use. Adapt freely with attribution.
