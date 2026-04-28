from pathlib import Path
import numpy as np
from scipy.ndimage import label
import utils.config as cf
from utils.logger import success, info
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import ListedColormap, to_rgba
from utils.logger import info, setup_logging
setup_logging()

def create_dirs(paths: list[Path] | Path, parents: bool = True, exist_ok: bool = True) -> None:
    if isinstance(paths, Path):
        paths = [paths]

    created = []
    for path in paths:
        if not path.exists():
            created.append(str(path))
        path.mkdir(parents=parents, exist_ok=exist_ok)

    if created:
        success(f"Created {len(created)} directorie(s): {', '.join(created)}")
    else:
        info("All directories already exist")

def nifti_loader(path: Path) -> np.ndarray:
    img = nib.load(path)
    data = img.get_fdata()
    zooms = img.header.get_zooms()
    info(f"--- {path.name} Shape ---")
    info(data.shape)
    info(f"--- {path.name} Affine ---")
    info(img.affine)
    info(f"Orientation: {nib.aff2axcodes(img.affine)}")
    return data, zooms

def pmap_loader(path: Path) -> np.ndarray:
    data = np.load(path)

    if "probabilities" in data:
        prob = data["probabilities"]
        if prob.ndim == 4: # (C, X, Y, Z)
            prob = prob[1]
    else:
        key = list(data.keys())[0]
        prob = data[key]
        if prob.ndim == 4:
            prob = prob[1]

    prob = np.transpose(prob, (1, 2, 0))
    prob = np.rot90(prob, k=-1, axes=(0, 1))
    prob = np.flip(prob, axis=1)
    info(f"--- PMAP Shape ---")
    info(prob.shape)
    return prob.astype(np.float32)

def load_eval_data():
    if not cf.DASHBOARD_DATA_PATH.exists():
        from utils.reorganise import run as reorganise_run
        reorganise_run()
    try:
        return pd.read_csv(cf.DASHBOARD_DATA_PATH / cf.INFER_EVAL_FILE).sort_values(by="subject_id", ascending=True)
    except:
        return pd.DataFrame()

# using logic from the iapt.ipynb evaluation scripts
def classify(prob_map:np.ndarray, gt:np.ndarray, threshold: float):
    bin_preds = (prob_map > threshold).astype(np.int32) # thresholded binary probability map
    bin_gt = (gt > 0).astype(np.int32)

    # 3d structure
    structure = np.ones((3, 3, 3), dtype=np.uint8)

    # getting connected components
    pred_labels, n_preds = label(bin_preds, structure=structure)
    gt_labels, n_gts = label(bin_gt, structure=structure)

    # init boolean label masks 
    tp_mask = np.zeros_like(pred_labels, dtype=bool) # green
    fp_mask = np.zeros_like(pred_labels, dtype=bool) # red
    fn_mask = np.zeros_like(gt_labels, dtype=bool) # yellow

    # initialisation
    overlap_pred_label = np.array([])
    overlap_gt_label = np.array([])
    detected_preds = 0
    detected_gts = 0

    if n_preds > 0 and np.any(bin_gt):
        # finding id of pred components that overlap the gt mask
        overlap_pred_label = np.unique(pred_labels[bin_gt > 0])
        overlap_pred_label = overlap_pred_label[overlap_pred_label > 0] # reomving the background

        detected_preds = len(overlap_pred_label)

        # populating masks
        if len(overlap_pred_label) > 0:
            tp_mask = np.isin(pred_labels, overlap_pred_label)

    fp_mask = np.logical_and(bin_preds > 0, ~tp_mask)

    if n_gts > 0:
        if np.any(bin_preds):
            overlap_gt_label = np.unique(gt_labels[bin_preds > 0])
            overlap_gt_label = overlap_gt_label[overlap_gt_label > 0]

            detected_gts = len(overlap_gt_label)  

            detected_gt_mask = np.isin(gt_labels, overlap_gt_label)
            fn_mask = np.logical_and(bin_gt > 0, ~detected_gt_mask)
        else:
            fn_mask = (bin_gt > 0)   

    fp = n_preds - detected_preds
    fn = n_gts - detected_gts
    tp = detected_gts

    return tp_mask.astype(np.int32), fp_mask.astype(np.int32), fn_mask.astype(np.int32), tp, fp, fn

def _create_overlay_cmap(hex_color: str, alpha: float = 0.7) -> ListedColormap:
    color = to_rgba(hex_color, alpha=alpha)
    transparent = (0.0, 0.0, 0.0, 0.0)
    
    return ListedColormap([transparent, color])

def slice_renderer(
    t2s_img: np.ndarray, 
    tp: np.ndarray, fp: np.ndarray, fn: np.ndarray, 
    slice_idx: int, axis: int, zooms: float, seg: bool = True):
    """Renders one slice with colored metrics"""

    # logic for that slice
    img_slice = t2s_img.take(slice_idx, axis=axis).T
    tp_slice = tp.take(slice_idx, axis=axis).T
    fp_slice = fp.take(slice_idx, axis=axis).T
    fn_slice = fn.take(slice_idx, axis=axis).T

    # calc aspect ratio (keeping in mind the transpose) vertical/horiz
    # zoom (dx, dy, dz)
    if axis == 0: # sagittal
        ar = zooms[2] / zooms[1]
    elif axis == 1: # coronal
        ar = zooms[2] / zooms[0]
    else: # axial
        ar = zooms[1] / zooms[0]

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100, facecolor="None")
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.axis("off")

    vmax = np.percentile(img_slice, 99.5) if np.any(img_slice) else 1
    ax.imshow(img_slice, cmap="gray", origin="lower", vmin=0, vmax=vmax, aspect=ar)
    
    overlay_param = {"origin":"lower", "vmin":0, "vmax":1, "aspect":ar, "interpolation":"nearest"} # interpolation nearest for no smoothing hence better and more precise masks

    if seg:
        if np.any(tp_slice):
            ax.imshow(tp_slice, cmap=_create_overlay_cmap(cf.TP_HEX), **overlay_param)
            
        if np.any(fp_slice):
            ax.imshow(fp_slice, cmap=_create_overlay_cmap(cf.FP_HEX), **overlay_param)
            
        if np.any(fn_slice):
            ax.imshow(fn_slice, cmap=_create_overlay_cmap(cf.FN_HEX), **overlay_param)
        

    p_bbox = FancyBboxPatch(
        (0, 0), 1, 1, 
        boxstyle="round,pad=0,rounding_size=0.05", 
        ec="none", fc="none", 
        transform=ax.transAxes
    )
    ax.add_patch(p_bbox)

    for img in ax.get_images():
        img.set_clip_path(p_bbox)

    border = FancyBboxPatch(
        (0, 0), 1, 1, 
        boxstyle="round,pad=0,rounding_size=0.05", 
        edgecolor='#333333', facecolor='none', lw=2,
        transform=ax.transAxes, zorder=10
    )
    ax.add_patch(border)
    plt.tight_layout(pad=0)
    return fig