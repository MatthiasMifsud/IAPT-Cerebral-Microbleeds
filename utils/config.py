from pathlib import Path

BASE_PATH: Path = Path(__file__).parent.parent

# data
DATA_PATH: Path = BASE_PATH / "data"

# nnUNet data
DATASET_NAME: str = "Dataset001_VALDO"
NNU_RAW: Path = DATA_PATH / "nnUNet_raw" / DATASET_NAME
RAW_IMAGES_PATH: Path = NNU_RAW / "imagesTr"
RAW_LABELS_PATH: Path = NNU_RAW / "labelsTr"

NNU_INFERENCE_PATH: Path = DATA_PATH / "nnUNet_inference"

# dashboard data
DASHBOARD_DATA_PATH: Path = DATA_PATH / "dashboard_data"

T2S_VOLUMES_PATH: Path = DASHBOARD_DATA_PATH / "volumes"
GT_LABELS_PATH: Path = DASHBOARD_DATA_PATH / "labels"
PRED_PATH: Path = DASHBOARD_DATA_PATH / "predictions"
PMAP_PATH: Path = DASHBOARD_DATA_PATH / "probabilities"
ALL_DASHBOARD_FOLDERS: list[Path] = [T2S_VOLUMES_PATH, GT_LABELS_PATH, PRED_PATH, PMAP_PATH]

# files
INFER_EVAL_FILE: str = "evaluation_results.csv"

# extensions
T2S_EXT: str = "_0002.nii.gz"
NIFTI_EXT: str = ".nii.gz"
PMAP_EXT: str = ".npz"

# ui
TP_HEX = "#00FF00"
FP_HEX = "#FF0000"
FN_HEX = "#FFEA00"