# BrewLine — Smart Coffee Capsule Manufacturing &amp; Monitoring System

A modern, dark‑themed, fully responsive web simulation of a 5‑stage coffee‑capsule production line, with a SCADA HMI, quality control, CMMS, and an InfluxDB / Grafana analytics integration. Built for a university Industrial Informatics module — deployable as a 100% static site on **GitHub Pages**.

> Stack: **HTML · CSS · JavaScript** (browser) + **Python** (simulator) + **InfluxDB v2** + **Grafana**.

---

## Live preview

| Page          | Path                              |
| ------------- | --------------------------------- |
| Landing       | `/index.html`                     |
| Production    | `/pages/production.html`          |
| SCADA         | `/pages/scada.html`               |
| Quality       | `/pages/quality.html`             |
| CMMS          | `/pages/cmms.html`                |
| Analytics     | `/pages/analytics.html`           |
| Documentation | `/pages/docs.html`                |
| About         | `/pages/about.html`               |

---

## Features

- Animated **5‑stage conveyor** with capsules visibly moving through Load → Fill → Seal → Pack → Inspect.
- Industrial **SCADA HMI**: process variables, gauges, alarm log, Start / Stop / Reset / Emergency Stop.
- **Quality control** classifier: underfill, overfill, seal failure, shell damage, packaging failure — with pass / reject %, donut chart, and full defect history.
- **CMMS**: health cards per machine, maintenance schedule, repair log, MTBF / MTTR.
- **Analytics**: live mini‑dashboard + InfluxDB line‑protocol examples + a Grafana provisioning JSON.
- **Dark, industrial** theme with custom palette (charcoal, espresso, cream, copper) and grain overlay.
- Fully **responsive** (desktop / tablet / mobile) and accessible.

---

## Repository structure

```
/
├── index.html
├── assets/
│   ├── css/
│   │   ├── style.css
│   │   └── animations.css
│   └── js/
│       ├── main.js            ← shared simulator (1 Hz tick, localStorage)
│       ├── home.js
│       ├── production.js
│       ├── scada.js
│       ├── quality.js
│       ├── cmms.js
│       └── analytics.js
├── pages/
│   ├── production.html
│   ├── scada.html
│   ├── quality.html
│   ├── cmms.html
│   ├── analytics.html
│   ├── docs.html
│   └── about.html
├── simulation/
│   ├── simulator.py           ← Python replica of the JS simulator
│   └── influx_writer.py
├── dashboard/
│   └── grafana_dashboard.json
├── docs/
│   └── ARCHITECTURE.md
├── screenshots/               ← capture during marking
├── README.md
└── .gitignore
```

---

## Running locally

The site is plain static HTML — no build step.

```bash
# any static server works, e.g.:
python -m http.server 8080
# then open http://localhost:8080
```

To run the Python simulator against a real InfluxDB instance:

```bash
pip install influxdb-client
export INFLUX_URL="http://localhost:8086"
export INFLUX_TOKEN="<your token>"
export INFLUX_ORG="university"
export INFLUX_BUCKET="brewline"
python simulation/simulator.py --speed 12 --defect-rate 0.03
```

Import `dashboard/grafana_dashboard.json` into Grafana to visualise.

---

## Deploying to GitHub Pages

```bash
git init
git add .
git commit -m "1 Setup"
git branch -M main
git remote add origin https://github.com/<your-handle>/brewline.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Source → Deploy from a branch → `main` / `/ (root)`**.
Your site will be served at `https://<your-handle>.github.io/brewline/`.

### Commit plan

| # | Title              |
| - | ------------------ |
| 1 | Setup              |
| 2 | UI                 |
| 3 | Production Logic   |
| 4 | Dashboard          |
| 5 | SCADA              |
| 6 | CMMS               |
| 7 | Quality Control    |
| 8 | Documentation      |
| 9 | Final Deployment   |

---

## Author

See [`pages/about.html`](pages/about.html) — name, student ID, university and course details are editable placeholders.

## License

This project is released for academic use. Adapt freely with attribution.
