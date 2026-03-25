from . import config as cf
from pathlib import Path

def create_dirs(dirs: list[Path], with_parent=True):

    created = []
    for dir in dirs:
        if not dir.exists():
            created.append(str(dir))
        dir.mkdir(parents=with_parent, exist_ok=True)
    
    created_len = len(created)
    if created_len > 0:
        print(f"Created {created_len} directories: {', '.join(created)}")
    else:
        print(f"Directories already exist")

def populate_nnu_dir():
    pass
    
create_dirs([cf.IMAGES_DIR, cf.LABELS_DIR])
populate_nnu_dir()