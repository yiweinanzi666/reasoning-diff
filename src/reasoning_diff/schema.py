"""Versioned, JSON-serializable contracts shared by all experiment stages."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fractions import Fraction
from typing import Any
import math

SCHEMA_VERSION = 1
SPLITS = ("train", "dev", "direction", "calibration", "transfer", "test")


def canonical_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    text = str(value).strip()
    try:
        return str(Fraction(text.replace(",", "")))
    except (ValueError, ZeroDivisionError):
        return " ".join(text.casefold().split())


@dataclass
class Premise:
    id: str
    text: str
    start: int
    end: int
    value: str | None = None
    kind: str = "fact"


@dataclass
class Node:
    id: str
    parents: list[str]
    value: str
    aliases: list[str] = field(default_factory=list)
    expression: str = ""
    scope: str = "global"


@dataclass
class Task:
    id: str
    base_id: str
    family: str
    prompt: str
    premises: list[Premise]
    nodes: list[Node]
    target: str | None
    answer: str
    answer_type: str = "numeric"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.id or not self.base_id or not self.prompt:
            raise ValueError("Task id, base_id and prompt must be nonempty")
        ids = [p.id for p in self.premises] + [n.id for n in self.nodes]
        if len(set(ids)) != len(ids):
            raise ValueError("Premise/node IDs must be unique")
        if not self.premises:
            raise ValueError("Task requires at least one premise")
        for p in self.premises:
            if not 0 <= p.start < p.end <= len(self.prompt) or self.prompt[p.start:p.end] != p.text:
                raise ValueError(f"Premise span mismatch: {p.id}")
        known = {p.id for p in self.premises}
        for n in self.nodes:
            if not n.parents or not set(n.parents) <= known:
                raise ValueError(f"Node {n.id} must reference earlier nodes/premises (acyclic DAG)")
            if len(n.parents) != len(set(n.parents)):
                raise ValueError(f"Repeated dependency in {n.id}")
            known.add(n.id)
        if self.target is not None and self.target not in {n.id for n in self.nodes}:
            raise ValueError("Target must be a task node")

    def ancestors(self) -> dict[str, set[str]]:
        self.validate()
        result = {p.id: {p.id} for p in self.premises}
        for n in self.nodes:
            result[n.id] = set().union(*(result[parent] for parent in n.parents))
        return {n.id: result[n.id] for n in self.nodes}

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        obj = cls(**{**data, "premises": [Premise(**p) for p in data["premises"]],
                     "nodes": [Node(**n) for n in data["nodes"]]})
        obj.validate()
        return obj


@dataclass(frozen=True)
class EventIdentity:
    node_id: str
    expression: str
    occurrence: int
    scope: str = "global"

    def key(self) -> str:
        import json
        return json.dumps(asdict(self), sort_keys=True, ensure_ascii=False)


@dataclass
class Event:
    identity: EventIdentity
    value: str
    start: int
    end: int
    value_start: int
    text: str
    task_parents: list[str] | None = None
    correct: bool | None = None
    source: str = "parser"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Event:
        return cls(**{**data, "identity": EventIdentity(**data["identity"])})


@dataclass
class Cost:
    prefill_tokens: int = 0
    decode_tokens: int = 0
    elapsed_seconds: float = 0.0
    probe_seconds: float = 0.0
    scheduling_seconds: float = 0.0

    def __add__(self, other: Cost) -> Cost:
        return Cost(**{key: getattr(self, key) + getattr(other, key) for key in asdict(self)})


@dataclass
class Trace:
    id: str
    task_id: str
    base_id: str
    model: str
    seed: int
    text: str
    token_ids: list[int]
    offsets: list[list[int]]
    events: list[Event]
    answer: str | None
    correct: bool | None
    status: str = "ok"
    cost: Cost = field(default_factory=Cost)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Trace:
        return cls(**{**data, "events": [Event.from_dict(e) for e in data["events"]],
                     "cost": Cost(**data["cost"])})


@dataclass
class Edit:
    id: str
    base_task_id: str
    premise_id: str
    task: Task
    kind: str = "value"
    exhaustive: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Edit:
        return cls(**{**data, "task": Task.from_dict(data["task"])})


def finite_or_none(value: float | None) -> float | None:
    return value if value is not None and math.isfinite(value) else None
