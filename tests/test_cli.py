from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from agentic_template_kit.cli import app

runner = CliRunner()


def test_init_with_comma_platforms(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "gitlab-duo,codex,github-copilot",
            "--project-name",
            "Demo",
        ],
    )

    assert result.exit_code == 0, result.output

    text = (tmp_path / "agentic.bake.yaml").read_text(encoding="utf-8")
    assert "gitlab-duo" in text
    assert "codex" in text
    assert "github-copilot" in text
    assert "{{ project_name }}" not in text


def test_gitlab_bake_writes_expected_paths(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "gitlab-duo",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / ".agentic" / "gitlab-duo" / "AGENTS.md").exists()
    assert (tmp_path / "skills" / "security-reviewer" / "SKILL.md").exists()
    assert (tmp_path / "skills" / "threat-modeler" / "SKILL.md").exists()
    assert (tmp_path / ".gitlab" / "duo" / "chat-rules.md").exists()
    assert (tmp_path / ".gitlab" / "duo" / "flows" / "secure-code-change.yaml").exists()


def test_gitlab_skill_enables_slash_command(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "gitlab-duo",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    text = (tmp_path / "skills" / "security-reviewer" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "slash-command: enabled" in text


def test_gitlab_flow_passes_required_context(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "gitlab-duo",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    text = (tmp_path / ".gitlab" / "duo" / "flows" / "secure-code-change.yaml").read_text(
        encoding="utf-8"
    )

    assert "context:inputs.user_rule" in text
    assert "context:inputs.workspace_agent_skills" in text


def test_gitlab_validation_passes(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "gitlab-duo",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    validate_result = runner.invoke(
        app,
        [
            "validate",
            "--target",
            str(tmp_path),
        ],
    )

    assert validate_result.exit_code == 0, validate_result.output


def test_all_preset_contains_local_ai(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--preset",
            "all",
            "--project-name",
            "Demo",
        ],
    )

    assert result.exit_code == 0, result.output

    text = (tmp_path / "agentic.bake.yaml").read_text(encoding="utf-8")
    assert "ollama" in text
    assert "openhands" in text
    assert "opencode" in text


def test_init_without_platform_defaults_to_all_platforms(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--project-name",
            "Demo",
        ],
    )

    assert result.exit_code == 0, result.output

    text = (tmp_path / "agentic.bake.yaml").read_text(encoding="utf-8")
    for platform in [
        "codex",
        "github-copilot",
        "claude",
        "gitlab-duo",
        "opencode",
        "openhands",
        "ollama",
    ]:
        assert platform in text


def test_codex_bake_writes_codex_skills(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "codex",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    assert (tmp_path / ".agentic" / "codex" / "AGENTS.md").exists()
    assert (tmp_path / ".agents" / "skills" / "safe-implementer" / "SKILL.md").exists()
    assert (tmp_path / ".agents" / "skills" / "security-reviewer" / "SKILL.md").exists()


def test_copilot_bake_writes_prompt_files(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "github-copilot",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    assert (tmp_path / ".agentic" / "github-copilot" / "AGENTS.md").exists()
    assert (tmp_path / ".github" / "copilot-instructions.md").exists()
    assert (tmp_path / ".github" / "prompts" / "security-reviewer.prompt.md").exists()


@pytest.mark.parametrize(
    ("platform", "expected_paths"),
    [
        (
            "codex",
            [
                "AGENTS.md",
                ".agents/skills/security-reviewer/SKILL.md",
                ".agents/skills/safe-implementer/SKILL.md",
                ".agents/skills/threat-modeler/SKILL.md",
            ],
        ),
        (
            "gitlab-duo",
            [
                "AGENTS.md",
                ".agentic/gitlab-duo/AGENTS.md",
                "skills/security-reviewer/SKILL.md",
                "skills/safe-implementer/SKILL.md",
                "skills/threat-modeler/SKILL.md",
                ".gitlab/duo/chat-rules.md",
                ".gitlab/duo/flows/secure-code-change.yaml",
            ],
        ),
        (
            "github-copilot",
            [
                ".github/copilot-instructions.md",
                ".github/prompts/security-reviewer.prompt.md",
                ".github/prompts/safe-implementer.prompt.md",
            ],
        ),
        (
            "claude",
            [
                "AGENTS.md",
                ".agentic/claude/AGENTS.md",
                ".claude/skills/security-reviewer/SKILL.md",
                ".claude/skills/safe-implementer/SKILL.md",
            ],
        ),
        (
            "openhands",
            [
                "AGENTS.md",
                ".agentic/openhands/AGENTS.md",
                ".openhands/instructions.md",
            ],
        ),
        (
            "opencode",
            [
                "AGENTS.md",
                ".agentic/opencode/AGENTS.md",
                ".opencode/instructions.md",
            ],
        ),
        (
            "ollama",
            [
                "AGENTS.md",
                ".agentic/ollama/AGENTS.md",
                ".ollama/Modelfile",
                ".ollama/README.md",
            ],
        ),
    ],
)
def test_each_platform_bakes_successfully(
    tmp_path: Path,
    platform: str,
    expected_paths: list[str],
) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            platform,
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    for expected_path in expected_paths:
        assert (tmp_path / expected_path).exists(), expected_path


def test_multi_platform_bake_writes_all_expected_outputs(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "gitlab-duo,codex,github-copilot,claude,opencode,openhands,ollama",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    expected_paths = [
        # Codex
        ".agents/skills/security-reviewer/SKILL.md",
        ".agents/skills/safe-implementer/SKILL.md",

        # GitLab Duo
        "skills/security-reviewer/SKILL.md",
        "skills/safe-implementer/SKILL.md",
        ".gitlab/duo/chat-rules.md",
        ".gitlab/duo/flows/secure-code-change.yaml",

        # GitHub Copilot
        ".github/copilot-instructions.md",
        ".github/prompts/security-reviewer.prompt.md",

        # Claude
        ".agentic/claude/AGENTS.md",
        ".claude/skills/security-reviewer/SKILL.md",

        # OpenCode
        ".opencode/instructions.md",

        # OpenHands
        ".openhands/instructions.md",

        # Ollama
        ".ollama/Modelfile",
        ".ollama/README.md",
    ]

    for expected_path in expected_paths:
        assert (tmp_path / expected_path).exists(), expected_path

def test_claude_bake_writes_skills_and_subagents(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "claude",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_result.exit_code == 0, bake_result.output

    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / ".agentic" / "claude" / "AGENTS.md").exists()
    assert (tmp_path / ".claude" / "skills" / "security-reviewer" / "SKILL.md").exists()
    assert (tmp_path / ".claude" / "skills" / "ci-cd-reviewer" / "SKILL.md").exists()

    assert (tmp_path / ".claude" / "agents" / "devsecops-reviewer.md").exists()
    assert (tmp_path / ".claude" / "agents" / "security-reviewer.md").exists()
    assert (tmp_path / ".claude" / "agents" / "ci-cd-reviewer.md").exists()
    assert (tmp_path / ".claude" / "agents" / "test-runner.md").exists()


def test_claude_subagent_preloads_skills(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "claude",
            "--project-name",
            "Demo",
        ],
    )
    runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )

    text = (tmp_path / ".claude" / "agents" / "devsecops-reviewer.md").read_text(
        encoding="utf-8"
    )

    assert "skills:" in text
    assert "security-reviewer" in text
    assert "ci-cd-reviewer" in text
    assert "dependency-supply-chain-reviewer" in text
    assert "release-readiness-reviewer" in text


def test_claude_md_references_subagents(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "claude",
            "--project-name",
            "Demo",
        ],
    )
    runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )

    text = (tmp_path / ".agentic" / "claude" / "AGENTS.md").read_text(encoding="utf-8")

    assert ".claude/agents/<subagent-name>.md" in text
    assert "devsecops-reviewer" in text
    assert "security-reviewer" in text
    assert "test-runner" in text


def test_plan_uses_state_and_reports_noop_after_write(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "codex",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_write = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_write.exit_code == 0, bake_write.output

    plan_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--plan",
        ],
    )
    assert plan_result.exit_code == 0, plan_result.output
    assert "State Plan (.agentic-template.lock)" in plan_result.output
    assert "noop" in plan_result.output


def test_plan_reports_state_delete_when_target_changes(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "codex",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_write = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_write.exit_code == 0, bake_write.output

    bake_text = (tmp_path / "agentic.bake.yaml").read_text(encoding="utf-8")
    updated_text = bake_text.replace("inherits:\n    - codex", "inherits: []\n    platforms: []")
    (tmp_path / "agentic.bake.yaml").write_text(updated_text, encoding="utf-8")

    plan_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--plan",
        ],
    )
    assert plan_result.exit_code == 0, plan_result.output
    assert "delete" in plan_result.output


def test_plan_accepts_detailed_diff_flag(tmp_path: Path) -> None:
    init_result = runner.invoke(
        app,
        [
            "init",
            "--target",
            str(tmp_path),
            "--platform",
            "codex",
            "--project-name",
            "Demo",
        ],
    )
    assert init_result.exit_code == 0, init_result.output

    bake_write = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--write",
        ],
    )
    assert bake_write.exit_code == 0, bake_write.output

    bake_file = tmp_path / "agentic.bake.yaml"
    original = bake_file.read_text(encoding="utf-8")
    changed = original.replace("project_name: Demo", "project_name: Demo Changed")
    bake_file.write_text(changed, encoding="utf-8")

    plan_result = runner.invoke(
        app,
        [
            "bake",
            "default",
            "--target",
            str(tmp_path),
            "--plan",
            "--detailed-diff",
        ],
    )
    assert plan_result.exit_code == 0, plan_result.output
    assert "Diff:" in plan_result.output

MARKDOWN_PATHS = [
    Path("README.md"),
    Path("docs/CLAUDE_CODE.md"),
    Path("docs/CONFIGURATION.md"),
    Path("docs/GITLAB_DUO.md"),
    Path("docs/SDLC_SKILLS.md"),
    Path("docs/USAGE.md"),
    Path("docs/ARCHITECTURE.md"),
    Path("src/agentic_template_kit/templates/claude/CLAUDE.md.j2"),
]


def test_markdown_code_fences_are_balanced() -> None:
    broken_files = []

    for path in MARKDOWN_PATHS:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        fence_count = text.count("```")

        if fence_count % 2 != 0:
            broken_files.append(f"{path} has {fence_count} code fences")

    assert broken_files == []
