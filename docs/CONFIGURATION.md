# Configuration Reference

This document explains the `agentic.bake.yaml` schema used by Agentic Template Kit.

## Mental model

```text
target   = named bake preset, for example default, codex, gitlab, all
platform = destination agentic system, for example codex or github-copilot
profile  = behavior/policy package passed into templates
skill    = reusable capability bundle rendered as SKILL.md where supported
flow     = multi-step process guidance, mainly for GitLab Duo style workflows
```

## Minimal file

```yaml
version: "1"

targets:
  codex:
    platforms:
      - codex
    skills:
      - cost-based-planner
      - safe-implementer
```

## Full example

```yaml
version: "1"

variables:
  project_name: CoachIQ
  owner_team: platform-engineering
  default_language: de
  governance_level: strict

targets:
  codex:
    description: Codex AGENTS.md and skill setup
    platforms:
      - codex
    profiles:
      - base
      - devsecops
    skills:
      - cost-based-planner
      - safe-implementer
      - verification-reviewer
      - security-reviewer
      - documentation-maintainer

  gitlab:
    description: GitLab Duo Agent Platform setup
    platforms:
      - gitlab-duo
    profiles:
      - base
      - gitlab-governance
      - devsecops
    flows:
      - secure-code-change
      - documentation-review
      - ci-cd-review

  local-ai:
    description: Local Ollama-based setup
    platforms:
      - opencode
      - openhands
    profiles:
      - base
      - local-models
    model:
      provider: ollama
      default_model: qwen2.5-coder:7b
      base_url: http://localhost:11434

  default:
    inherits:
      - codex

  all:
    inherits:
      - codex
      - gitlab
      - local-ai
```

## Top-level schema

| Field | Type | Required | Description |
|---|---:|---:|---|
| `version` | string | yes | Schema version. Currently only `"1"`. |
| `variables` | object | no | Global template variables. |
| `targets` | object | yes | Map of target names to configurations. |

## Target schema

| Field | Type | Required | Description |
|---|---:|---:|---|
| `description` | string | no | Human-readable description. |
| `inherits` | list[string] | no | Parent targets merged before the current target. |
| `platforms` | list[string] | no | Platform adapters to render. |
| `profiles` | list[string] | no | Behavior labels passed to templates. |
| `skills` | list[string] | no | Skill bundles to render where supported. |
| `flows` | list[string] | no | Flow files to render where supported. |
| `model` | object | no | Model defaults for generated guidance. |
| `rules` | object | no | Open-ended policy flags. |
| `variables` | object | no | Target-specific template variables. |

## Supported platforms

| Platform | Main output |
|---|---|
| `codex` | `AGENTS.md`, `.agents/skills/...` |
| `gitlab-duo` | `AGENTS.md`, `.gitlab/duo/...` |
| `github-copilot` | `.github/copilot-instructions.md`, `.github/prompts/...` |
| `openhands` | `AGENTS.md`, `.openhands/instructions.md` |
| `opencode` | `AGENTS.md`, `.opencode/instructions.md` |
| `generic` | portable `.skills/.../SKILL.md` |

## Model schema

| Field | Type | Example |
|---|---:|---|
| `provider` | string | `ollama` |
| `default_model` | string | `qwen2.5-coder:7b` |
| `base_url` | string | `http://localhost:11434` |

## Rules

`rules` can contain team-specific governance flags.

Example:

```yaml
rules:
  no_direct_push: true
  require_tests: true
  require_security_review: true
  forbid_secret_files: true
  require_merge_request: true
```

The core schema does not restrict rule names. Templates decide how to render them.

## Inheritance behavior

Child targets inherit parent targets listed in `inherits`.

Merge behavior:

- `platforms`, `profiles`, `skills`, `flows`: appended and de-duplicated while preserving order.
- `rules`: merged, child overrides parent.
- `variables`: merged, child overrides parent.
- `model`: child replaces parent if defined.
- `description`: child replaces parent if defined.

Cycles are invalid:

```yaml
targets:
  a:
    inherits: [b]
  b:
    inherits: [a]
```

## Target naming recommendations

Use explicit platform targets:

```yaml
targets:
  codex:
    platforms: [codex]
  copilot:
    platforms: [github-copilot]
  gitlab:
    platforms: [gitlab-duo]
```

Use aggregate targets for common combinations:

```yaml
targets:
  default:
    inherits: [codex, copilot]
  all:
    inherits: [codex, copilot, gitlab, local-ai]
```

This is easier to understand than placing every platform directly into `default`.
