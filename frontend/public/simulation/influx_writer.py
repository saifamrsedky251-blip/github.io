"""Thin helper to write a single observation to InfluxDB v2."""
from __future__ import annotations

import os
import time


def write_observation(measurement: str, tags: dict, fields: dict, ts_ns: int | None = None) -> str:
    """Return InfluxDB line-protocol string and (optionally) send it.

    Environment:
        INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET
    """
    if ts_ns is None:
        ts_ns = int(time.time() * 1e9)

    tag_str = ",".join(f"{k}={v}" for k, v in tags.items())
    field_parts = []
    for k, v in fields.items():
        if isinstance(v, bool):
            field_parts.append(f"{k}={'true' if v else 'false'}")
        elif isinstance(v, int):
            field_parts.append(f"{k}={v}i")
        elif isinstance(v, (float,)):
            field_parts.append(f"{k}={v}")
        else:
            field_parts.append(f'{k}="{v}"')
    field_str = ",".join(field_parts)

    line = f"{measurement},{tag_str} {field_str} {ts_ns}" if tag_str else f"{measurement} {field_str} {ts_ns}"

    if os.environ.get("INFLUX_TOKEN"):
        try:
            from influxdb_client import InfluxDBClient
            from influxdb_client.client.write_api import SYNCHRONOUS
            client = InfluxDBClient(
                url=os.environ["INFLUX_URL"],
                token=os.environ["INFLUX_TOKEN"],
                org=os.environ["INFLUX_ORG"],
            )
            client.write_api(write_options=SYNCHRONOUS).write(
                bucket=os.environ["INFLUX_BUCKET"],
                org=os.environ["INFLUX_ORG"],
                record=line,
            )
        except Exception as e:  # noqa: BLE001
            print(f"[influx] write skipped: {e}")

    return line


if __name__ == "__main__":
    print(write_observation(
        "brewline_summary",
        tags={"line": "A"},
        fields={"produced": 142, "defective": 4, "temp": 94.1, "pressure": 4.43},
    ))
