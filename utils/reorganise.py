from . import config as cf
from .helpers import create_dirs
from .logger import info, success, setup_logging
import shutil

# creating necessary dirs
def run():
    info("Starting file reorganisation for the dashboard")
    create_dirs(cf.ALL_DASHBOARD_FOLDERS)

    info("Copying T2* Volumes...")
    t2s_count = 0
    for file in cf.RAW_IMAGES_PATH.glob("*_0002.nii.gz"):
        t2s_count += 1
        shutil.copy2(file, cf.T2S_VOLUMES_PATH / file.name)

    info("Copying Ground Truth Labels...")
    gt_lab_count = 0
    for file in cf.RAW_LABELS_PATH.glob("*.nii.gz"):
        gt_lab_count += 1
        shutil.copy2(file, cf.GT_LABELS_PATH / file.name)

    info("Copying Predictions and Probability Maps...")
    pred_count = 0
    prob_count = 0
    for file in cf.NNU_INFERENCE_PATH.glob("*"):
        if file.name.endswith(".nii.gz"):
            pred_count += 1
            shutil.copy2(file, cf.PRED_PATH / file.name)
        elif file.name.endswith(".npz"):
            prob_count += 1
            shutil.copy2(file, cf.PMAP_PATH / file.name)
        elif file.name == cf.INFER_EVAL_FILE:
            shutil.copy2(file, cf.DASHBOARD_DATA_PATH / file.name)

    success(f"File reorganisation complete | Counts - T2s Volumes: {t2s_count}, GT_Labels: {gt_lab_count}, Predictions: {pred_count}, Probabilities: {prob_count}")

if __name__ == "__main__":
    setup_logging()
    run()