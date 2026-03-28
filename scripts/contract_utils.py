#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path


CANDIDATE_RELATIVE_PATHS = (
    Path("shared/config/runtime_contract.json"),
    Path("config/runtime_contract.json"),
    Path(".runtime/runtime_contract.json"),
    Path("runtime_contract.json"),
)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def find_contract(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()

    env_path = os.environ.get("OPENCLAW_RUNTIME_CONTRACT")
    if env_path:
        return Path(env_path).expanduser().resolve()

    start = Path.cwd().resolve()
    for base in (start, *start.parents):
        for relative in CANDIDATE_RELATIVE_PATHS:
            candidate = base / relative
            if candidate.exists():
                return candidate.resolve()

    candidates = ", ".join(str(path) for path in CANDIDATE_RELATIVE_PATHS)
    raise FileNotFoundError(
        "Could not find runtime_contract.json automatically. "
        f"Searched upward from {start} for: {candidates}. "
        "Pass --contract /absolute/path/to/runtime_contract.json."
    )
