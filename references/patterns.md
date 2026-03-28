# Runtime Hardening Patterns

## 1. Common Failure Modes

### Wrong agent in the wrong chat

Usually caused by one of these:

- only one agent has an explicit binding
- another agent relies on default fallback
- session files were previously polluted by the wrong account
- thread-binding files point a chat at the wrong runtime

### Agent is unsure who it is

Usually caused by:

- runtime is healthy, but identity files are incomplete
- old chat history is being mistaken for live routing truth
- the architecture still mixes persistent agents with workflow modes

### Dashboard and runtime disagree

Usually caused by:

- multiple hand-maintained rosters
- missing mirror sync tooling
- docs being used as config databases

## 2. Strong Default Pattern

The most robust pattern is:

1. one canonical persistent-agent registry
2. one runtime contract
3. one doctor script
4. one mirror sync script
5. explicit chat bindings for every persistent agent
6. shared layer separated from private agent workspaces

## 3. Persistent Agents vs Workflows

Persistent agents should have:

- their own workspace
- their own memory/identity files
- their own runtime entry
- their own chat/account binding when practical

Workflows and modes should not pretend to be souls.
Research, review, build, and test are usually execution modes, not independent long-term beings.

## 4. Shared vs Private Layers

Shared layer:

- config
- scripts
- knowledge base facts
- logs
- reports

Private layer:

- AGENTS.md
- MEMORY.md
- SOUL.md
- IDENTITY.md
- private workflow docs

Do not use one agent's private workflow as another agent's internal operating system.

## 5. What To Trust First

When something feels wrong, trust in this order:

1. machine-checked runtime doctor
2. runtime config
3. session/account mappings
4. identity and memory content
5. old chat history

Old chat history is often evidence, but it is not always the current truth.

## 6. Minimal Artifact Set

If you want a setup to stay stable over time, aim for this minimum:

1. `agents/agents.json` or equivalent canonical roster
2. `runtime_contract.json`
3. `doctor_runtime.py`
4. `sync_agent_registry.py`
5. core docs pointing to those machine truth sources

## 7. Sharing Checklist

Before publishing or open-sourcing:

- remove live bot tokens
- remove real secrets
- replace personal paths with placeholders
- keep examples generic
- include a template contract, not a live private config
