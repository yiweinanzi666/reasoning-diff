"""All variants, models and editing rounds share their base problem's split."""
from __future__ import annotations

import hashlib
from .schema import SPLITS

DEFAULT_FRACTIONS = (0.40, 0.15, 0.10, 0.10, 0.10, 0.15)


def assign_split(base_id: str, seed: int = 0, fractions=DEFAULT_FRACTIONS) -> str:
    if len(fractions) != len(SPLITS) or any(v <= 0 for v in fractions) or abs(sum(fractions) - 1) > 1e-9:
        raise ValueError("Require six positive split fractions summing to 1")
    value = int.from_bytes(hashlib.sha256(f"{seed}:{base_id}".encode()).digest()[:8], "big") / 2**64
    cumulative = 0.0
    for split, fraction in zip(SPLITS, fractions, strict=True):
        cumulative += fraction
        if value < cumulative:
            return split
    return SPLITS[-1]


def assert_disjoint(groups: dict[str, set[str]]) -> None:
    seen = set()
    for name, ids in groups.items():
        overlap = seen & ids
        if overlap:
            raise ValueError(f"Base-problem leakage into {name}: {sorted(overlap)[:5]}")
        seen |= ids


def require_split(split: str, allowed: tuple[str, ...], operation: str) -> None:
    if split not in allowed:
        raise ValueError(f"{operation} cannot fit on {split}; expected {allowed}")
