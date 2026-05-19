from pathlib import Path

from agentic_template_kit.validator import validate_target


def test_validator_passes_empty_repo(tmp_path: Path):
    assert validate_target(tmp_path) == []


def test_validator_detects_bad_skill(tmp_path: Path):
    skill_dir = tmp_path / ".agents" / "skills" / "bad"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Missing metadata\n", encoding="utf-8")

    issues = validate_target(tmp_path)

    assert any("frontmatter" in issue for issue in issues)
    assert any("name" in issue for issue in issues)
    assert any("description" in issue for issue in issues)
