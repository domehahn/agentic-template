# Architecture

Agentic Template Kit separates four responsibilities:

1. **Bake file**: project-local selection of targets, platforms, skills, flows, rules, and variables.
2. **Template pack**: versioned templates embedded in the Python package.
3. **Renderer**: resolves targets, renders Jinja templates, merges common destinations such as `AGENTS.md`.
4. **Lockfile**: records managed outputs and checksums for safe updates.

## Safety

The generator is dry-run by default. File writes require `--write`.

Existing unmanaged files are treated as conflicts. Use `--force` only when intentional.

## Platform adapters

Each platform adapter maps a logical platform name to concrete output paths:

- Codex: `AGENTS.md`, `.agents/skills/**`
- GitLab Duo: `AGENTS.md`, `.gitlab/duo/**`
- GitHub Copilot: `.github/copilot-instructions.md`, `.github/prompts/**`
- OpenHands: `AGENTS.md`, `.openhands/instructions.md`
- OpenCode: `AGENTS.md`, `.opencode/instructions.md`

`AGENTS.md` may be shared by multiple platforms. In that case, the renderer merges platform sections using managed HTML comments.
