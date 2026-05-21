from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from .models import RenderedFile

LOCKFILE = ".agentic-template.lock"


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_lockfile(target: Path, files: list[RenderedFile], target_name: str) -> None:
    data = {
        "version": "1",
        "target": target_name,
        "managed_files": [
            {
                "path": str(rendered.destination),
                "platform": rendered.platform,
                "source": rendered.source,
                "checksum": sha256_text(rendered.content),
            }
            for rendered in files
        ],
    }
    (target / LOCKFILE).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def load_lockfile(target: Path) -> dict:
    path = target / LOCKFILE
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def managed_files_by_path(lockfile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    managed_files = lockfile.get("managed_files", [])
    result: dict[str, dict[str, Any]] = {}
    for item in managed_files:
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        result[path] = item
    return result
