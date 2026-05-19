from __future__ import annotations

from pathlib import Path

import yaml

from agentic_template_kit.models import LockFile, LockFileEntry, RenderedFile

LOCK_FILE_NAME = ".agentic-template.lock"


def sha256_text(content: str) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_lock_file(target: Path) -> LockFile:
    path = target / LOCK_FILE_NAME
    if not path.exists():
        return LockFile(
            template_pack={"name": "agentic-template-kit", "version": "0.1.0"},
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return LockFile.model_validate(data)


def write_lock_file(target: Path, lock: LockFile) -> None:
    path = target / LOCK_FILE_NAME
    payload = lock.model_dump(mode="json")
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def update_lock(lock: LockFile, target_name: str, rendered_files: list[RenderedFile]) -> LockFile:
    entries_by_path = {entry.path: entry for entry in lock.managed_files}

    for rendered in rendered_files:
        rel = rendered.destination.as_posix()
        entries_by_path[rel] = LockFileEntry(
            path=rel,
            source=rendered.source,
            checksum=sha256_text(rendered.content),
            platform=rendered.platform,
        )

    if target_name not in lock.applied_targets:
        lock.applied_targets.append(target_name)

    for platform in sorted({rf.platform for rf in rendered_files}):
        if platform not in lock.platforms:
            lock.platforms.append(platform)

    lock.managed_files = [entries_by_path[key] for key in sorted(entries_by_path)]
    return lock
