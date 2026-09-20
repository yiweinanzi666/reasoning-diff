"""Atomic artifacts, content hashes and strict JSON; no silent NaN serialization."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from typing import Iterable


def encode(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      default=lambda value: asdict(value) if is_dataclass(value) else _unsupported(value))


def _unsupported(value):
    raise TypeError(f"Not JSON serializable: {type(value).__name__}")


def digest(obj) -> str:
    return hashlib.sha256(encode(obj).encode("utf-8")).hexdigest()


def file_digest(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_text(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def write_json(path: str | Path, obj) -> None:
    atomic_text(path, encode(obj) + "\n")


def read_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_jsonl(path: str | Path, rows: Iterable) -> None:
    atomic_text(path, "".join(encode(row) + "\n" for row in rows))


def read_jsonl(path: str | Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def runtime_info() -> dict:
    import importlib.metadata
    versions = {}
    for name in ("reasoning-diff", "numpy", "scipy", "scikit-learn", "torch", "transformers"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    return {"python": sys.version, "platform": platform.platform(), "packages": versions,
            "git_revision": result.stdout.strip() if result.returncode == 0 else None}
