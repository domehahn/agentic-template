# Agentic Template Kit

`agentic-template-kit` is a production-oriented Python CLI for generating agentic configuration files, instructions, and skill bundles across multiple coding-assistant platforms.

It follows a **Docker Bake-like model** for agentic configuration:

- Define reusable targets in `agentic.bake.yaml`.
- Select one or more target platforms per target.
- Render platform-specific outputs from versioned templates.
- Apply the same setup to many repositories without copy and paste.
- Use dry-runs, diffs, validation, conflict detection, and a lockfile for controlled updates.

## Why this exists

Most agentic coding tools use different instruction files and different conventions:

- Codex uses `AGENTS.md` and `.agents/skills/...`.
- GitHub Copilot uses `.github/copilot-instructions.md` and prompt files.
- GitLab Duo Agent Platform uses repository instructions, custom rules, and flow-like guidance.
- OpenHands and OpenCode can use repository-level instruction files.
- Generic agents often understand portable `SKILL.md` bundles.

Without a generator, every project tends to get copied instructions that drift over time. This tool treats agentic configuration as generated, versioned, reproducible project infrastructure.

## Core concepts

### Target

A **target** is a named bake preset. It answers:

> What agentic setup should be rendered for this repository?

Examples:

- `codex`
- `copilot`
- `gitlab`
- `local-ai`
- `devsecops`
- `documentation`
- `default`
- `all`

A target can include one or more platforms, profiles, skills, flows, rules, variables, and model settings.

### Platform

A **platform** is the destination agentic system for which files are generated.

Supported platform adapters:

| Platform key | Generated artifacts |
|---|---|
| `codex` | `AGENTS.md`, `.agents/skills/<skill>/SKILL.md` |
| `gitlab-duo` | `AGENTS.md`, `.gitlab/duo/custom-rules.md`, `.gitlab/duo/flows/*.md` |
| `github-copilot` | `.github/copilot-instructions.md`, `.github/prompts/*.prompt.md` |
| `openhands` | `AGENTS.md`, `.openhands/instructions.md` |
| `opencode` | `AGENTS.md`, `.opencode/instructions.md` |
| `generic` | portable `SKILL.md` bundles |

### Profile

A **profile** is a named behavior package used by templates. Examples:

- `base`
- `devsecops`
- `documentation`
- `gitlab-governance`
- `local-models`
- `python`
- `typescript`
- `strict`

Profiles are passed into templates and can be used to alter generated wording or policy emphasis.

### Skill

A **skill** is a reusable capability bundle, usually rendered as a `SKILL.md` file.

Included skills:

- `cost-based-planner`
- `safe-implementer`
- `verification-reviewer`
- `security-reviewer`
- `documentation-maintainer`
- `universal-skill-creator`

### Flow

A **flow** is a named multi-step process, primarily useful for GitLab Duo / agent-platform-style usage.

Included example flows:

- `secure-code-change`
- `documentation-review`
- `ci-cd-review`

### Lockfile

The CLI writes `.agentic-template.lock` after applying a target. It records managed files, checksums, platforms, and applied targets.

The lockfile enables safe updates:

- unchanged managed files can be updated automatically;
- locally modified managed files become conflicts;
- unmanaged existing files are not overwritten unless `--force` is used.

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

Alternative editable-style usage during development:

```bash
uv run agentic-template --help
```

## Quickstart

Create a starter bake file in a target repository:

```bash
agentic-template init --target /path/to/repo
```

List available targets:

```bash
agentic-template list-targets --target /path/to/repo
```

Preview a target without writing files:

```bash
agentic-template bake default --target /path/to/repo --dry-run
```

Apply a target:

```bash
agentic-template bake default --target /path/to/repo --write
```

Validate generated files:

```bash
agentic-template validate --target /path/to/repo
```

Show the planned file-level changes for a target:

```bash
agentic-template diff default --target /path/to/repo
```

## Recommended target layout

A clear production-oriented bake file should separate platform targets from aggregate targets:

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

  copilot:
    description: GitHub Copilot repository instructions and prompts
    platforms:
      - github-copilot
    profiles:
      - base
      - devsecops
      - documentation

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
    description: Local agent setup for Ollama-friendly tools
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
    description: Standard daily development setup
    inherits:
      - codex
      - copilot

  all:
    description: All supported agentic platforms
    inherits:
      - codex
      - copilot
      - gitlab
      - local-ai
```

## Why can `default` contain multiple platforms?

`default` is only a target name. It is not special beyond being a convenient preset.

If `default` contains:

```yaml
platforms:
  - codex
  - github-copilot
  - opencode
```

then running:

```bash
agentic-template bake default --target . --write
```

means:

> Render Codex, GitHub Copilot, and OpenCode artifacts for this repository.

For stricter production usage, prefer explicit targets like `codex`, `copilot`, `gitlab`, `local-ai`, and aggregate them with `inherits` into `default` or `all`.

## Configuration reference: `agentic.bake.yaml`

### Top-level fields

| Field | Type | Required | Description |
|---|---:|---:|---|
| `version` | string | yes | Bake file schema version. Currently only `"1"` is supported. |
| `variables` | object | no | Global variables passed to all rendered templates. |
| `targets` | object | yes | Map of target names to target configurations. |

### `targets.<name>` fields

| Field | Type | Required | Description |
|---|---:|---:|---|
| `description` | string | no | Human-readable description shown in `list-targets`. |
| `inherits` | list[string] | no | Other targets to merge before this target. Enables reusable target composition. |
| `platforms` | list[string] | no | Platform adapters to render. Supported: `codex`, `gitlab-duo`, `github-copilot`, `openhands`, `opencode`, `generic`. |
| `profiles` | list[string] | no | Behavior/profile labels passed to templates. |
| `skills` | list[string] | no | Skill bundles to render where supported by the selected platform. |
| `flows` | list[string] | no | Flow instruction files to render where supported, mainly GitLab Duo. |
| `model` | object | no | Optional local/cloud model defaults for generated instructions. |
| `rules` | object | no | Policy flags passed to templates. |
| `variables` | object | no | Target-specific variables. These override top-level variables with the same key. |

### `model` fields

| Field | Type | Required | Description |
|---|---:|---:|---|
| `provider` | string | no | Model provider name, for example `ollama`, `openai`, `anthropic`, `openrouter`. |
| `default_model` | string | no | Default model name, for example `qwen2.5-coder:7b`. |
| `base_url` | string | no | Base URL for local or OpenAI-compatible endpoints, for example `http://localhost:11434`. |

### `rules` examples

`rules` is intentionally open-ended so teams can express governance flags without changing the schema.

Example:

```yaml
rules:
  no_direct_push: true
  require_tests: true
  require_security_review: true
  forbid_secret_files: true
  require_merge_request: true
```

Templates can render these as explicit agent instructions.

### Variable merge behavior

Top-level variables apply to every target:

```yaml
variables:
  project_name: CoachIQ
  default_language: de
```

Target-level variables override top-level variables:

```yaml
targets:
  documentation:
    variables:
      default_language: en
```

Resolved value for `documentation.default_language` is `en`.

### Inheritance merge behavior

When a target inherits another target:

- lists are appended and de-duplicated while preserving order;
- `rules` are merged, with child values overriding parent values;
- `variables` are merged, with child values overriding parent values;
- `model` is replaced by the child target if the child defines one;
- `description` is replaced by the child target if the child defines one.

Example:

```yaml
targets:
  base:
    platforms:
      - codex
    profiles:
      - base
    skills:
      - cost-based-planner

  strict:
    inherits:
      - base
    profiles:
      - devsecops
      - strict
    skills:
      - security-reviewer
      - verification-reviewer
    rules:
      require_tests: true
```

Resolved `strict` target:

```yaml
platforms:
  - codex
profiles:
  - base
  - devsecops
  - strict
skills:
  - cost-based-planner
  - security-reviewer
  - verification-reviewer
rules:
  require_tests: true
```

## CLI reference

### `init`

Create a starter `agentic.bake.yaml`.

```bash
agentic-template init --target .
agentic-template init --target . --overwrite
```

Options:

| Option | Description |
|---|---|
| `--target`, `-t` | Target repository path. Defaults to current directory. |
| `--overwrite` | Replace an existing `agentic.bake.yaml`. |

### `list-targets`

List configured targets.

```bash
agentic-template list-targets --target .
agentic-template list-targets --file ./agentic.bake.yaml
```

Options:

| Option | Description |
|---|---|
| `--target`, `-t` | Target repository path. |
| `--file`, `-f` | Explicit bake file path. Defaults to `<target>/agentic.bake.yaml`. |

### `bake`

Render a target.

```bash
agentic-template bake <target-name> --target . --dry-run
agentic-template bake <target-name> --target . --write
agentic-template bake <target-name> --target . --write --force
```

Options:

| Option | Description |
|---|---|
| `<target-name>` | Target from `agentic.bake.yaml`, for example `default`, `codex`, `gitlab`, `all`. |
| `--target`, `-t` | Target repository path. |
| `--file`, `-f` | Explicit bake file path. |
| `--write` | Write files to disk. Without this, the command is a dry-run. |
| `--dry-run` | Preview only. Equivalent to omitting `--write`. |
| `--force` | Overwrite unmanaged or conflicting files. Use carefully. |

### `diff`

Show planned file-level changes. This is a dry-run wrapper around `bake`.

```bash
agentic-template diff default --target .
```

### `validate`

Validate generated agentic files.

```bash
agentic-template validate --target .
```

The validator checks core structures, required metadata, and known platform output conventions.

### `--version`

Show the installed version.

```bash
agentic-template --version
```

## Safety model

The CLI is safe by default:

- `bake` does not write unless `--write` is set.
- Existing unmanaged files are not overwritten unless `--force` is set.
- Conflicting managed files block writes unless `--force` is set.
- A `.agentic-template.lock` file records managed files and checksums.
- `diff` and `dry-run` show planned changes before write.
- `validate` checks expected structures and core metadata.

## Typical workflows

### Initialize a repository

```bash
agentic-template init --target .
agentic-template list-targets --target .
agentic-template bake default --target . --dry-run
agentic-template bake default --target . --write
agentic-template validate --target .
git diff
```

### Apply only Codex files

```bash
agentic-template bake codex --target . --dry-run
agentic-template bake codex --target . --write
```

### Apply GitLab Duo setup

```bash
agentic-template bake gitlab --target . --dry-run
agentic-template bake gitlab --target . --write
```

### Apply everything

```bash
agentic-template bake all --target . --dry-run
agentic-template bake all --target . --write
```

### Resolve conflicts

If the CLI reports conflicts:

1. Inspect the existing file.
2. Decide whether local changes should be preserved.
3. Manually merge or rerun with `--force` if overwriting is intended.

```bash
agentic-template bake default --target . --write --force
```

## Generated output by platform

### Codex

Typical output:

```text
AGENTS.md
.agents/skills/<skill-name>/SKILL.md
```

Use for Codex CLI and Codex-enabled repository workflows.

### GitHub Copilot

Typical output:

```text
.github/copilot-instructions.md
.github/prompts/default.prompt.md
```

Use for repository-wide Copilot guidance and reusable prompt files.

### GitLab Duo

Typical output:

```text
AGENTS.md
.gitlab/duo/custom-rules.md
.gitlab/duo/flows/<flow-name>.md
```

This adapter intentionally models GitLab Duo through repository instructions, rules, and flow guidance rather than Claude-style subagents.

### OpenHands

Typical output:

```text
AGENTS.md
.openhands/instructions.md
```

Use for local or remote OpenHands runs.

### OpenCode

Typical output:

```text
AGENTS.md
.opencode/instructions.md
```

Use for terminal-centric local coding-agent workflows.

### Generic

Typical output:

```text
.skills/<skill-name>/SKILL.md
```

Use for portable skill bundles or unsupported agentic systems.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Project structure

```text
agentic-template-kit/
├── pyproject.toml
├── README.md
├── docs/
├── examples/
├── src/
│   └── agentic_template_kit/
│       ├── cli.py
│       ├── bake.py
│       ├── detector.py
│       ├── lockfile.py
│       ├── models.py
│       ├── renderer.py
│       ├── validator.py
│       └── templates/
└── tests/
```

## Design notes

This project intentionally separates:

- **Templates**: reusable platform-specific text assets.
- **Bake file**: project-specific target selection.
- **Targets**: named presets for one or more agentic outputs.
- **Profiles**: behavior and policy bundles passed to templates.
- **CLI**: reproducible renderer and lockfile manager.
- **Generated files**: committed into target repositories as normal agentic configuration.
