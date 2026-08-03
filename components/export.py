"""Safe local exports for plans and selected content."""

from __future__ import annotations

import csv
import io
import json


def as_json_bytes(data: object) -> bytes:
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def tools_as_csv(tools: list[dict]) -> bytes:
    buffer = io.StringIO()
    fields = ["id", "name", "category", "purpose", "official_url", "pricing_type", "india_availability", "last_verified"]
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for tool in tools:
        writer.writerow({field: tool.get(field, "") for field in fields})
    return buffer.getvalue().encode("utf-8")

