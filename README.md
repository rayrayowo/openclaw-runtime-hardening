# OpenClaw Runtime Hardening

An OpenClaw skill for diagnosing and hardening multi-agent runtime architecture.

It is designed for setups where persistent agents have separate identities, workspaces, and chat surfaces, but the runtime layer can still drift over time.

## What Problems It Solves

Use this skill when:

- the wrong agent answers in the wrong chat
- one agent relies too heavily on `default` fallback routing
- dashboard agent rosters drift from runtime truth
- session files get contaminated by the wrong account
- workspaces and shared layers are not clearly separated
- the system feels fragile even after one-off fixes

The goal is to leave behind machine-checkable guardrails, not just patch one symptom.

## What The Skill Encourages

- one canonical machine-readable agent registry
- one runtime contract
- explicit bindings for persistent agents
- a runtime doctor script
- a registry mirror sync script
- a clear split between shared infrastructure and private agent state

## Included Files

- `SKILL.md`
  Core instructions for applying the hardening workflow.
- `agents/openai.yaml`
  UI metadata for OpenClaw-compatible skill surfaces.
- `scripts/doctor_runtime.py`
  Checks routing, bindings, session/account mapping, symlinks, secrets pointers, and registry drift against a runtime contract.
- `scripts/sync_agent_registry.py`
  Checks or repairs derived registry mirrors from the canonical registry.
- `scripts/contract_utils.py`
  Shared contract loading and discovery helpers.
- `references/patterns.md`
  Common failure modes and design heuristics.
- `assets/runtime_contract.template.json`
  Starter template for a hardened multi-agent runtime contract.

## Installation

Clone or copy the folder into your OpenClaw skills directory, or install it through your own distribution flow.

Example local use:

```bash
cp -R openclaw-runtime-hardening ~/.codex/skills/
```

## Usage

If your workspace already has a `runtime_contract.json`:

```bash
python3 scripts/doctor_runtime.py
python3 scripts/sync_agent_registry.py --check
```

If the contract lives elsewhere:

```bash
python3 scripts/doctor_runtime.py --contract /absolute/path/to/runtime_contract.json
python3 scripts/sync_agent_registry.py --contract /absolute/path/to/runtime_contract.json --check
```

## Recommended Architecture Pattern

This skill works best when your system follows this shape:

1. Persistent agents have their own workspaces, identities, and explicit bindings.
2. Shared facts, scripts, logs, and reports live in a shared layer.
3. Temporary workflows remain workflows, not fake long-term personalities.
4. Runtime truth is enforced by code, not only by markdown.

## Sharing / Open Source Notes

Before publishing your own runtime package:

- remove real secrets
- remove live bot tokens
- replace personal absolute paths with placeholders
- keep examples generic
- publish a template contract, not your live private config

## License

MIT
