import nibabel as nib
import numpy as np
from scipy.ndimage import label
import json
from ..utils.directories import _create_dirs
from ..config import (
    IMAGES_DIR, LABELS_DIR, DATA_TYPE, 
    MODALITY_SUFFIXES, STATS_DIR, DATASET_DIR,
    METADATA_FILE
)
import logging
logger = logging.getLogger(__name__)

class LabelVerification:
    def __init__(self):
        self.corrupt_lbls = []
        self.misaligned_lbls = set()
        self.missing_mod = set()
        self.component_stats = {}

        try:
            with open(DATASET_DIR / METADATA_FILE, 'r') as file:
                data = json.load(file)
                self.dataset_size = data.get('numTraining', 0)
        except Exception as e:
            logger.error(f"❌ Failed to load {METADATA_FILE}: {e}")
            self.dataset_size = 0

    def _lbl_val_integrity(self, sub_id:str, lbl_data) -> bool:
        unique_vals = np.unique(lbl_data)
        if not np.all(np.isin(unique_vals, [0, 1])):
            logger.error(f"❌ Label for '{sub_id}' is corrupt.")
            self.corrupt_lbls.append(sub_id)
            return False
        return True
        
    def _spatial_alignment(self, sub_id:str, lbl_img) -> None:
        for mod in MODALITY_SUFFIXES:
            img_path = IMAGES_DIR / f"{sub_id}_{mod}{DATA_TYPE}"

            if not img_path.exists():
                logger.error(f"❌ Missing Modality: '{sub_id}' is missing '{mod}'")
                self.missing_mod.add(f"{sub_id}_{mod}")
                continue

            img = nib.load(img_path)
            
            # dimension check
            if img.shape != lbl_img.shape:
                logger.error(f"❌ Dimension Mismatch: '{sub_id}' ({mod})")
                self.misaligned_lbls.add(f"{sub_id}_{mod}")

            # spatial mapping check
            if not np.allclose(img.affine, lbl_img.affine, atol=1e-3):
                logger.error(f"❌ Affine Matrix Mismatch: '{sub_id}' ({mod})")
                self.misaligned_lbls.add(f"{sub_id}_{mod}")
        
    def _compute_connected_component(self, sub_id: str, lbl_img, lbl_data) -> None:
        # lbl_data == 1 is a microbleed
        label_mask, bleeds_count = label(lbl_data == 1)

        bleed_volumes = []
        voxel_spacing = ()

        # positive cases
        if bleeds_count > 0:
            # calc dimentions of bleed
            voxel_spacing = lbl_img.header.get_zooms()[:3] # ignoring 4th dim (time dim for fmri
            # get vol of each voxel
            voxel_vol = np.prod(voxel_spacing)

            # get size of each bleed (in voxel)
            bleed_sizes = np.bincount(label_mask.ravel())[1:] #skipping background dim (0s)
            # converting the bleed sizes to volumes
            bleed_volumes = (bleed_sizes * voxel_vol).tolist()  
        
        self.component_stats[sub_id] = {
            'microbleed_count': int(bleeds_count),
            'microbleed_vol_mm3': [float(i) for i in bleed_volumes],
            'total_microbleed_vol_mm3': float(np.sum(bleed_volumes)),
            'voxel_spacing': tuple(float(i) for i in voxel_spacing),
            'max_bleed_vol_mm3': float(max(bleed_volumes)) if bleed_volumes else 0.0,
            'min_bleed_vol_mm3': float(min(bleed_volumes)) if bleed_volumes else 0.0,
        }
        
    def verify_labels(self) -> None:
        lbl_files = list(LABELS_DIR.glob(f"*{DATA_TYPE}"))
        lbl_size = len(lbl_files)

        if len(lbl_files) == 0:
            logger.error("❌ No label files found.")
            return

        # fail if we cannot extract all of the labels
        if lbl_size != self.dataset_size:
            logger.error(f"❌ Extraced only {lbl_size}/{self.dataset_size} labels.")
            return
        
        logger.info(f"ℹ️ Starting label verification for {self.dataset_size} subjects...")
        for lbl_path in lbl_files:
            sub_id = lbl_path.name.replace(DATA_TYPE, "")
            
            try:
                lbl_img = nib.load(lbl_path)
                lbl_data = np.asanyarray(lbl_img.dataobj)
            except Exception as e:
                logger.error(f"❌ Failed to load {sub_id}: {e}")
                self.corrupt_lbls.append(sub_id)
                continue
                    
            # label val integrity
            if not self._lbl_val_integrity(sub_id, lbl_data):
                continue
                
            # spatial alignment
            self._spatial_alignment(sub_id, lbl_img)

            # connected component statistics
            self._compute_connected_component(sub_id, lbl_img, lbl_data)

        logger.info(f"Verification Summary")

        if not self.corrupt_lbls and not self.misaligned_lbls and not self.missing_mod:
            logger.info("✅ All checks passed succesfully")
            return
        logger.warning(f"⚠️ Issues found: {len(self.corrupt_lbls)} corrupt labels, {len(self.misaligned_lbls)} misaligned labels, {len(self.missing_mod)} missing modalities")

    def generate_summary(self) -> None:
        if not self.component_stats:
            logger.warning("⚠️ No statistics detected.")
            return

        stats = self.component_stats
        summary = {
            'total_subjects': len(stats),
            'statistics': stats
        }

        path = STATS_DIR / "stats.json"
        _create_dirs([STATS_DIR])
        with open(path, 'w') as f:
            json.dump(summary, f, indent=4)
        logger.info(f"ℹ️ Statistics saved to {path}")