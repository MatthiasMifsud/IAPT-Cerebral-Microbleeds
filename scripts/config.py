import os 
from dotenv import load_dotenv
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

BASE_PATH: Path = Path(__file__).resolve().parent.parent
load_dotenv(BASE_PATH / ".env") # loading env

def create_dirs(dirs: list, parents=True, exist_ok=True) -> None:
    created = []
    for dir in dirs:
        if not dir.exists():
            created.append(str(dir))
        dir.mkdir(parents=parents, exist_ok=exist_ok) # on each run it recreates the directory
    
    if created:
        logger.info(f"ℹ️ Created {len(created)} directories: {', '.join(created)}")
    else:
        logger.info("ℹ️ Directories already exist")

def get_abs_path(var_name) -> Path:
    """
    Retrieves the absolute paths from environmental variables.

    * Uses relative path to project root if path is relative.
    * Uses absolute path if the path is explicitly defined.
    """
    path_str = os.getenv(var_name)
    if not path_str: # not found in .env
        raise EnvironmentError(f"Variable: '{var_name}' NOT found in .env")
    
    path_obj = Path(path_str)
    if not path_obj.is_absolute(): # assuming now that it is relative to the root    
        path_obj = (BASE_PATH / path_str).resolve()

    create_dirs([path_obj])
    return path_obj

# env vars
ORIG_DATA_PATH: Path = get_abs_path('original_dataset')
RAW_PATH: Path = get_abs_path('nnUNet_raw')

# target paths
DATASET_PATH: Path = RAW_PATH / "Dataset001_VALDO"
IMAGES_PATH: Path = DATASET_PATH / "imagesTr"
LABELS_PATH: Path = DATASET_PATH / "labelsTr"

SUBJECT_PREFIX:str = "sub-"
DATA_TYPE: str = ".nii.gz"
METADATA_FILE: str = "dataset.json"
MODALITY_SUFFIXES: list[str] = ["0000", "0001", "0002"] 