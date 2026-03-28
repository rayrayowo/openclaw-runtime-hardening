#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from contract_utils import dump_json, find_contract, load_json


def compare_json(a: object, b: object) -> bool:
    return a == b


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or sync derived registry mirrors from the canonical agent registry."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        help="Path to runtime_contract.json. If omitted, search from cwd upward.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--write",
        action="store_true",
        help="Overwrite mirror files with canonical registry content.",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Check whether mirror files match the canonical registry.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of plain text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract_path = find_contract(args.contract)
    contract = load_json(contract_path)
    registry_path = Path(contract["registry"]["canonical"])
    mirror_paths = [Path(path) for path in contract["registry"].get("mirrors", [])]

    canonical = load_json(registry_path)
    drift_paths: list[str] = []
    written_paths: list[str] = []

    for mirror_path in mirror_paths:
        if not mirror_path.exists():
            drift_paths.append(str(mirror_path))
            if args.write:
                mirror_path.parent.mkdir(parents=True, exist_ok=True)
                mirror_path.write_text(dump_json(canonical), encoding="utf-8")
                written_paths.append(str(mirror_path))
            continue

        mirror = load_json(mirror_path)
        if compare_json(canonical, mirror):
            continue

        drift_paths.append(str(mirror_path))
        if args.write:
            mirror_path.write_text(dump_json(canonical), encoding="utf-8")
            written_paths.append(str(mirror_path))

    status = "ok"
    exit_code = 0
    if drift_paths and not args.write:
        status = "drift"
        exit_code = 1
    elif written_paths:
        status = "synced"

    payload = {
        "status": status,
        "contract": str(contract_path),
        "canonical": str(registry_path),
        "mirrors": [str(path) for path in mirror_paths],
        "drift": drift_paths,
        "written": written_paths,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return exit_code

    if status == "ok":
        print("Registry mirrors are in sync.")
        print(f"Contract: {contract_path}")
        print(f"Canonical: {registry_path}")
        return 0

    if status == "synced":
        print("Registry mirrors were updated from canonical registry.")
        print(f"Contract: {contract_path}")
        for path in written_paths:
            print(f"- {path}")
        return 0

    print("Registry mirror drift detected.")
    print(f"Contract: {contract_path}")
    print(f"Canonical: {registry_path}")
    for path in drift_paths:
        print(f"- {path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
