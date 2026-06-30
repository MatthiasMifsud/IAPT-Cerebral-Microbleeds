# Data Folder Setup

The real dataset and generated nnU-Net outputs are intentionally excluded from this repository because they are too large for submission.

Create the following folders locally before running the notebook pipeline or dashboard.

## Dashboard-Only Setup

Use this path if you already have the converted nnU-Net data and inference outputs.

```text
data/
├── nnUNet_raw/
│   └── Dataset001_VALDO/
│       ├── imagesTr/
│       │   ├── VALDO_101_0002.nii.gz
│       │   └── ...
│       └── labelsTr/
│           ├── VALDO_101.nii.gz
│           └── ...
└── nnUNet_inference/
    ├── VALDO_101.nii.gz
    ├── VALDO_101.npz
    ├── evaluation_results.csv
    └── ...
```

Then run:

```bash
streamlit run dashboard.py
```

On first launch, the dashboard creates `data/dashboard_data/` automatically by copying the required volumes, labels, predictions, probability maps, and evaluation CSV into a dashboard-friendly structure.

If `data/dashboard_data/` already exists, it will not be regenerated. Delete `data/dashboard_data/` before rerunning the dashboard if you replace the source data.

## Full Pipeline Setup

Use this path if you are starting from the original VALDO Challenge training data. The notebook conversion code expects the Task 2 CMB dataset here:

```text
data/
└── original_dataset/
    └── Task2/
        ├── sub-101/
        │   ├── sub-101_space-T2S_desc-masked_T2S.nii.gz
        │   ├── sub-101_space-T2S_desc-masked_T2.nii.gz
        │   ├── sub-101_space-T2S_desc-masked_T1.nii.gz
        │   └── sub-101_space-T2S_desc-masked_CMB.nii.gz
        ├── sub-102/
        └── ...
```

After placing the original dataset, run the cells in `notebooks/iapt.ipynb`. The data conversion step reads `data/original_dataset/Task2/` and creates the nnU-Net training folders automatically.

Expected generated folders:

```text
data/
├── original_dataset/
├── nnUNet_raw/
├── nnUNet_preprocessed/
├── nnUNet_results/
├── nnUNet_inference/
└── dashboard_data/
```
