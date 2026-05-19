# Agentic Template Kit

`agentic-template-kit` is a production-oriented Python CLI for generating agentic configuration files, instructions, and skill bundles across multiple coding-assistant platforms.

It follows a **Docker Bake-like model**:

- Define reusable targets in `agentic.bake.yaml`.
- Render platform-specific outputs from versioned templates.
- Apply the same setup to many repositories without copy & paste.
- Use dry-runs, diffs, validation, and a lockfile for controlled updates.

Supported platform adapters:

| Platform | Generated artifacts |
|---|---|
| Codex | `AGENTS.md`, `.agents/skills/<skill>/SKILL.md` |
| GitLab Duo | `AGENTS.md`, `.gitlab/duo/custom-rules.md`, `.gitlab/duo/flows/*.md` |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/prompts/*.prompt.md` |
| OpenHands | `AGENTS.md`, `.openhands/instructions.md` |
| OpenCode | `AGENTS.md`, `.opencode/instructions.md` |
| Generic | portable `SKILL.md` bundles |

## Installation

From the project root:

```bash
uv tool install .
```

For local development:

```bash
uv sync --extra dev
uv run agentic-template --help
```

## Quickstart

Create a bake file in your target repository:

```bash
agentic-template init --target /path/to/repo
```

Preview changes:

```bash
agentic-template bake default --target /path/to/repo --dry-run
```

Write changes:

```bash
agentic-template bake default --target /path/to/repo --write
```

Validate generated files:

```bash
agentic-template validate --target /path/to/repo
```

Show targets:

```bash
agentic-template list-targets --file /path/to/repo/agentic.bake.yaml
```

## Example `agentic.bake.yaml`

```yaml
version: "1"

variables:
  project_name: CoachIQ
  owner_team: platform-engineering
  default_language: de
  governance_level: strict

targets:
  default:
    description: Standard local setup
    platforms:
      - codex
      - github-copilot
      - opencode
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
    description: GitLab Duo setup
    platforms:
      - gitlab-duo
    profiles:
      - base
      - gitlab-governance
      - devsecops
    flows:
      - secure-code-change
      - documentation-review

  local-ai:
    description: Local model setup
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

  all:
    description: Everything
    inherits:
      - default
      - gitlab
      - local-ai
```

## Safety model

The CLI is safe by default:

- `bake` does not write unless `--write` is set.
- Existing unmanaged files are not overwritten unless `--force` is set.
- A `.agentic-template.lock` file records managed files, checksums, targets, platforms, and template-pack version.
- `diff` and `dry-run` show planned changes before write.
- `validate` checks expected structures and core metadata.

## Typical workflow

```bash
agentic-template init --target .
agentic-template bake devsecops --target . --dry-run
agentic-template bake devsecops --target . --write
agentic-template validate --target .
git diff
```

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Notes

This project intentionally separates:

- **Templates**: reusable platform-specific text assets.
- **Bake file**: project-specific target selection.
- **CLI**: reproducible renderer and lockfile manager.
- **Generated files**: committed into target repositories as normal agentic configuration.
