
# Task 1: Baseline Pipeline

## Overview

Cerebral microbleed (CMB) detection pipeline using VALDO dataset and nnU-Net v2. The pipeline consists of:

1. **Data Conversion** — Format dataset to nnU-Net specifications
2. **Model Planning & Preprocessing** — Generate preprocessing strategies and cache training data
3. **Model Training** — Train with 5-fold cross-validation
4. **Evaluation** — Evaluate model performance

All code is executed in the `notebooks/iapt.ipynb` notebook.

## Dataset & Setup

**VALDO Dataset:** 72 subjects with T2-weighted 3D brain MRI scans and annotated cerebral microbleed labels.

**Prerequisites:**
- Python 3.11+
- NVIDIA GPU (24GB+ VRAM recommended)
- Virtual environment activated

**nnU-Net Installation:**

```bash
git clone https://github.com/MIC-DKFZ/nnUNet.git
cd nnUNet
pip install -e .
cd ..
```

---

## Pipeline Execution

## Pipeline Execution

### 1. Data Conversion

Loads VALDO MRI scans and annotations, validates consistency, converts to nnU-Net format.

**Output structure:**
```
data/nnUNet_raw/Dataset001_VALDO/
├── imagesTr/
│   ├── VALDO_101_0000.nii.gz
│   └── ...
├── labelsTr/
│   ├── VALDO_101.nii.gz
│   └── ...
├── dataset.json
└── stats.json
```

**Execute in notebook:** Run the "Data Conversion" cell in `notebooks/iapt.ipynb`

---

### 2. Model Planning & Preprocessing

Analyzes dataset characteristics, determines optimal patch size/spacing, caches preprocessed data.

**[WARNING] CPU Intensive**

**Output structure:**
```
data/nnUNet_preprocessed/Dataset001_VALDO/
├── nnUNetPlans.json
├── VALDO_101.npz
└── ...
```

**Execute in notebook:** Run the "Planning & Preprocessing" cell in `notebooks/iapt.ipynb`

---

### 3. Model Training

Trains 5 independent models with 5-fold cross-validation. Each fold trains for 1000 epochs.

** [WARNING] GPU Intensive**

**Output structure:**
```
data/nnUNet_results/Dataset001_VALDO/nnUNetTrainer__nnUNetPlans__3d_fullres/
├── fold_0/checkpoint_best.pth
├── fold_1/...
└── fold_4/...
```

**Execute in notebook:** Run the "Model Training" cell in `notebooks/iapt.ipynb`

---

### 4. Evaluation

Computes metrics on validation predictions. Generates evaluation CSV and probability maps.

**Output:**
- `data/dashboard_data/evaluation_results.csv` — Per-subject metrics
- Prediction probability maps

**Execute in notebook:** Run the "Evaluation" cell in `notebooks/iapt.ipynb`

---

## Interactive Exploration

After evaluation completes:

```bash
streamlit run dashboard.py
```

See [Task 2: Interactive Exploration Dashboard](interactive_exploration_dashboard.md) for more detailed documentation.

---

## Next Steps
Use Interactive Dashboard to explore results

