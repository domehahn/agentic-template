from agentic_template_kit.models import BakeFile


def test_resolve_inherited_target():
    bake = BakeFile.model_validate(
        {
            "version": "1",
            "variables": {"project_name": "x"},
            "targets": {
                "base": {"platforms": ["codex"], "skills": ["safe-implementer"]},
                "child": {
                    "inherits": ["base"],
                    "platforms": ["github-copilot"],
                    "skills": ["security-reviewer"],
                },
            },
        }
    )

    target = bake.resolve_target("child")

    assert target.platforms == ["codex", "github-copilot"]
    assert target.skills == ["safe-implementer", "security-reviewer"]
    assert target.variables["project_name"] == "x"
