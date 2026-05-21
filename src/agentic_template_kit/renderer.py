from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .catalog import CLAUDE_SUBAGENTS, skill_description, skill_title
from .models import BakeConfig, RenderedFile, TargetConfig

TEMPLATE_ROOT = Path(__file__).parent / "templates"


def _render(env: Environment, template: str, context: dict) -> str:
    return env.get_template(template).render(**context)


def _skill_meta(skill_names: list[str]) -> list[dict[str, str]]:
    return [
        {
            "name": skill,
            "title": skill_title(skill),
            "description": skill_description(skill),
        }
        for skill in skill_names
    ]


def _claude_subagents_for_target(target: TargetConfig) -> list[dict]:
    available_skills = set(target.skills)
    selected: list[dict] = []

    for agent in CLAUDE_SUBAGENTS:
        agent_skills = [skill for skill in agent.get("skills", []) if skill in available_skills]
        if not agent_skills:
            continue

        selected.append(
            {
                **agent,
                "title": skill_title(agent["name"]),
                "skills": agent_skills,
            }
        )

    return selected


def render_files(config: BakeConfig, target: TargetConfig) -> list[RenderedFile]:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    skills = _skill_meta(target.skills)
    claude_subagents = _claude_subagents_for_target(target)

    context = {
        "variables": config.variables,
        "target": target,
        "skills": skills,
        "claude_subagents": claude_subagents,
        "flows": target.flows,
        "rules": target.rules,
        "model": target.model,
    }

    files: list[RenderedFile] = []
    platform_docs: list[dict[str, str]] = []

    def add(platform: str, template: str, destination: str, extra: dict | None = None) -> None:
        ctx = context if extra is None else {**context, **extra}
        files.append(
            RenderedFile(
                source=template,
                destination=Path(destination),
                content=_render(env, template, ctx),
                platform=platform,
            )
        )

    if "codex" in target.platforms:
        add("codex", "codex/AGENTS.md.j2", ".agentic/codex/AGENTS.md")
        platform_docs.append(
            {
                "platform": "codex",
                "path": ".agentic/codex/AGENTS.md",
                "description": "Codex instructions and skill routing",
            }
        )
        for skill in skills:
            add(
                "codex",
                "shared/SKILL.md.j2",
                f".agents/skills/{skill['name']}/SKILL.md",
                {"skill": skill, "invocation_prefix": "$", "slash_command": False},
            )

    if "gitlab-duo" in target.platforms:
        add("gitlab-duo", "gitlab-duo/AGENTS.md.j2", ".agentic/gitlab-duo/AGENTS.md")
        platform_docs.append(
            {
                "platform": "gitlab-duo",
                "path": ".agentic/gitlab-duo/AGENTS.md",
                "description": "GitLab Duo instructions, skills, and flow context requirements",
            }
        )
        add("gitlab-duo", "gitlab-duo/chat-rules.md.j2", ".gitlab/duo/chat-rules.md")
        for skill in skills:
            add(
                "gitlab-duo",
                "shared/SKILL.md.j2",
                f"skills/{skill['name']}/SKILL.md",
                {"skill": skill, "invocation_prefix": "/", "slash_command": True},
            )
        add("gitlab-duo", "gitlab-duo/flows/README.md.j2", ".gitlab/duo/flows/README.md")
        for flow in target.flows:
            add(
                "gitlab-duo",
                "gitlab-duo/flows/flow.yaml.j2",
                f".gitlab/duo/flows/{flow}.yaml",
                {"flow_name": flow, "flow_title": skill_title(flow)},
            )

    if "claude" in target.platforms:
        add("claude", "claude/CLAUDE.md.j2", ".agentic/claude/AGENTS.md")
        platform_docs.append(
            {
                "platform": "claude",
                "path": ".agentic/claude/AGENTS.md",
                "description": "Claude Code integration, skills, and subagent routing",
            }
        )
        for skill in skills:
            add(
                "claude",
                "shared/SKILL.md.j2",
                f".claude/skills/{skill['name']}/SKILL.md",
                {"skill": skill, "invocation_prefix": "/", "slash_command": False},
            )
        for subagent in claude_subagents:
            add(
                "claude",
                "claude/agent.md.j2",
                f".claude/agents/{subagent['name']}.md",
                {"subagent": subagent},
            )

    if "github-copilot" in target.platforms:
        add(
            "github-copilot",
            "github-copilot/copilot-instructions.md.j2",
            ".github/copilot-instructions.md",
        )
        add(
            "github-copilot",
            "shared/platform-reference.md.j2",
            ".agentic/github-copilot/AGENTS.md",
            {
                "platform_label": "GitHub Copilot",
                "target_file": ".github/copilot-instructions.md",
                "target_description": "Repository-level Copilot instructions",
            },
        )
        platform_docs.append(
            {
                "platform": "github-copilot",
                "path": ".agentic/github-copilot/AGENTS.md",
                "description": "Pointer to GitHub Copilot repository instructions and prompts",
            }
        )
        for skill in skills:
            add(
                "github-copilot",
                "github-copilot/prompt.prompt.md.j2",
                f".github/prompts/{skill['name']}.prompt.md",
                {"skill": skill},
            )

    if "openhands" in target.platforms:
        add("openhands", "openhands/AGENTS.md.j2", ".agentic/openhands/AGENTS.md")
        platform_docs.append(
            {
                "platform": "openhands",
                "path": ".agentic/openhands/AGENTS.md",
                "description": "OpenHands instructions and capability overview",
            }
        )
        add("openhands", "openhands/instructions.md.j2", ".openhands/instructions.md")

    if "opencode" in target.platforms:
        add("opencode", "opencode/AGENTS.md.j2", ".agentic/opencode/AGENTS.md")
        platform_docs.append(
            {
                "platform": "opencode",
                "path": ".agentic/opencode/AGENTS.md",
                "description": "OpenCode instructions and capability overview",
            }
        )
        add("opencode", "opencode/instructions.md.j2", ".opencode/instructions.md")

    if "ollama" in target.platforms:
        add("ollama", "ollama/Modelfile.j2", ".ollama/Modelfile")
        add("ollama", "ollama/README.md.j2", ".ollama/README.md")
        add(
            "ollama",
            "shared/platform-reference.md.j2",
            ".agentic/ollama/AGENTS.md",
            {
                "platform_label": "Ollama",
                "target_file": ".ollama/README.md",
                "target_description": "Local model configuration and usage notes",
            },
        )
        platform_docs.append(
            {
                "platform": "ollama",
                "path": ".agentic/ollama/AGENTS.md",
                "description": "Pointer to Ollama model and runtime configuration",
            }
        )

    if "generic" in target.platforms:
        for skill in skills:
            add(
                "generic",
                "shared/SKILL.md.j2",
                f".agentic/skills/{skill['name']}/SKILL.md",
                {"skill": skill, "invocation_prefix": "$", "slash_command": False},
            )

    if platform_docs:
        add("shared", "shared/AGENTS.index.md.j2", "AGENTS.md", {"platform_docs": platform_docs})

    return files
