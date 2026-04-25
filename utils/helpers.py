from pathlib import Path
from .logger import success, info

def create_dirs(paths: list[Path] | Path, parents: bool = True, exist_ok: bool = True) -> None:
    if isinstance(paths, Path):
        paths = [paths]

    created = []
    for path in paths:
        if not path.exists():
            created.append(str(path))
        path.mkdir(parents=parents, exist_ok=exist_ok)

    if created:
        success(f"Created {len(created)} directorie(s): {', '.join(created)}")
    else:
        info("All directories already exist")