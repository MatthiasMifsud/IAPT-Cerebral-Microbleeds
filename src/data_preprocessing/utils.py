from ..config import ORIG_DATA, DATASET_DIR, IMAGES_DIR, LABELS_DIR, SUBJECT_PREFIX, DATASET_SIZE
import shutil
import json

def create_dirs():
    created = []
    for dir in [IMAGES_DIR, LABELS_DIR]:
        if not dir.exists():
            created.append(str(dir))
        dir.mkdir(parents=True, exist_ok=True)
    
    created_len = len(created)
    if created_len > 0:
        print(f"Created {created_len} directories: {', '.join(created)}")
    else:
        print(f"Directories already exist")

def valdo_to_nnu():
    print(f"Converting from Valdo Dataset {ORIG_DATA}...")

    subjects = [f for f in ORIG_DATA.iterdir() if f.is_dir()] # 72 subjects
    sub_count = 0
    for sub_dir in subjects: # iterating over all 72 subjects
        sub_id = sub_dir.name # getting folder names
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

        # movinf the files
        mv_count = 0
        for orig_name, target_path in mappings.items():
            file_path = sub_dir / orig_name
            if file_path.exists():
                shutil.copy(file_path, target_path)
                mv_count += 1
            else:
                print(f"Warining: {orig_name} not found.")

        if mv_count == 4:
            sub_count += 1
            print(f"processed {sub_id}")
        else:
            print(f"Warning: {sub_id} does not have all required files (T1, T2, T2* images and label mask)")

    if sub_count != DATASET_SIZE:
        raise ValueError(f"The added subjects are not equal to the required dataset size: we want: {DATASET_SIZE} got: {sub_count}")

def add_metadata():
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

    with open(DATASET_DIR / "dataset.json", 'w') as f:
        json.dump(metadata, f, indent=4)
    print("Added metadata.")