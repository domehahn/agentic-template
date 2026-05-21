# Agentic Template Kit - DevSecOps SDLC Edition

Generate agentic configuration for Codex, GitLab Duo Agent Platform, GitHub Copilot, Claude Code, OpenHands, OpenCode, Ollama, and generic agentic systems.

This edition includes a full DevSecOps SDLC skill set and platform-specific render targets.

## Included SDLC Skills

### Planning and analysis

- `requirements-analyst`
- `cost-based-planner`
- `architecture-reviewer`
- `threat-modeler`

### Implementation and validation

- `safe-implementer`
- `test-strategy-engineer`
- `verification-reviewer`

### Security and governance

- `security-reviewer`
- `secrets-reviewer`
- `dependency-supply-chain-reviewer`
- `ci-cd-reviewer`
- `iac-gitops-reviewer`
- `compliance-governance-reviewer`

### Delivery and operations

- `release-readiness-reviewer`
- `observability-reviewer`
- `incident-postmortem-assistant`

### Knowledge and reuse

- `documentation-maintainer`
- `universal-skill-creator`

## Quickstart

Use this sequence for a clean first setup in any repository:

1. Install dependencies.
2. Initialize `agentic.bake.yaml`.
3. Preview generated files (`--plan`).
4. Write generated files (`--write`).
5. Validate project consistency.

```bash
uv sync
uv run agentic-template init --target /path/to/repo --project-name MyProject
uv run agentic-template bake default --target /path/to/repo --plan
uv run agentic-template bake default --target /path/to/repo --write
uv run agentic-template validate --target /path/to/repo
```

If `init` runs without `--platform` or `--preset`, it configures:

- `codex`
- `github-copilot`
- `claude`
- `gitlab-duo`
- `opencode`
- `openhands`
- `ollama`

## Command Overview

This section focuses on what each command is for and when to use it.

### `agentic-template init`

Creates a new `agentic.bake.yaml` in the target repository.

Use this command when:

- you onboard a new repository
- you want a fresh baseline configuration
- you want to switch to a different platform/preset setup and regenerate from a new bakefile

### `agentic-template list-targets`

Shows all available bake targets from `agentic.bake.yaml` in a table.

Use this command when:

- you need to understand which targets exist (`default`, `all`, platform-specific targets)
- you are unsure which target to pass to `bake`
- you want to inspect inherited target structure quickly

### `agentic-template bake`

Renders files for one target and either previews or writes them.

Use this command when:

- you want to preview upcoming changes (`--plan`)
- you want to materialize generated files in the repo (`--write`)
- your bakefile, skills, rules, or platform selection changed and outputs must be refreshed

Typical behavior:

- compares generated output to existing files
- compares planned output to `.agentic-template.lock` state (Terraform/OpenTofu-like)
- reports whether each file would be created, updated, or unchanged
- reports state actions (`create`, `update`, `delete`, `noop`) and a plan summary
- shows compact unified diffs for changed files in `--plan`
- supports `--detailed-diff` to print full diffs (without truncation)
- writes `.agentic-template.lock` when run with `--write`

### `agentic-template validate`

Checks whether generated/project state is valid and consistent.

Use this command when:

- you finished a bake and want a safety check
- you want CI to fail early on invalid configuration
- you changed `agentic.bake.yaml` manually and need a verification pass

## GitHub Copilot Example

```bash
uv run agentic-template init --target /path/to/repo --platform "github-copilot" --project-name MyProject
uv run agentic-template bake default --target /path/to/repo --write
```

Generated Copilot structure:

```text
AGENTS.md
.agentic/github-copilot/AGENTS.md
.github/copilot-instructions.md
.github/prompts/<skill-name>.prompt.md
.agentic-template.lock
```

Root `AGENTS.md` is a generated platform index. Platform-specific instruction files are written under `.agentic/<platform>/AGENTS.md`.

## Documentation

- `docs/CONFIGURATION.md`
- `docs/GITLAB_DUO.md`
- `docs/SDLC_SKILLS.md`
- `docs/USAGE.md`
- `docs/ARCHITECTURE.md`
