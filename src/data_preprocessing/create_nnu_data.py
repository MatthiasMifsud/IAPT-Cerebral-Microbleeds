import logging
import shutil
import json
from ..config import ORIG_DATA, DATASET_DIR, IMAGES_DIR, LABELS_DIR, SUBJECT_PREFIX, DATASET_SIZE

logger = logging.getLogger(__name__)

def _create_dirs() -> None:
    created = []
    for dir in [IMAGES_DIR, LABELS_DIR]:
        if not dir.exists():
            created.append(str(dir))
        dir.mkdir(parents=True, exist_ok=True) #on each run it recreates the directory
    
    if created:
        logger.info(f"ℹ️ Created {len(created)} directories: {', '.join(created)}")
    else:
        logger.info("ℹ️ Directories already exist")

def _valdo_to_nnu() -> None:
    logger.info(f"ℹ️ Converting Valdo Dataset to fit nnUNet format")

    subjects = [f for f in ORIG_DATA.iterdir() if f.is_dir() and f.name.startswith(SUBJECT_PREFIX)] # 72 subjects
    
    sub_count = 0
    failed_sub = []

    for sub_dir in subjects: # iterating over all 72 subjects
        sub_id = sub_dir.name
        id = sub_id.replace(SUBJECT_PREFIX, "")

        # creating mappings (orig name: dest path)
        mappings = {
            # label
            f"{sub_id}_space-T2S_CMB.nii.gz": LABELS_DIR / f"VALDO_{id}.nii.gz",
            # images
            f"{sub_id}_space-T2S_desc-masked_T1.nii.gz": IMAGES_DIR / f"VALDO_{id}_0000.nii.gz", # T1
            f"{sub_id}_space-T2S_desc-masked_T2.nii.gz": IMAGES_DIR / f"VALDO_{id}_0001.nii.gz", # T2
            f"{sub_id}_space-T2S_desc-masked_T2S.nii.gz": IMAGES_DIR / f"VALDO_{id}_0002.nii.gz", # T2S
        }

        # moving the files
        mv_count = 0
        for orig_name, target_path in mappings.items():
            file_path = sub_dir / orig_name
            if file_path.exists():
                shutil.copy2(file_path, target_path)
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

    if sub_count != DATASET_SIZE:
        raise ValueError(f"Dataset size mismatch. Expected: {DATASET_SIZE}, Got: {sub_count}.")

def _add_metadata() -> None:
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
        "numTraining": DATASET_SIZE, 
        "file_ending": ".nii.gz" 
    }

    meta_path = DATASET_DIR / "dataset.json"
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    logger.info(f"ℹ️ Added metadata to {str(meta_path)}.")

def setup_dataset():
    logger.info(f"ℹ️ Starting nnUNet dataset setup...")
    # creating target data directory
    _create_dirs()

    # converting source data to target data
    _valdo_to_nnu()

    # adding metadata
    _add_metadata()
    logger.info("ℹ️ Successfully finished setting up the nnUNet dataset.")