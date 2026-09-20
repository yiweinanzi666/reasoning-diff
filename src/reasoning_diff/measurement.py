"""Finite intervention measurements, with explicit support and structural changes."""
from __future__ import annotations

from collections import defaultdict
import math
import numpy as np
from .events import align_events
from .schema import Task, Trace


def compare(base: Trace, changed: Trace, premise_id: str, edit_id: str, *, kind="edit") -> dict:
    if base.base_id != changed.base_id or base.model != changed.model:
        raise ValueError("Comparisons must use same base problem and model")
    if kind == "edit" and base.seed != changed.seed:
        raise ValueError("Paired edit comparison must use a common random stream")
    alignment = align_events(base.events, changed.events)
    valid = base.status == "ok" and changed.status == "ok"
    return {"base_id": base.base_id, "base_trace": base.id, "changed_trace": changed.id,
            "premise_id": premise_id, "edit_id": edit_id, "kind": kind,
            "status": "ok" if valid else "generation_failure",
            "values": [{"event": left.identity.key(), "changed": left.value != right.value,
                        "base_value": left.value, "new_value": right.value}
                       for left, right in alignment["pairs"]] if valid else [],
            "removed": alignment["removed"], "added": alignment["added"],
            "base_event_count": len(base.events), "changed_event_count": len(changed.events)}


def build_labels(task: Task, trace: Trace, observations: list[dict], *, minimum_observations=1) -> dict:
    """0 = no response in evaluated finite scan, not proven causal independence.

    Unknown entries are -1; masks must exclude them from loss and metrics. Sham
    opportunities are paired by edit ID so edit/noise densities use common support.
    """
    if minimum_observations < 1:
        raise ValueError("minimum_observations must be positive")
    event_keys = [e.identity.key() for e in trace.events]
    premises = [p.id for p in task.premises]
    shape = (len(event_keys), len(premises))
    by_cell = defaultdict(lambda: {"edit": {}, "noise": {}})
    for record in observations:
        if record["base_trace"] != trace.id or record["status"] != "ok":
            continue
        if record["premise_id"] not in premises or record["kind"] not in ("edit", "noise"):
            raise ValueError("Observation has an unknown premise or comparison kind")
        for value in record["values"]:
            key = (value["event"], record["premise_id"])
            bucket = by_cell[key][record["kind"]]
            if record["edit_id"] in bucket:
                raise ValueError("Duplicate perturbation/sham opportunity")
            bucket[record["edit_id"]] = int(value["changed"])
    behavior = np.full(shape, -1, dtype=int)
    noise = np.full(shape, -1, dtype=int)
    task_labels = np.full(shape, -1, dtype=int)
    counts = np.zeros(shape, dtype=int)
    rates = np.full(shape, np.nan)
    noise_rates = np.full(shape, np.nan)
    for i, event in enumerate(trace.events):
        for j, premise in enumerate(premises):
            if event.task_parents is not None:
                task_labels[i, j] = int(premise in event.task_parents)
            cell = by_cell[(event_keys[i], premise)]
            # A common opportunity set is necessary for signed subtraction.
            shared = cell["edit"].keys() & cell["noise"].keys()
            if len(shared) >= minimum_observations:
                edited = [cell["edit"][key] for key in shared]
                sham = [cell["noise"][key] for key in shared]
                behavior[i, j], noise[i, j] = max(edited), max(sham)
                counts[i, j] = len(shared)
                rates[i, j], noise_rates[i, j] = np.mean(edited), np.mean(sham)
    def serial(array):
        return [[None if isinstance(v, float) and not math.isfinite(v) else v for v in row]
                for row in array.tolist()]
    density = dependency_densities(task_labels, behavior, noise)
    return {"trace_id": trace.id, "base_id": trace.base_id, "event_keys": event_keys,
            "premise_ids": premises, "task": serial(task_labels), "behavior": serial(behavior),
            "noise": serial(noise), "opportunities": serial(counts),
            "response_rate": serial(rates), "noise_rate": serial(noise_rates),
            "label_scope": "empirical_finite_scan_common_support",
            "densities": density,
            "structural_comparisons": sum(bool(r["removed"] or r["added"]) for r in observations
                                          if r["base_trace"] == trace.id),
            "failed_comparisons": sum(r["status"] != "ok" for r in observations
                                      if r["base_trace"] == trace.id)}


def dependency_densities(task: np.ndarray, behavior: np.ndarray, noise: np.ndarray) -> dict:
    if task.shape != behavior.shape or task.shape != noise.shape or task.ndim != 2:
        raise ValueError("Expected equal event × premise label matrices")
    support = (task >= 0) & (behavior >= 0) & (noise >= 0)
    result = {"events": [], "support_cells": int(support.sum()), "total_cells": int(task.size)}
    for i in range(task.shape[0]):
        row = {}
        for name, eligible in (("S", task[i] == 0), ("M", task[i] == 1)):
            mask = support[i] & eligible
            total_eligible = int(eligible.sum())
            denominator = int(mask.sum())
            raw = float(((behavior[i] == (1 if name == "S" else 0)) & mask).sum() / denominator) if denominator else None
            ref = float(((noise[i] == (1 if name == "S" else 0)) & mask).sum() / denominator) if denominator else None
            row[name] = {"raw": raw, "noise": ref, "excess": raw - ref if raw is not None else None,
                         "denominator": denominator, "eligible": total_eligible,
                         "coverage": denominator / total_eligible if total_eligible else None}
        result["events"].append(row)
    for name in ("S", "M"):
        for kind in ("raw", "noise", "excess"):
            values = [row[name][kind] for row in result["events"] if row[name][kind] is not None]
            result[f"rho_{name}_{kind}"] = float(np.mean(values)) if values else None
    result["interpretation"] = "signed descriptive excess on evaluated common support; M is empirical"
    return result


def lcs_overlap(left: list, right: list) -> float | None:
    if not left and not right:
        return None
    if len(left) < len(right):
        left, right = right, left
    previous = [0] * (len(right) + 1)
    for item in left:
        current = [0]
        for j, other in enumerate(right, 1):
            current.append(previous[j - 1] + 1 if item == other else max(previous[j], current[-1]))
        previous = current
    return 2 * previous[-1] / (len(left) + len(right))


def preservation(base: Trace, changed: Trace, edited_premises: set[str]) -> dict:
    aligned = align_events(base.events, changed.events)
    clean_base = [e for e in base.events if e.task_parents is not None
                  and not edited_premises.intersection(e.task_parents)]
    clean = [(a, b) for a, b in aligned["pairs"] if a.task_parents is not None
             and not edited_premises.intersection(a.task_parents)]
    dirty = [(a, b) for a, b in aligned["pairs"] if a.task_parents is not None
             and edited_premises.intersection(a.task_parents)]
    def token_region(trace, events):
        return [token for token, (a, b) in zip(trace.token_ids, trace.offsets, strict=True)
                if any(e.start <= a < b <= e.end for e in events)]
    return {"csp": sum(a.value == b.value for a, b in clean) / len(clean) if clean else None,
            "clean_alignment_coverage": len(clean) / len(clean_base) if clean_base else None,
            "clean_matched": len(clean), "clean_total": len(clean_base),
            "dirty_change_rate": sum(a.value != b.value for a, b in dirty) / len(dirty) if dirty else None,
            "added": len(aligned["added"]), "removed": len(aligned["removed"]),
            "to_all": lcs_overlap(base.token_ids, changed.token_ids),
            "to_clean": lcs_overlap(token_region(base, [a for a, _ in clean]),
                                    token_region(changed, [b for _, b in clean]))}
