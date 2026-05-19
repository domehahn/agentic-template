from __future__ import annotations

from pathlib import Path

import yaml

from agentic_template_kit.models import BakeFile

DEFAULT_BAKE_FILE = "agentic.bake.yaml"


def load_bake_file(path: Path) -> BakeFile:
    if not path.exists():
        raise FileNotFoundError(f"Bake file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return BakeFile.model_validate(data)


def write_default_bake_file(target: Path, overwrite: bool = False) -> Path:
    bake_file = target / DEFAULT_BAKE_FILE
    if bake_file.exists() and not overwrite:
        return bake_file

    bake_file.write_text(
        """version: "1"

variables:
  project_name: "{{ project_name }}"
  owner_team: platform-engineering
  default_language: de
  governance_level: standard

targets:
  default:
    description: Standard agentic setup for local development
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
    description: Local Ollama/OpenCode/OpenHands setup
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
    description: Generate all supported platform artifacts
    inherits:
      - default
      - gitlab
      - local-ai
""",
        encoding="utf-8",
    )
    return bake_file
