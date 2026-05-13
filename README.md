# IAPT: Benchmarking Small-Object Detection on Brain MRI: A Cerebral Microbleed Case Study

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Framework](https://img.shields.io/badge/framework-nnU--Net_v2-green)

## Overview

This project benchmarks cerebral microbleed detection on brain MRI using the VALDO dataset and nnU-Net v2. It includes:

- **Task 1:** Dataset preparation, nnU-Net training, inference, and evaluation.
- **Task 2:** Interactive Streamlit dashboard for visualising the model output and performance.

---

## Documentation

- [**Task 1: Baseline Pipeline**](docs/shared_core.md) data preparation, model training, inference, and evaluation workflow
- [**Task 2: Interactive Exploration Dashboard**](docs/interactive_exploration_dashboard.md) — Web-based visualization and performance analysis tool

---

## Getting Started

### Prerequisite

- **Python:** 3.11+

- **Hardware:** High-performance CPU for preprocessing; High-performance GPU for model training.

### 1. Environment Setup

Create a virtual environment for dependancy management

#### macOS / Linux

```shell
# create and activate the environment
python3.11 -m venv iapt_env
source iapt_env/bin/activate

# upgrade pip and install the requirements
pip install -upgrade pip
pip install -r requirements.txt
```

#### Windows

```shell
# Create the environment
python -m venv iapt_env

# Activate the environment
.\iapt_env\Scripts\activate

# Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Quick Start: Interactive Dashboard

After model training and inference are complete, explore the results interactively:

```bash
# Ensure your environment is activated
source iapt_env/bin/activate  # macOS/Linux

# Run the dashboard
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501` and provides the following tabs:

- **Per-Subject Viewer:** Slice-by-slice exploration with real-time probability threshold adjustment.
- **Dataset Summary:** Aggregate statistics and sortable performance table.
- **Graph Analytics:** Visualizations of model performance.

For comprehensive documentation including classification algorithm details, setup instructions, and performance analysis, see [Interactive Exploration Dashboard](docs/interactive_exploration_dashboard.md).

---

## Project Structure

```
CMB_Detection/
├── dashboard.py                # Interactive Exploration Dashboard
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation file
├── docs/
│   ├── shared_core.md          # Task 1: Shared Core documentation
│   └── interactive_exploration_dashboard.md  # Task 2: Interactive Dashboard documentation
├── data/
│   ├── nnUNet_raw/             # Raw dataset in nnU-Net format
│   ├── nnUNet_preprocessed/    # Preprocessed training data
│   ├── nnUNet_results/         # Trained models and training logs
│   ├── nnUNet_inference/       # Inference outputs
│   └── dashboard_data/         # Processed data for visualization
├── notebooks/
│   └── iapt.ipynb              # The entirety of task 1 code
├── utils/                      # Utility modules
│   ├── config.py               # Configuration and paths
│   ├── helpers.py              # Data loading and visualization
│   ├── logger.py               # Logging utilities
│   └── reorganise.py           # Data reorganization scripts
└── iapt_env/                   # Python virtual environment
```

---

## Dataset

The **VALDO Dataset** consists of 72 subjects with T2-weighted brain MRI scans and expert-annotated cerebral microbleed labels.

For detailed dataset information, see [Task 1: Baseline Pipeline](docs/shared_core.md).

---

## Research Report

For a detailed walkthrough on the research please visit the [Report](/docs/report.pdf).

---