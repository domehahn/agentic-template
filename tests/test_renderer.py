from pathlib import Path

from agentic_template_kit.models import TargetConfig
from agentic_template_kit.renderer import plan_changes, render_files


def test_render_codex_files(tmp_path: Path):
    target = TargetConfig(
        platforms=["codex"],
        skills=["safe-implementer"],
        variables={"project_name": "demo"},
    )

    files = render_files(tmp_path, target, "default")
    paths = {f.destination.as_posix() for f in files}

    assert "AGENTS.md" in paths
    assert ".agents/skills/safe-implementer/SKILL.md" in paths


def test_plan_create(tmp_path: Path):
    target = TargetConfig(
        platforms=["github-copilot"],
        variables={"project_name": "demo"},
    )
    files = render_files(tmp_path, target, "default")
    changes = plan_changes(tmp_path, files, managed_checksums={})

    assert all(change.action == "create" for change in changes)
