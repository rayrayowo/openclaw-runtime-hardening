# Publishing Notes

## GitHub

- Repository: `rayrayowo/openclaw-runtime-hardening`
- Recommended visibility: public
- Recommended topics:
  - `openclaw`
  - `ai-agents`
  - `multi-agent`
  - `agent-runtime`
  - `diagnostics`
  - `developer-tools`
  - `skills`

## ClawHub

- Slug: `openclaw-runtime-hardening`
- Name: `OpenClaw Runtime Hardening`
- Version: `1.0.0`

Suggested changelog:

```text
Initial public release: adds a reusable runtime hardening skill with a runtime contract template, doctor script, registry mirror sync script, and architecture patterns for stabilizing multi-agent OpenClaw setups.
```

Suggested publish command:

```bash
clawhub login
clawhub publish . \
  --slug openclaw-runtime-hardening \
  --name "OpenClaw Runtime Hardening" \
  --version 1.0.0 \
  --changelog "Initial public release: adds a reusable runtime hardening skill with a runtime contract template, doctor script, registry mirror sync script, and architecture patterns for stabilizing multi-agent OpenClaw setups."
```

## Release Checklist

1. Confirm the package contains no real secrets or bot tokens.
2. Confirm placeholder paths remain generic.
3. Run `python3 /Users/rayzhang/.codex/skills/.system/skill-creator/scripts/quick_validate.py .`
4. Run `python3 scripts/doctor_runtime.py --contract /absolute/path/to/runtime_contract.json` against a real workspace.
5. Push the current GitHub commit before publishing to ClawHub.
