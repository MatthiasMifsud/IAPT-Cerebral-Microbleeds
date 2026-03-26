import os 
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env") # loading env

def _get_abs_path(var_name) -> Path:
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
        path_obj = (ROOT_DIR / path_str).resolve()

    return path_obj

# source dataset dir
ORIG_DATA = _get_abs_path('original_dataset')

# target dataset dir
RAW_BASE = _get_abs_path('nnUNet_raw')
DATASET_DIR = RAW_BASE / "Dataset001_VALDO"
IMAGES_DIR = DATASET_DIR / "imagesTr"
LABELS_DIR = DATASET_DIR / "labelsTr"

SUBJECT_PREFIX = "sub-"
DATASET_SIZE = 72