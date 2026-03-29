import os 
from dotenv import load_dotenv
from pathlib import Path
from .utils.directories import _create_dirs

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env") # loading env

DATA_DIR: Path = ROOT_DIR / "data"
STATS_DIR: Path = DATA_DIR / "statistics"

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

    _create_dirs([path_obj])
    return path_obj

# env vars
ORIG_DATA: Path = _get_abs_path('original_dataset')
RAW_BASE: Path = _get_abs_path('nnUNet_raw')
PREPROCESSED_BASE: Path = _get_abs_path('nnUNet_preprocessed')
RESULTS_BASE: Path = _get_abs_path('nnUNet_results')

# target dataset dirs
DATASET_DIR: Path = RAW_BASE / "Dataset001_VALDO"
IMAGES_DIR: Path = DATASET_DIR / "imagesTr"
LABELS_DIR: Path = DATASET_DIR / "labelsTr"

SUBJECT_PREFIX:str = "sub-"
DATA_TYPE:str = ".nii.gz"
METADATA_FILE:str = "dataset.json"
MODALITY_SUFFIXES:list[str] = ["0000", "0001", "0002"] 
K_FOLDS:int = 5