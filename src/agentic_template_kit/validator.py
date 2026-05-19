from __future__ import annotations

from pathlib import Path

import yaml


def validate_target(target: Path) -> list[str]:
    issues: list[str] = []

    if not target.exists():
        return [f"Target does not exist: {target}"]

    bake = target / "agentic.bake.yaml"
    if bake.exists():
        try:
            yaml.safe_load(bake.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            issues.append(f"Invalid agentic.bake.yaml: {exc}")

    agents = target / "AGENTS.md"
    if agents.exists() and not agents.read_text(encoding="utf-8").strip():
        issues.append("AGENTS.md exists but is empty")

    skills_dir = target / ".agents" / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                issues.append(f"Missing SKILL.md in {skill_dir}")
                continue
            text = skill_file.read_text(encoding="utf-8")
            if not text.startswith("---"):
                issues.append(f"{skill_file} is missing YAML frontmatter")
            if "name:" not in text:
                issues.append(f"{skill_file} is missing 'name' metadata")
            if "description:" not in text:
                issues.append(f"{skill_file} is missing 'description' metadata")

    copilot = target / ".github" / "copilot-instructions.md"
    if copilot.exists() and "Agentic" not in copilot.read_text(encoding="utf-8"):
        issues.append(".github/copilot-instructions.md does not look like an agentic-template output")

    return issues
