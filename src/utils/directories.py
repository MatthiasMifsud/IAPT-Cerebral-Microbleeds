import logging
logger = logging.getLogger(__name__)

def _create_dirs(dirs: list, parents=True, exist_ok=True) -> None:
    created = []
    for dir in dirs:
        if not dir.exists():
            created.append(str(dir))
        dir.mkdir(parents=parents, exist_ok=exist_ok) #on each run it recreates the directory
    
    if created:
        logger.info(f"ℹ️ Created {len(created)} directories: {', '.join(created)}")
    else:
        logger.info("ℹ️ Directories already exist")