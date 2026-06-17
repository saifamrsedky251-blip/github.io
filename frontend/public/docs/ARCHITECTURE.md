# Architecture — BrewLine

```
┌──────────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────┐
│  Browser (HMI)   │←→ │  Simulator   │ → │  InfluxDB v2 │ → │   Grafana   │
│  HTML / CSS / JS │   │  Python · JS │   │  bucket      │   │  dashboard  │
└──────────────────┘   └──────────────┘   └──────────────┘   └─────────────┘
        ▲                       │
        └── shared localStorage ┘
```

## Modules

| ID    | Module           | File                          |
| ----- | ---------------- | ----------------------------- |
| M·01 | Production line  | `pages/production.html`       |
| M·02 | SCADA HMI        | `pages/scada.html`            |
| M·03 | Quality control  | `pages/quality.html`          |
| M·04 | CMMS             | `pages/cmms.html`             |
| M·05 | Analytics        | `pages/analytics.html`        |
| M·06 | Documentation    | `pages/docs.html`             |
| M·07 | About            | `pages/about.html`            |

## Stages

1. **Load capsule** — empty shell loaded onto the carousel.
2. **Fill coffee** — doser drops 5.5 g of ground coffee.
3. **Compress & seal** — piston compresses, foil sealer applies heat at 94 °C.
4. **Packaging** — capsules sleeved into 10‑packs.
5. **Inspect** — vision QC classifies into PASS / 5 reject reasons.

## Data model

```
brewline_summary,line=A  produced,defective,temp,pressure,speed,defect_rate
brewline_health,machine=<m>  value
brewline_inspection,status=<s>,reason=<r>  product_id
```
