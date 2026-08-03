"""Exhaustive finite-input coverage audit for publication QA."""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.data import (  # noqa: E402
    load_cases,
    load_json,
    load_prompts,
    load_quiz,
    load_tools,
    load_workflows,
    recommend_guided_workflow,
    resolve_assessment_pool,
    resolve_prompts,
    resolve_workflows,
    unique_values,
)


def _directory_audit(tools: list[dict]) -> dict[str, int]:
    full = (1 << len(tools)) - 1

    def masks(values: list, predicate) -> list[int]:
        output = []
        for value in values:
            mask = 0
            for index, tool in enumerate(tools):
                if predicate(tool, value):
                    mask |= 1 << index
            output.append(mask)
        return output

    categories = [""] + unique_values(tools, "category")
    specialties = [""] + unique_values(tools, "specialties")
    use_types = [""] + unique_values(tools, "use_type")
    pricing = [""] + unique_values(tools, "pricing_type")
    access = [""] + unique_values(tools, "access_type")
    india = [""] + unique_values(tools, "india_availability")
    technical = ["", "No-code", "Technical"]
    demo = ["", "Public demo", "Institutional"]
    times = [3, 5, 10, 15]

    dimensions = [
        masks(categories, lambda tool, value: not value or tool["category"] == value),
        masks(specialties, lambda tool, value: not value or value in tool["specialties"]),
        masks(use_types, lambda tool, value: not value or tool["use_type"] == value),
        masks(pricing, lambda tool, value: not value or tool["pricing_type"] == value),
        masks(access, lambda tool, value: not value or tool["access_type"] == value),
        masks(india, lambda tool, value: not value or tool["india_availability"] == value),
        masks(technical, lambda tool, value: not value or tool["no_code"] == (value == "No-code")),
        masks(demo, lambda tool, value: not value or tool["public_demo"] == (value == "Public demo")),
        masks(times, lambda tool, value: tool["demo_duration_minutes"] <= value),
    ]
    states = exact = fallback = zero_output = 0
    for selections in product(*dimensions):
        states += 1
        mask = full
        for selection in selections:
            mask &= selection
        if mask:
            exact += 1
        elif tools:
            fallback += 1
        else:
            zero_output += 1
    return {"states": states, "exact": exact, "labelled_fallback": fallback, "zero_output": zero_output}


def run_audit() -> dict[str, dict[str, int]]:
    tools = load_tools()
    workflows = load_workflows()
    prompts = load_prompts()
    cases = load_cases()
    questions = load_quiz()
    specialties = load_json("specialties.json")

    report: dict[str, dict[str, int]] = {"directory": _directory_audit(tools)}

    live_states = live_fallback = live_zero = 0
    for category, level in product(
        ["All"] + sorted({item["category"] for item in workflows}),
        ["All", "Beginner", "Intermediate", "Advanced"],
    ):
        live_states += 1
        resolved, exact = resolve_workflows(workflows, category, level)
        live_fallback += int(not exact)
        live_zero += int(not resolved)
    report["live_demonstrations"] = {"states": live_states, "labelled_fallback": live_fallback, "zero_output": live_zero}

    guided_states = guided_zero = 0
    for duration, specialty, objective, level in product(
        [3, 5, 10, 15],
        specialties,
        ["Patient communication", "Documentation", "Research", "Workflow", "Professional engagement", "Diagnostic awareness"],
        ["Beginner", "Intermediate", "Advanced"],
    ):
        guided_states += 1
        selected, reasons = recommend_guided_workflow(
            workflows, tools, duration=duration, specialty=specialty, objective=objective, level=level
        )
        guided_zero += int(not selected or not reasons)
    report["guided_start"] = {"states": guided_states, "zero_output": guided_zero}

    prompt_states = prompt_fallback = prompt_zero = 0
    for category, specialty in product(
        ["All"] + sorted({item["category"] for item in prompts}),
        ["All"] + sorted({item["specialty"] for item in prompts}),
    ):
        prompt_states += 1
        resolved, exact = resolve_prompts(prompts, category=category, specialty=specialty)
        prompt_fallback += int(not exact)
        prompt_zero += int(not resolved)
    nonsense, nonsense_exact = resolve_prompts(prompts, query="no-such-clinical-task-9z7q")
    prompt_states += 1
    prompt_fallback += int(not nonsense_exact)
    prompt_zero += int(not nonsense)
    report["prompt_library"] = {"states": prompt_states, "labelled_fallback": prompt_fallback, "zero_output": prompt_zero}

    case_states = case_zero = 0
    for specialty in ["All"] + sorted({item["specialty"] for item in cases}):
        case_states += 1
        resolved = cases if specialty == "All" else [item for item in cases if item["specialty"] == specialty]
        case_zero += int(not resolved)
    report["case_library"] = {"states": case_states, "zero_output": case_zero}

    assessment_states = assessment_zero = 0
    for category, count in product(
        ["Mixed"] + sorted({item["category"] for item in questions}), [5, 10, 15, 20]
    ):
        assessment_states += 1
        resolved, _ = resolve_assessment_pool(questions, category, count)
        assessment_zero += int(len(resolved) != count)
    report["assessment"] = {"states": assessment_states, "zero_or_underfilled_output": assessment_zero}

    resources = load_json("resources.json")
    facilitator_states = facilitator_zero = 0
    objectives = ["Balanced", "AI versus Doctor", "Patient centricity", "Communication", "Documentation", "Research", "Workflow", "Diagnostic awareness"]
    tool_names = {tool["name"] for tool in tools}
    for duration, _specialty, _objective in product([30, 60, 90], specialties, objectives):
        facilitator_states += 1
        sequence = resources["recommended_sequences"].get(str(duration), [])
        facilitator_zero += int(not sequence or not any(name in tool_names for name in sequence))
    report["facilitator_plan"] = {"states": facilitator_states, "zero_output": facilitator_zero}

    problem_zero = 0
    for terms in resources["problem_routes"].values():
        matches = [
            tool for tool in tools
            if any(term.casefold() in (tool["problem"] + " " + tool["purpose"] + " " + tool["category"]).casefold() for term in terms)
        ]
        problem_zero += int(not matches)
    report["problem_routes"] = {"states": len(resources["problem_routes"]), "zero_output": problem_zero}

    image_index = load_json("image_index.json")
    modalities = sorted({item["modality"] for item in image_index})
    report["diagnostic_simulations"] = {
        "states": len(modalities),
        "zero_output": sum(not any(item["modality"] == modality for item in image_index) for modality in modalities),
    }
    report["audience_resources"] = {
        "states": len(resources["audience_marketing"]),
        "zero_output": sum(not all(copy.get(key) for key in ("headline", "copy", "cta", "platform_post")) for copy in resources["audience_marketing"].values()),
    }
    return report


if __name__ == "__main__":
    result = run_audit()
    print(json.dumps(result, indent=2))
    if any(value.get("zero_output", value.get("zero_or_underfilled_output", 0)) for value in result.values()):
        raise SystemExit(1)

