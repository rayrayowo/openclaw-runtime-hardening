---
name: openclaw-runtime-hardening
description: Diagnose and harden OpenClaw-style multi-agent runtimes when persistent agents bleed across chats, bindings rely on defaults, workspaces overlap, mirrors drift, or routing/session state becomes hard to trust.
license: MIT
---

# OpenClaw Runtime Hardening

## Overview

Use this skill when a multi-agent OpenClaw setup feels fragile: the wrong agent answers in the wrong chat, an agent is unsure which workspace it owns, dashboard rosters drift from runtime truth, or the architecture depends too heavily on implicit defaults.

The goal is not just to patch one bug. The goal is to leave behind machine-checkable guardrails.

## When To Use It

Trigger this skill when any of these happen:

- a persistent agent speaks in another agent's Telegram or chat surface
- routing depends on `default` fallback and feels brittle
- per-agent workspaces and shared files are mixed together
- `AGENTS.md`, dashboard JSON, and runtime config disagree
- session files look contaminated by the wrong account
- secrets pointers or root compatibility links keep drifting
- a user wants to turn an ad hoc agent setup into a robust, shareable architecture

## Core Workflow

### 1. Map the live architecture first

Identify:

- persistent agents vs temporary workflows/modes
- the canonical machine-readable registry
- runtime config and live bindings
- per-agent workspaces
- the shared layer
- session files and account mappings

If the ontology is messy, read `references/patterns.md` before making changes.

### 2. Choose machine truth sources

The default hardening pattern is:

- one canonical persistent-agent registry
- one runtime contract
- derived dashboard mirrors
- a runtime doctor script
- a mirror sync script

Do not keep multiple hand-maintained “truth” files if one machine-readable file can own the data.

### 3. Prefer explicit bindings over implicit identity

For every persistent agent:

- give it a dedicated runtime entry
- give it a dedicated workspace
- give it an explicit chat/account binding when possible

Treat default routing as fallback only, not as identity.

### 4. Separate shared and private layers

Keep:

- facts, scripts, logs, reports, and common config in a shared layer
- persona files, private memory, and internal workflow docs inside each agent workspace

Do not put one persistent agent inside another agent's conceptual world.

### 5. Install guardrails, not just fixes

Use the bundled tools to create or maintain:

- a `runtime_contract.json`
- a `doctor_runtime.py`
- a `sync_agent_registry.py`

Back up external runtime configs before editing them.

### 6. Verify before reasoning from chat history

Run the doctor first.

If runtime is healthy but the chat still feels strange, then inspect prompt, memory, or identity files.
Do not infer routing corruption from old chat history alone.

## Bundled Resources

- `scripts/doctor_runtime.py`
  Checks contract integrity, registry mirrors, shared dirs, root symlinks, secrets pointers, runtime bindings, session routing, and suspicious thread-binding files.
- `scripts/sync_agent_registry.py`
  Checks or repairs derived mirror files from the canonical registry.
- `assets/runtime_contract.template.json`
  Starter contract for a hardened multi-agent workspace.
- `references/patterns.md`
  Design heuristics, failure modes, and a minimal artifact set.

## Typical Deliverables

When you apply this skill well, you usually leave behind:

1. a canonical registry
2. a runtime contract
3. explicit bindings for persistent agents
4. a doctor script
5. a mirror sync script
6. updated docs that point to the machine truths
7. a verification run showing the current runtime is healthy

## Commands

If the workspace already has a contract:

```bash
python3 scripts/doctor_runtime.py
python3 scripts/sync_agent_registry.py --check
```

If the contract is elsewhere:

```bash
python3 scripts/doctor_runtime.py --contract /absolute/path/to/runtime_contract.json
python3 scripts/sync_agent_registry.py --contract /absolute/path/to/runtime_contract.json --check
```

## Sharing Rule

If the user wants a reusable package or GitHub-ready output:

- remove real secrets
- remove live bot tokens
- replace personal absolute paths with templates or placeholders
- keep the workflow and tools generic
