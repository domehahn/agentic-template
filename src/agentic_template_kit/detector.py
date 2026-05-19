from __future__ import annotations

from pathlib import Path


def detect_project(target: Path) -> dict[str, object]:
    """Detect lightweight repository metadata for template context."""
    files = {p.name for p in target.iterdir()} if target.exists() else set()

    package_manager = None
    language = "unknown"
    framework_markers: list[str] = []

    if "pyproject.toml" in files:
        language = "python"
        package_manager = "uv/poetry/pip"
    if "poetry.lock" in files:
        package_manager = "poetry"
    if "uv.lock" in files:
        package_manager = "uv"
    if "requirements.txt" in files and package_manager is None:
        language = "python"
        package_manager = "pip"

    if "package.json" in files:
        language = "javascript/typescript"
        package_manager = "npm"
    if "pnpm-lock.yaml" in files:
        package_manager = "pnpm"
    if "yarn.lock" in files:
        package_manager = "yarn"

    if "pom.xml" in files:
        language = "java"
        package_manager = "maven"
    if "build.gradle" in files or "build.gradle.kts" in files:
        language = "java/kotlin"
        package_manager = "gradle"

    if "go.mod" in files:
        language = "go"
        package_manager = "go"
    if "Cargo.toml" in files:
        language = "rust"
        package_manager = "cargo"

    if (target / ".gitlab-ci.yml").exists():
        framework_markers.append("gitlab-ci")
    if (target / ".github").exists():
        framework_markers.append("github")
    if (target / "Dockerfile").exists():
        framework_markers.append("docker")

    return {
        "repo_name": target.name,
        "language": language,
        "package_manager": package_manager,
        "framework_markers": framework_markers,
    }
