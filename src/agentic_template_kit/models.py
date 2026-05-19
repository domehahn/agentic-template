from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ModelConfig(BaseModel):
    provider: str | None = None
    default_model: str | None = None
    base_url: str | None = None


class TargetConfig(BaseModel):
    description: str | None = None
    inherits: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    profiles: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    flows: list[str] = Field(default_factory=list)
    model: ModelConfig | None = None
    rules: dict[str, Any] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)

    @field_validator("platforms", "profiles", "skills", "flows", "inherits")
    @classmethod
    def unique_preserve_order(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in value:
            if item not in seen:
                result.append(item)
                seen.add(item)
        return result


class BakeFile(BaseModel):
    version: Literal["1"] = "1"
    variables: dict[str, Any] = Field(default_factory=dict)
    targets: dict[str, TargetConfig] = Field(default_factory=dict)

    def resolve_target(self, name: str) -> TargetConfig:
        if name not in self.targets:
            available = ", ".join(sorted(self.targets)) or "<none>"
            raise KeyError(f"Target '{name}' not found. Available targets: {available}")

        resolving: set[str] = set()

        def merge(base: TargetConfig, overlay: TargetConfig) -> TargetConfig:
            merged = TargetConfig(
                description=overlay.description or base.description,
                inherits=[],
                platforms=[*base.platforms, *overlay.platforms],
                profiles=[*base.profiles, *overlay.profiles],
                skills=[*base.skills, *overlay.skills],
                flows=[*base.flows, *overlay.flows],
                model=overlay.model or base.model,
                rules={**base.rules, **overlay.rules},
                variables={**base.variables, **overlay.variables},
            )
            # normalize uniqueness through validation
            return TargetConfig.model_validate(merged.model_dump())

        def resolve(current: str) -> TargetConfig:
            if current in resolving:
                chain = " -> ".join([*resolving, current])
                raise ValueError(f"Cyclic target inheritance detected: {chain}")
            resolving.add(current)

            target = self.targets[current]
            result = TargetConfig()
            for parent in target.inherits:
                if parent not in self.targets:
                    raise KeyError(f"Target '{current}' inherits unknown target '{parent}'")
                result = merge(result, resolve(parent))
            result = merge(result, target)

            resolving.remove(current)
            return result

        resolved = resolve(name)
        resolved.variables = {**self.variables, **resolved.variables}
        return resolved


class RenderedFile(BaseModel):
    source: str
    destination: Path
    content: str
    platform: str
    managed: bool = True


class PlannedChange(BaseModel):
    action: Literal["create", "update", "skip", "conflict", "unchanged"]
    destination: Path
    source: str | None = None
    reason: str | None = None
    old_checksum: str | None = None
    new_checksum: str | None = None


class LockFileEntry(BaseModel):
    path: str
    source: str
    checksum: str
    platform: str


class LockFile(BaseModel):
    version: Literal["1"] = "1"
    template_pack: dict[str, str] = Field(default_factory=dict)
    applied_targets: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    managed_files: list[LockFileEntry] = Field(default_factory=list)
