"""Local data access, validation, search, and resilient filtering."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@dataclass(frozen=True)
class ToolRecord:
    id: str
    name: str
    category: str
    subcategory: str
    purpose: str
    problem: str
    solution: str
    official_url: str
    specialties: list[str]
    intended_users: list[str]
    inputs: list[str]
    outputs: list[str]
    use_type: str
    access_type: str
    pricing_type: str
    pricing_detail: str
    pricing_currency: str
    approximate_inr: str
    pricing_checked: str
    free_tier: str
    india_availability: str
    public_demo: bool
    no_code: bool
    platforms: list[str]
    mobile_support: str
    collaboration: str
    demo_duration_minutes: int
    live_demo_suitability: str
    phi_suitability: str
    phi_warning: str
    regulatory_status: str
    evidence_status: str
    limitations: list[str]
    demo_steps: list[str]
    sample_prompt: str
    alternatives: list[str]
    exports: list[str]
    integrations: list[str]
    geography_notes: str
    last_verified: str
    verification_status: str
    source_urls: list[str]


REQUIRED_TOOL_FIELDS = {field.name for field in fields(ToolRecord)}


@lru_cache(maxsize=None)
def load_json(filename: str) -> Any:
    with (DATA_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def load_tools() -> list[dict[str, Any]]:
    return load_json("tools_catalog.json")


def load_workflows() -> list[dict[str, Any]]:
    return load_json("demo_workflows.json")


def load_prompts() -> list[dict[str, Any]]:
    return load_json("prompts.json")


def load_cases() -> list[dict[str, Any]]:
    return load_json("synthetic_cases.json")


def load_quiz() -> list[dict[str, Any]]:
    return load_json("quiz_bank.json")


def validate_tool(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOOL_FIELDS - set(record))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if not record.get("id") or not record.get("name"):
        errors.append("id and name are required")
    if not str(record.get("official_url", "")).startswith("https://"):
        errors.append("official_url must use https")
    if record.get("demo_duration_minutes", 0) < 1:
        errors.append("demo_duration_minutes must be positive")
    if not isinstance(record.get("specialties"), list):
        errors.append("specialties must be a list")
    if not isinstance(record.get("source_urls"), list) or not record.get("source_urls"):
        errors.append("at least one source URL is required")
    return errors


def validate_catalog(records: Iterable[dict[str, Any]]) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    seen: set[str] = set()
    for index, record in enumerate(records):
        key = str(record.get("id", f"row-{index}"))
        item_errors = validate_tool(record)
        if key in seen:
            item_errors.append("duplicate id")
        seen.add(key)
        if item_errors:
            errors[key] = item_errors
    return errors


def searchable_text(tool: dict[str, Any]) -> str:
    values = [
        tool.get("name", ""), tool.get("category", ""), tool.get("subcategory", ""),
        tool.get("purpose", ""), tool.get("problem", ""), tool.get("solution", ""),
        " ".join(tool.get("specialties", [])), " ".join(tool.get("intended_users", [])),
    ]
    return " ".join(str(value) for value in values).casefold()


def filter_tools(tools: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    query = str(filters.get("query", "")).strip().casefold()
    query_tokens = [token for token in query.replace("-", " ").split() if token]
    result: list[dict[str, Any]] = []
    for tool in tools:
        haystack = searchable_text(tool).replace("-", " ")
        if query_tokens and not all(token in haystack for token in query_tokens):
            continue
        if filters.get("category") and tool["category"] != filters["category"]:
            continue
        if filters.get("specialty") and filters["specialty"] not in tool["specialties"]:
            continue
        if filters.get("use_type") and tool["use_type"] != filters["use_type"]:
            continue
        if filters.get("pricing") and tool["pricing_type"] != filters["pricing"]:
            continue
        if filters.get("access") and tool["access_type"] != filters["access"]:
            continue
        if filters.get("india") and tool["india_availability"] != filters["india"]:
            continue
        if filters.get("no_code") == "No-code" and not tool["no_code"]:
            continue
        if filters.get("no_code") == "Technical" and tool["no_code"]:
            continue
        if filters.get("public_demo") == "Public demo" and not tool["public_demo"]:
            continue
        if filters.get("public_demo") == "Institutional" and tool["public_demo"]:
            continue
        if filters.get("max_time") and tool["demo_duration_minutes"] > int(filters["max_time"]):
            continue
        result.append(tool)
    return result


def closest_alternatives(
    tools: list[dict[str, Any]], filters: dict[str, Any], limit: int = 6
) -> list[dict[str, Any]]:
    """Rank near matches so every filter state remains useful."""
    scored: list[tuple[int, dict[str, Any]]] = []
    query = str(filters.get("query", "")).strip().casefold()
    for tool in tools:
        score = 0
        if query and any(token in searchable_text(tool) for token in query.split()):
            score += 5
        if filters.get("category") == tool["category"]:
            score += 5
        if filters.get("specialty") in tool["specialties"]:
            score += 4
        if filters.get("use_type") == tool["use_type"]:
            score += 3
        if filters.get("pricing") == tool["pricing_type"]:
            score += 2
        if filters.get("access") == tool["access_type"]:
            score += 2
        if filters.get("india") == tool["india_availability"]:
            score += 1
        if filters.get("no_code") == "No-code" and tool["no_code"]:
            score += 1
        if filters.get("no_code") == "Technical" and not tool["no_code"]:
            score += 1
        if filters.get("public_demo") == "Public demo" and tool["public_demo"]:
            score += 1
        if filters.get("public_demo") == "Institutional" and not tool["public_demo"]:
            score += 1
        if filters.get("max_time") and tool["demo_duration_minutes"] <= int(filters["max_time"]):
            score += 1
        scored.append((score, tool))
    scored.sort(key=lambda item: (-item[0], item[1]["name"].casefold()))
    return [tool for _, tool in scored[:limit]]


def resolve_tool_results(
    tools: list[dict[str, Any]], filters: dict[str, Any], limit: int = 6
) -> tuple[list[dict[str, Any]], bool]:
    """Return exact records or explicitly ranked alternatives; never an empty list."""
    exact = filter_tools(tools, filters)
    if exact:
        return exact, True
    return closest_alternatives(tools, filters, limit=limit), False


def tool_filter_match_count(tool: dict[str, Any], filters: dict[str, Any]) -> tuple[int, int]:
    """Count matched finite filters for transparent fallback labelling."""
    checks: list[bool] = []
    query = str(filters.get("query", "")).strip().casefold()
    if query:
        tokens = [token for token in query.replace("-", " ").split() if token]
        haystack = searchable_text(tool).replace("-", " ")
        checks.append(all(token in haystack for token in tokens))
    if filters.get("category"):
        checks.append(tool["category"] == filters["category"])
    if filters.get("specialty"):
        checks.append(filters["specialty"] in tool["specialties"])
    if filters.get("use_type"):
        checks.append(tool["use_type"] == filters["use_type"])
    if filters.get("pricing"):
        checks.append(tool["pricing_type"] == filters["pricing"])
    if filters.get("access"):
        checks.append(tool["access_type"] == filters["access"])
    if filters.get("india"):
        checks.append(tool["india_availability"] == filters["india"])
    if filters.get("no_code"):
        checks.append(tool["no_code"] == (filters["no_code"] == "No-code"))
    if filters.get("public_demo"):
        checks.append(tool["public_demo"] == (filters["public_demo"] == "Public demo"))
    if filters.get("max_time"):
        checks.append(tool["demo_duration_minutes"] <= int(filters["max_time"]))
    return sum(checks), len(checks)


def resolve_workflows(
    workflows: list[dict[str, Any]], category: str = "All", level: str = "All"
) -> tuple[list[dict[str, Any]], bool]:
    """Resolve every category/level state with a disclosed nearest alternative."""
    exact = [
        item for item in workflows
        if (category == "All" or item["category"] == category)
        and (level == "All" or item["level"] == level)
    ]
    if exact:
        return exact, True
    ranked = sorted(
        workflows,
        key=lambda item: (
            category != "All" and item["category"] != category,
            level != "All" and item["level"] != level,
            item["duration_minutes"],
            item["title"].casefold(),
        ),
    )
    return ranked[:6], False


def recommend_guided_workflow(
    workflows: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    *,
    duration: int,
    specialty: str,
    objective: str,
    level: str,
) -> tuple[dict[str, Any], list[str]]:
    """Return one workflow for every guided-start combination and explain the fit."""
    objective_categories = {
        "Patient communication": {"Patient Communication"},
        "Documentation": {"Clinical Documentation"},
        "Research": {"Research & Evidence"},
        "Workflow": {"Workflow & Knowledge", "Administrative Productivity"},
        "Professional engagement": {"Professional Engagement", "Presentations & Teaching"},
        "Diagnostic awareness": {"Precision Diagnostics"},
    }
    categories = objective_categories[objective]
    tools_by_id = {tool["id"]: tool for tool in tools}

    def specialty_fit(item: dict[str, Any]) -> bool:
        tool = tools_by_id.get(item.get("tool_id"), {})
        supported = tool.get("specialties", [])
        return specialty in supported or "General Medicine" in supported

    ranked = sorted(
        workflows,
        key=lambda item: (
            item["category"] not in categories,
            not specialty_fit(item),
            item["duration_minutes"] > duration,
            item["level"] != level,
            abs(item["duration_minutes"] - duration),
            item["title"].casefold(),
        ),
    )
    selected = ranked[0]
    reasons = [f"supports {objective.casefold()}"]
    if specialty_fit(selected):
        reasons.append(f"catalogued for {specialty} or adaptable general medicine use")
    else:
        reasons.append(f"requires adaptation for {specialty}")
    reasons.append(
        f"{selected['duration_minutes']} minutes"
        + (" within the selected time" if selected["duration_minutes"] <= duration else "; use the abbreviated steps")
    )
    reasons.append(selected["level"].casefold() + (" level match" if selected["level"] == level else f"; requested {level.casefold()}"))
    return selected, reasons


def resolve_prompts(
    prompts: list[dict[str, Any]], *, query: str = "", category: str = "All", specialty: str = "All"
) -> tuple[list[dict[str, Any]], bool]:
    """Resolve every prompt-filter state while keeping fallbacks labelled."""
    query_text = query.strip().casefold()
    exact = [
        item for item in prompts
        if (not query_text or query_text in searchable_prompt_text(item))
        and (category == "All" or item["category"] == category)
        and (specialty == "All" or item["specialty"] == specialty)
    ]
    if exact:
        return exact, True
    query_tokens = [token for token in query_text.replace("-", " ").split() if token]
    ranked = sorted(
        prompts,
        key=lambda item: (
            -sum(token in searchable_prompt_text(item).replace("-", " ") for token in query_tokens),
            category != "All" and item["category"] != category,
            specialty != "All" and item["specialty"] != specialty,
            item["title"].casefold(),
        ),
    )
    return ranked[:17], False


def searchable_prompt_text(prompt: dict[str, Any]) -> str:
    return " ".join(
        str(prompt.get(key, ""))
        for key in ("title", "category", "specialty", "use_case", "decision_question", "prompt")
    ).casefold()


def resolve_assessment_pool(
    questions: list[dict[str, Any]], category: str, count: int
) -> tuple[list[dict[str, Any]], int]:
    """Supply the requested question count, supplementing short category pools."""
    primary = questions if category == "Mixed" else [item for item in questions if item["category"] == category]
    selected = list(primary[:count])
    if len(selected) < count:
        selected_ids = {item["id"] for item in selected}
        selected.extend(item for item in questions if item["id"] not in selected_ids)
    selected = selected[:count]
    return selected, max(0, len(selected) - min(len(primary), count))


def find_tool(tool_id: str) -> dict[str, Any] | None:
    return next((tool for tool in load_tools() if tool["id"] == tool_id), None)


def unique_values(tools: list[dict[str, Any]], key: str) -> list[str]:
    values: set[str] = set()
    for tool in tools:
        value = tool.get(key)
        if isinstance(value, list):
            values.update(str(item) for item in value)
        elif value:
            values.add(str(value))
    return sorted(values)
