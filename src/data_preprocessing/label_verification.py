import nibabel as nib
import numpy as np
from scipy.ndimage import label
from pathlib import Path
from ..config import IMAGES_DIR, LABELS_DIR, DATA_TYPE, DATASET_SIZE, MODALITY_SUFFIXES
import logging

logger = logging.getLogger(__name__)

class LabelVerification:
    def __init__(self):
        self.corrupt_lbls = []
        self.misaligned_lbls = set()
        self.missing_mod = []
        self.component_stats = {}

    def _lbl_val_integrity(self, sub_id:str, lbl_data) -> list:
        unique_vals = np.unique(lbl_data)
        if not np.all(np.isin(unique_vals, [0, 1])):
            logger.error(f"❌ Label for '{sub_id}' is corrupt.")
            self.corrupt_lbls.append(sub_id)
        
    def _spatial_alignment(self, sub_id:str, lbl_img):
        for mod in MODALITY_SUFFIXES:
            img_path = IMAGES_DIR / f"{sub_id}_{mod}{DATA_TYPE}"

            if not img_path.exists():
                logger.error(f"❌ Missing Modality: '{sub_id}' is missing '{mod}'")
                self.missing_mod.append(f"{sub_id}_{mod}")
                continue

            img = nib.load(img_path)
            
            # dimension check
            if img.shape != lbl_img.shape:
                logger.error(f"❌ Dimesion Mismatch: '{sub_id}' ({mod})")
                self.misaligned_lbls.add(f"{sub_id}_{mod}")

            # spatial mapping check
            if not np.allclose(img.affine, lbl_img.affine, atol=1e-3):
                logger.error(f"❌ Affine Matrix Mismatch: '{sub_id}' ({mod})")
                self.misaligned_lbls.add(f"{sub_id}_{mod}")
        
    def _compute_connected_component(self, sub_id: str, lbl_img, lbl_data):
        # lbl_data == 1 is a microbleed
        label_mask, bleeds_count = label(lbl_data == 1)

        bleed_volumes = []

        # positive cases
        if bleeds_count > 0:
            # calc dimentions of bleed

            voxel_3dims = lbl_img.header.get_zooms()[:3] # ignoring 4th dim (time dim for fmri)
            
            # get vol of each voxel
            voxel_vol = np.prod(voxel_3dims)

            # get size of each bleed (in voxel)
            bleed_sizes = np.bincount(label_mask.ravel())[1:] #skipping background dim (0s)

            # converting the bleed sizes to volumes
            bleed_volumes = bleed_sizes * voxel_vol  
        
        self.component_stats[sub_id] = {
            'count': bleeds_count,
            'sizes_mm3': list(bleed_volumes)
        }
        
    def verify_labels(self):
        lbl_files = list(LABELS_DIR.glob(f"*{DATA_TYPE}"))
        lbl_size = len(lbl_files)

        # fail if we cannot extract all of the labels
        if lbl_size != DATASET_SIZE:
            logger.error(f"❌ Extraced only {lbl_size}/{DATASET_SIZE} labels.")
            return
        
        logger.info(f"ℹ️ Starting label verification for {DATASET_SIZE} subjects...")
        for lbl_path in lbl_files:
            sub_id = lbl_path.name.replace(DATA_TYPE, "")
            lbl_img = nib.load(lbl_path)
            lbl_data = np.asanyarray(lbl_img.dataobj)
        
            # label val integrity
            self._lbl_val_integrity(sub_id, lbl_data)
                
            # spatial alignment
            self._spatial_alignment(sub_id, lbl_img)

            # connected component statistics
            self._compute_connected_component(sub_id, lbl_img, lbl_data)

        logger.info(f"Verification Summary")
        if not self.corrupt_lbls and not self.misaligned_lbls and not self.missing_mod:
            logger.info("✅ All checks passed succesfully!")
        else:
            logger.warning(f"⚠️ Issues found: {len(self.corrupt_labels)} corrupt labels, {len(self.misaligned_labels)} misaligned labels, {len(self.missing_modalities)} missing modalities.")