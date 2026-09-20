"""Conservative event extraction; ambiguous/unparsed text stays unlabelled.

Math assignments are recognized from predeclared aliases, never by matching output
values. Natural language and code datasets can supply independently reviewed spans.
"""
from __future__ import annotations

from collections import Counter
import re
from .schema import Event, EventIdentity, Task, canonical_value

NUMBER = r"[+-]?(?:\d[\d,]*(?:\.\d+)?(?:\s*/\s*[+-]?\d+)?|\.\d+)"


def parse_events(text: str, task: Task) -> list[Event]:
    aliases = [(alias, node) for node in task.nodes for alias in (node.aliases or [node.id])]
    counts = Counter(alias.casefold() for alias, _ in aliases)
    found = []
    for alias, node in aliases:
        if counts[alias.casefold()] != 1:
            continue
        value_pattern = NUMBER if task.answer_type == "numeric" else r"[^\n.;]+"
        pattern = re.compile(rf"(?<!\w){re.escape(alias)}\s*(?:=|:|equals?|is|are)\s*\$?"
                             rf"(?P<value>{value_pattern})", re.IGNORECASE)
        for match in pattern.finditer(text):
            start = text.rfind("\n", 0, match.start()) + 1
            # A line containing multiple assignments has no unambiguous step boundary.
            found.append((start, match.end(), match.start("value"), node, match.group("value")))
    found.sort(key=lambda item: (item[0], item[1]))
    line_counts = Counter(item[0] for item in found)
    occurrences: Counter = Counter()
    ancestors = task.ancestors()
    events = []
    for start, end, value_start, node, value in found:
        if line_counts[start] != 1:
            continue
        key = (node.id, node.expression, node.scope)
        occurrences[key] += 1
        events.append(Event(EventIdentity(*key[:2], occurrences[key], key[2]), canonical_value(value),
                            start, end, value_start, text[start:end], sorted(ancestors[node.id]),
                            canonical_value(value) == canonical_value(node.value)))
    return events


def annotated_events(text: str, task: Task, annotations: list[dict]) -> list[Event]:
    result = []
    nodes = {n.id: n for n in task.nodes}
    ancestors = task.ancestors()
    keys = set()
    for row in annotations:
        identity = EventIdentity(row["node_id"], row["expression"], int(row["occurrence"]),
                                 row.get("scope", "global"))
        if identity.key() in keys or identity.occurrence < 1:
            raise ValueError("Duplicate/invalid annotated event identity")
        keys.add(identity.key())
        start, end, value_start = (int(row[k]) for k in ("start", "end", "value_start"))
        if not 0 <= start <= value_start < end <= len(text):
            raise ValueError("Invalid annotation character spans")
        if "text" in row and row["text"] != text[start:end]:
            raise ValueError("Annotation does not match original trace")
        node = nodes.get(identity.node_id)
        value = canonical_value(row["value"])
        result.append(Event(identity, value, start, end, value_start, text[start:end],
                            sorted(ancestors[node.id]) if node else None,
                            value == canonical_value(node.value) if node else None, "human"))
    return sorted(result, key=lambda event: event.start)


def align_events(base: list[Event], changed: list[Event]) -> dict:
    left = {e.identity.key(): e for e in base}
    right = {e.identity.key(): e for e in changed}
    if len(left) != len(base) or len(right) != len(changed):
        raise ValueError("Duplicate event identities cannot be aligned")
    shared = left.keys() & right.keys()
    return {"pairs": [(left[key], right[key]) for key in sorted(shared)],
            "removed": sorted(left.keys() - shared), "added": sorted(right.keys() - shared)}


def boundary_index(offsets: list[list[int]], character: int, position: str = "before") -> int | None:
    """Last token fully before a boundary. Never include a straddling token.

    For before/value positions the caller must truncate/replay at this index.
    It may precede a few characters of the target when a BPE token crosses it.
    None means the prompt's final token (no output prefix).
    """
    if position not in ("before", "value", "end"):
        raise ValueError("Unknown boundary position")
    candidates = [i for i, (a, b) in enumerate(offsets) if a < b and b <= character]
    return candidates[-1] if candidates else None


def extract_answer(text: str, answer_type: str) -> str | None:
    if answer_type == "code":
        matches = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
        return matches[-1].strip() if matches else text.strip() or None
    matches = re.findall(r"\\boxed\{([^{}]+)\}", text)
    if matches:
        return canonical_value(matches[-1])
    matches = re.findall(r"(?:final\s+answer|answer|####)\s*(?:is|:|=)?\s*([^\n]+)", text, re.IGNORECASE)
    if not matches:
        return None
    answer = matches[-1].strip().rstrip(".")
    if answer_type == "numeric":
        match = re.fullmatch(rf"\$?({NUMBER})", answer)
        return canonical_value(match.group(1)) if match else None
    return canonical_value(answer)
