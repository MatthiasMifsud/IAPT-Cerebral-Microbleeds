import logging
import nibabel as nib
from pathlib import Path
import json
from .config import (
    ORIG_DATA_PATH, SUBJECT_PREFIX, DATA_TYPE,
    MODALITY_SUFFIXES, LABELS_PATH, IMAGES_PATH,
    DATASET_PATH, METADATA_FILE, create_dirs
)

#logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
)
nib.imageglobals.logger.setLevel(logging.WARNING) 
logging.getLogger('nibabel').setLevel(logging.WARNING) # supressing warnings that are being fixed in the script
logger = logging.getLogger(__name__)

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
print(ROOT_DIR)
DATA_DIR: Path = ROOT_DIR / "data"

def valdo_to_nnu() -> int:
    logger.info(f"ℹ️ Converting Valdo Dataset to fit nnUNet format")

    subjects = [f for f in ORIG_DATA_PATH.iterdir() if f.is_dir() and f.name.startswith(SUBJECT_PREFIX)] # 72 subjects
    
    sub_count = 0
    failed_sub = []

    for sub_dir in subjects: # iterating over all 72 subjects
        sub_id = sub_dir.name
        id = sub_id.replace(SUBJECT_PREFIX, "")

        # creating mappings (orig name: dest path)
        mappings = {
            # label
            f"{sub_id}_space-T2S_CMB{DATA_TYPE}": LABELS_PATH / f"VALDO_{id}{DATA_TYPE}",
            # images
            f"{sub_id}_space-T2S_desc-masked_T1{DATA_TYPE}": IMAGES_PATH / f"VALDO_{id}_{MODALITY_SUFFIXES[0]}{DATA_TYPE}", # T1
            f"{sub_id}_space-T2S_desc-masked_T2{DATA_TYPE}": IMAGES_PATH / f"VALDO_{id}_{MODALITY_SUFFIXES[1]}{DATA_TYPE}", # T2
            f"{sub_id}_space-T2S_desc-masked_T2S{DATA_TYPE}": IMAGES_PATH / f"VALDO_{id}_{MODALITY_SUFFIXES[2]}{DATA_TYPE}", # T2S
        }

        # moving the files
        mv_count = 0
        for orig_name, target_path in mappings.items():
            file_path = sub_dir / orig_name
            if file_path.exists():
                # saving through nibabel to fix pixdim[0] qfac warning (warning fix)
                img = nib.load(file_path)
                nib.save(img, target_path)
                mv_count += 1
            else:
                logger.warning(f"⚠️ Missing file '{orig_name}' in '{sub_id}'")

        if mv_count == 4:
            sub_count += 1
            logger.debug(f"🔍 Successfully processed '{sub_id}'")
        else:
            logger.error(f"❌ Subject '{sub_id}' is incomplete. Found {mv_count}/4 files.")
            failed_sub.append(sub_id)

    if failed_sub:
        logger.error(f"❌ Failed to process the following subjects: {failed_sub}")

    return sub_count

def add_metadata(dataset_size) -> None:
    metadata = { 
        "channel_names": { 
            "0": "T1", 
            "1": "T2", 
            "2": "T2star" 
        }, 
        "labels": { 
            "background": 0, 
            "microbleed": 1 
        }, 
        "numTraining": dataset_size, 
        "file_ending": ".nii.gz" 
    }

    meta_path = DATASET_PATH / METADATA_FILE
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    logger.info(f"ℹ️ Added metadata to {str(meta_path)}.")

if __name__ == "__main__":
    logger.info(f"ℹ️ Starting nnUNet dataset setup...")
    # creating target data directory
    create_dirs([IMAGES_PATH, LABELS_PATH])
    # converting source data to target data
    dataset_size = valdo_to_nnu()
    # adding metadata
    add_metadata(dataset_size)
    logger.info("✅ Successfully finished setting up the nnUNet dataset.")