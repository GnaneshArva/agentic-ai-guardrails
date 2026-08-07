# agentic-ai-guardrails Handbook

## Universal Rules
- **Git Push Approval Rule**: NEVER run `git push` automatically. Always present implemented changes and unit test verification results, and wait for explicit user confirmation before executing any `git push` command.
- **Python Virtualenv Path**: All unit tests must be executed using:
  `/Users/gnanesh_arva/Downloads/travel-planner-v2/travel-agent-service/.venv/bin/pytest`

## Repository Standards
- **Port**: `8004` (Default)
- **Role**: Input/output security guardrails, prompt injection detection, PII masking, secret detection, unicode normalization, coherence validation, and HITL risk assessment.

## Relevant Task Playbooks (`skills/`)
- `hitl-approval-workflow`: Human-in-the-Loop risk assessment and approval state resolution.
