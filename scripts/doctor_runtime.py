#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from contract_utils import find_contract, load_json


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check a multi-agent runtime contract for routing drift and architectural fragility."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        help="Path to runtime_contract.json. If omitted, search from cwd upward.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    return parser.parse_args()


class RuntimeDoctor:
    def __init__(self, contract_path: Path):
        self.contract_path = contract_path
        self.contract = load_json(contract_path)
        self.results: list[CheckResult] = []
        self.runtime_agents = self.contract.get("runtime", {}).get("agents", [])
        self.account_owner = {
            str(agent.get("requiredAccountId")): str(agent.get("runtimeId"))
            for agent in self.runtime_agents
            if agent.get("requiredAccountId")
        }

    def ok(self, name: str, detail: str) -> None:
        self.results.append(CheckResult(name=name, status="ok", detail=detail))

    def warn(self, name: str, detail: str) -> None:
        self.results.append(CheckResult(name=name, status="warn", detail=detail))

    def error(self, name: str, detail: str) -> None:
        self.results.append(CheckResult(name=name, status="error", detail=detail))

    def check_path_exists(self, name: str, path: Path) -> bool:
        if path.exists():
            self.ok(name, f"exists: {path}")
            return True
        self.error(name, f"missing: {path}")
        return False

    def run(self) -> list[CheckResult]:
        self.check_contract()
        self.check_registry()
        self.check_shared_dirs()
        self.check_root_symlinks()
        self.check_secrets_pointer()
        self.check_runtime_config()
        self.check_thread_bindings()
        return self.results

    def check_contract(self) -> None:
        self.ok("contract", f"loaded: {self.contract_path}")

    def check_registry(self) -> None:
        registry = self.contract.get("registry", {})
        canonical_path = Path(registry["canonical"])
        if not self.check_path_exists("registry canonical", canonical_path):
            return

        canonical = load_json(canonical_path)
        expected_agents = {
            str(agent["registryId"]): str(agent["workspace"])
            for agent in self.runtime_agents
        }
        actual_agents = {
            str(agent["id"]): str(agent["workspace"])
            for agent in canonical.get("agents", [])
        }

        if actual_agents == expected_agents:
            self.ok("registry mapping", "canonical registry matches runtime contract")
        else:
            self.error(
                "registry mapping",
                f"expected {expected_agents}, got {actual_agents}",
            )

        for mirror_path_str in registry.get("mirrors", []):
            mirror_path = Path(mirror_path_str)
            if not mirror_path.exists():
                self.error("registry mirror", f"missing mirror: {mirror_path}")
                continue

            mirror = load_json(mirror_path)
            if mirror == canonical:
                self.ok("registry mirror", f"in sync: {mirror_path}")
            else:
                self.error("registry mirror", f"drift detected: {mirror_path}")

    def check_shared_dirs(self) -> None:
        for path_str in self.contract.get("shared", {}).get("requiredDirectories", []):
            path = Path(path_str)
            if path.is_dir():
                self.ok("shared dir", f"ready: {path}")
            else:
                self.error("shared dir", f"missing directory: {path}")

    def check_root_symlinks(self) -> None:
        for link_str, target_str in self.contract.get("rootCompatibilitySymlinks", {}).items():
            link = Path(link_str)
            target = Path(target_str)
            if not link.exists():
                self.error("root symlink", f"missing: {link}")
                continue
            if not link.is_symlink():
                self.error("root symlink", f"not a symlink: {link}")
                continue
            resolved = link.resolve()
            if resolved == target:
                self.ok("root symlink", f"{link} -> {resolved}")
            else:
                self.error("root symlink", f"{link} -> {resolved}, expected {target}")

    def check_secrets_pointer(self) -> None:
        secrets = self.contract.get("secrets")
        if not secrets:
            self.warn("secrets pointer", "no secrets section in contract")
            return

        pointer = Path(secrets["pointer"])
        target = Path(secrets["target"])
        if not pointer.exists():
            self.error("secrets pointer", f"missing: {pointer}")
            return
        if not pointer.is_symlink():
            self.error("secrets pointer", f"not a symlink: {pointer}")
            return
        resolved = pointer.resolve()
        if resolved == target:
            self.ok("secrets pointer", f"{pointer} -> {resolved}")
        else:
            self.error("secrets pointer", f"{pointer} -> {resolved}, expected {target}")

    def check_runtime_config(self) -> None:
        runtime = self.contract.get("runtime", {})
        config_path = Path(runtime["config"])
        if not self.check_path_exists("runtime config", config_path):
            return

        config = load_json(config_path)
        defaults_workspace = config.get("agents", {}).get("defaults", {}).get("workspace")
        expected_workspace = runtime.get("defaults", {}).get("workspace")
        if expected_workspace is not None:
            if defaults_workspace == expected_workspace:
                self.ok("runtime default workspace", str(expected_workspace))
            else:
                self.error(
                    "runtime default workspace",
                    f"expected {expected_workspace}, got {defaults_workspace}",
                )

        actual_runtime_agents = {
            str(agent["id"]): agent
            for agent in config.get("agents", {}).get("list", [])
        }
        for expected in self.runtime_agents:
            runtime_id = str(expected["runtimeId"])
            actual = actual_runtime_agents.get(runtime_id)
            if actual is None:
                self.error("runtime agent", f"missing runtime agent: {runtime_id}")
                continue

            expected_workspace = str(expected["workspace"])
            actual_workspace = actual.get("workspace")
            if actual_workspace != expected_workspace:
                self.error(
                    "runtime agent",
                    f"{runtime_id} workspace expected {expected_workspace}, got {actual_workspace}",
                )
            else:
                self.ok("runtime agent", f"{runtime_id} workspace is correct")

            if "default" in expected:
                actual_default = bool(actual.get("default", False))
                expected_default = bool(expected.get("default", False))
                if actual_default != expected_default:
                    self.error(
                        "runtime agent default",
                        f"{runtime_id} default expected {expected_default}, got {actual_default}",
                    )
                else:
                    self.ok("runtime agent default", f"{runtime_id} default flag is correct")

        bindings = config.get("bindings", [])
        normalized_bindings = [
            {
                "channel": binding.get("match", {}).get("channel"),
                "accountId": binding.get("match", {}).get("accountId"),
                "agentId": binding.get("agentId"),
            }
            for binding in bindings
        ]

        for required in runtime.get("requiredBindings", []):
            if required in normalized_bindings:
                self.ok(
                    "runtime binding",
                    f"required binding present: {required['accountId']} -> {required['agentId']}",
                )
            else:
                self.error(
                    "runtime binding",
                    f"missing required binding: {required['accountId']} -> {required['agentId']}",
                )

        for forbidden in runtime.get("forbiddenBindings", []):
            if forbidden in normalized_bindings:
                self.error(
                    "runtime binding",
                    f"forbidden binding present: {forbidden['accountId']} -> {forbidden['agentId']}",
                )
            else:
                self.ok(
                    "runtime binding",
                    f"forbidden binding absent: {forbidden['accountId']} -> {forbidden['agentId']}",
                )

        for expected in self.runtime_agents:
            self.check_session_routing(expected)

    def check_session_routing(self, agent_contract: dict[str, object]) -> None:
        session_path = Path(str(agent_contract["sessionFile"]))
        runtime_id = str(agent_contract["runtimeId"])
        required_account = str(agent_contract["requiredAccountId"])
        if not session_path.exists():
            self.warn("session routing", f"session file missing for {runtime_id}: {session_path}")
            return

        sessions = load_json(session_path)
        session_key = f"agent:{runtime_id}:main"
        session_entry = sessions.get(session_key)
        if session_entry is None:
            self.warn("session routing", f"primary session not yet created for {runtime_id}")
        else:
            actual_account = (
                session_entry.get("deliveryContext", {}).get("accountId")
                or session_entry.get("origin", {}).get("accountId")
            )
            if actual_account == required_account:
                self.ok(
                    "session routing",
                    f"{session_key} uses accountId={required_account}",
                )
            else:
                self.error(
                    "session routing",
                    f"{session_key} expected accountId={required_account}, got {actual_account}",
                )

        for key, value in sessions.items():
            actual_account = (
                value.get("deliveryContext", {}).get("accountId")
                or value.get("origin", {}).get("accountId")
            )
            if actual_account in self.account_owner:
                expected_runtime = self.account_owner[actual_account]
                if expected_runtime != runtime_id:
                    self.error(
                        "session contamination",
                        f"{key} in {session_path} is bound to accountId={actual_account}, "
                        f"which belongs to runtimeId={expected_runtime}",
                    )

    def check_thread_bindings(self) -> None:
        pattern = self.contract.get("runtime", {}).get("threadBindingGlob")
        if not pattern:
            self.warn("thread bindings", "no threadBindingGlob configured")
            return

        matches = sorted(glob.glob(pattern))
        if matches:
            self.warn(
                "telegram thread bindings",
                "suspicious files present: " + ", ".join(matches),
            )
        else:
            self.ok("telegram thread bindings", "no thread-binding files detected")


def render_text(results: list[CheckResult]) -> str:
    lines = []
    for result in results:
        prefix = {
            "ok": "[OK]",
            "warn": "[WARN]",
            "error": "[ERROR]",
        }[result.status]
        lines.append(f"{prefix} {result.name}: {result.detail}")

    ok_count = sum(1 for result in results if result.status == "ok")
    warn_count = sum(1 for result in results if result.status == "warn")
    error_count = sum(1 for result in results if result.status == "error")
    lines.append("")
    lines.append(
        f"Summary: {ok_count} ok, {warn_count} warning(s), {error_count} error(s)"
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    contract_path = find_contract(args.contract)
    doctor = RuntimeDoctor(contract_path)
    results = doctor.run()
    summary = {
        "contract": str(contract_path),
        "results": [asdict(result) for result in results],
        "counts": {
            "ok": sum(1 for result in results if result.status == "ok"),
            "warn": sum(1 for result in results if result.status == "warn"),
            "error": sum(1 for result in results if result.status == "error"),
        },
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_text(results))

    return 1 if summary["counts"]["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
