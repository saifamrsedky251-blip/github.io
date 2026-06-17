"""
BrewLine — Coffee Capsule Production Line simulator
====================================================

Reproduces the same 5-stage production model used in the browser HMI,
but emits real time-series points to an InfluxDB v2 bucket.

Usage:
    pip install influxdb-client
    export INFLUX_URL="http://localhost:8086"
    export INFLUX_TOKEN="<your token>"
    export INFLUX_ORG="university"
    export INFLUX_BUCKET="brewline"
    python simulator.py --speed 12 --defect-rate 0.03

Run without InfluxDB (dry run) to just see the stream on stdout:
    python simulator.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


STAGES = ["load", "fill", "seal", "pack", "inspect"]
DEFECTS = [
    ("underfill", 0.30, "warn"),
    ("overfill",  0.18, "warn"),
    ("seal",      0.22, "bad"),
    ("shell",     0.14, "bad"),
    ("pack",      0.16, "warn"),
]


@dataclass
class State:
    running: bool = True
    speed_cpm: int = 12               # capsules per minute
    defect_rate: float = 0.03
    produced: int = 0
    defective: int = 0
    rejects: dict = field(default_factory=lambda: {k: 0 for k, _, _ in DEFECTS})
    temperature: float = 92.0
    pressure: float = 4.2
    runtime_s: float = 0.0
    health: dict = field(default_factory=lambda: {
        "loader": 96, "filler": 91, "sealer": 88, "packer": 94, "inspector": 97
    })


def pick_defect():
    r = random.random(); acc = 0
    for k, w, sev in DEFECTS:
        acc += w
        if r <= acc:
            return k, sev
    return DEFECTS[0][0], DEFECTS[0][2]


def make_product_id(n: int) -> str:
    return f"CAP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{n:06d}"


def tick(state: State, dt: float):
    # sensor drift
    state.temperature += (94 - state.temperature) * 0.08 + (random.random() - 0.5) * 0.6
    state.pressure    += (4.5 - state.pressure)   * 0.10 + (random.random() - 0.5) * 0.15

    if not state.running:
        return []

    state.runtime_s += dt
    per_sec = state.speed_cpm / 60.0
    n = int(per_sec * dt + random.random() * 0.6)

    events = []
    for _ in range(n):
        state.produced += 1
        pid = make_product_id(state.produced)
        if random.random() < state.defect_rate:
            kind, sev = pick_defect()
            state.defective += 1
            state.rejects[kind] += 1
            events.append({"id": pid, "status": "REJECT", "reason": kind, "sev": sev})
        else:
            events.append({"id": pid, "status": "PASS", "reason": "ok", "sev": "info"})

    # health drift
    for k in state.health:
        if random.random() < 0.06:
            state.health[k] = max(40, state.health[k] - random.random() * 0.25)

    return events


def to_line_protocol(state: State, events):
    """Emit one summary point per second + one point per inspection event."""
    ts = int(time.time() * 1e9)
    lines = []
    lines.append(
        f"brewline_summary,line=A produced={state.produced}i,defective={state.defective}i,"
        f"temp={state.temperature:.2f},pressure={state.pressure:.3f},"
        f"speed={state.speed_cpm}i,defect_rate={state.defect_rate:.4f} {ts}"
    )
    for k, v in state.health.items():
        lines.append(f"brewline_health,machine={k} value={v:.2f} {ts}")
    for ev in events:
        lines.append(
            f'brewline_inspection,status={ev["status"]},reason={ev["reason"]} '
            f'product_id="{ev["id"]}" {ts}'
        )
    return lines


def main():
    ap = argparse.ArgumentParser(description="BrewLine simulator")
    ap.add_argument("--speed", type=int, default=12, help="capsules per minute")
    ap.add_argument("--defect-rate", type=float, default=0.03)
    ap.add_argument("--duration", type=int, default=0, help="seconds, 0 = forever")
    ap.add_argument("--tick", type=float, default=1.0, help="seconds per tick")
    ap.add_argument("--dry-run", action="store_true", help="print line protocol to stdout")
    args = ap.parse_args()

    state = State(speed_cpm=args.speed, defect_rate=args.defect_rate)

    writer = None
    if not args.dry_run:
        try:
            from influxdb_client import InfluxDBClient, Point  # noqa: F401
            from influxdb_client.client.write_api import SYNCHRONOUS
            url = os.environ["INFLUX_URL"]
            token = os.environ["INFLUX_TOKEN"]
            org = os.environ["INFLUX_ORG"]
            bucket = os.environ["INFLUX_BUCKET"]
            client = InfluxDBClient(url=url, token=token, org=org)
            writer = client.write_api(write_options=SYNCHRONOUS)
            print(f"[brewline] connected → {url} bucket={bucket}")
        except Exception as e:
            print(f"[brewline] influx disabled — {e}. Falling back to dry-run.")
            writer = None
            bucket = None
            org = None

    started = time.time()
    print(f"[brewline] simulating @ {state.speed_cpm} cpm, defect_rate={state.defect_rate:.2%}")
    try:
        while True:
            events = tick(state, args.tick)
            lines = to_line_protocol(state, events)
            if writer:
                writer.write(bucket=bucket, org=org, record=lines)
            else:
                for ln in lines[:3]:
                    print(ln)
            if args.duration and time.time() - started >= args.duration:
                break
            time.sleep(args.tick)
    except KeyboardInterrupt:
        print(f"\n[brewline] stopped. produced={state.produced} defective={state.defective}")


if __name__ == "__main__":
    main()
