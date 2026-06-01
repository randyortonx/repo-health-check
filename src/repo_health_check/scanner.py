from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


IGNORED_DIRS = {".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules"}


@dataclass(frozen=True)
class RepositorySnapshot:
    root: Path
    files: tuple[str, ...]

    def has_file(self, relative_path: str) -> bool:
        return relative_path.replace("\\", "/") in self.files

    def matching_files(self, *names: str) -> list[str]:
        wanted = {name.lower() for name in names}
        return sorted(path for path in self.files if Path(path).name.lower() in wanted)

    def files_under(self, prefix: str) -> list[str]:
        normalized = prefix.strip("/").replace("\\", "/")
        return sorted(path for path in self.files if path.startswith(f"{normalized}/"))

    def read_text(self, relative_path: str) -> str:
        root = self.root.expanduser().resolve()
        target = (root / relative_path).resolve()
        if not _is_relative_to(target, root):
            raise ValueError(f"Cannot read path outside repository: {relative_path}")
        normalized = target.relative_to(root).as_posix()
        if normalized not in self.files:
            raise ValueError(f"Cannot read path not part of repository snapshot: {relative_path}")
        return target.read_text(encoding="utf-8")


def scan_repository(path: str | Path) -> RepositorySnapshot:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    files: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in IGNORED_DIRS and _is_relative_to((current / dirname).resolve(), root)
        ]
        for filename in filenames:
            item = current / filename
            if item.is_file() and _is_relative_to(item.resolve(), root):
                files.add(item.relative_to(root).as_posix())
    return RepositorySnapshot(root=root, files=tuple(sorted(files)))


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
