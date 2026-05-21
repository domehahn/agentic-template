# Usage

## Initialize for GitLab Duo

```bash
agentic-template init --target . --platform "gitlab-duo" --project-name MyProject
agentic-template bake default --target . --plan
agentic-template bake default --target . --write
agentic-template validate --target .
```

## Initialize for multiple platforms

```bash
agentic-template init --target . --platform "gitlab-duo,codex,github-copilot" --project-name MyProject
agentic-template bake default --target . --write
```

## Initialize with defaults (all supported platforms)

```bash
agentic-template init --target . --project-name MyProject
agentic-template bake default --target . --write
```

Default platforms when `--platform` and `--preset` are not provided:

- `codex`
- `github-copilot`
- `claude`
- `gitlab-duo`
- `opencode`
- `openhands`
- `ollama`

## Output layout for multi-platform bakes

- Root `AGENTS.md` is a generated platform index.
- Platform-specific instruction files are written to `.agentic/<platform>/AGENTS.md`.
- Platform-native files remain in their expected locations, for example:
  - `.github/copilot-instructions.md`
  - `.claude/skills/...`
  - `skills/...` and `.gitlab/duo/flows/...`

## Presets

```bash
agentic-template init --target . --preset gitlab
agentic-template init --target . --preset enterprise
agentic-template init --target . --preset local-ai
agentic-template init --target . --preset all
```
