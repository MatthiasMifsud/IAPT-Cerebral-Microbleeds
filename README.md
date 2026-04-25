# IAPT: Benchmarking Small-Object Detection on Brain MRI: A Cerebral Microbleed Case Study

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Framework](https://img.shields.io/badge/framework-nnU--Net_v2-green)

---

## Getting Started

### Prerequisite

- **Python:** 3.11+

- **Hardware:** High-performance CPU for preprocessing; High-performance GPU
for model training.

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

### 2. Integrating nnU-Net v2

This project makes use of the nnU-Net Framework and is added to the project 
itself to allow for adjustemnts of the framework if needed.

```shell
# clone the repository
git clone https://github.com/MIC-DKFZ/nnUNet.git

# install its requirements
cd nnUNet
pip install -e .
cd ..
```

---

## Execution

### 1. Data Conversion

During this step, the dataset is structured to the nnU-Net format and a 
metadata JSON file is generated. Additionally we also have verification of 
the subjects in the dataset and after verification, a summary of the subjects 
is stored as JSON.

```shell
python -m scripts.conversion
```

* Outputs: Standardized dataset and a `stats.json` statistical summary.

### 2. Model Planning & Preprocessing

This command analyses the dataset and generates a preprocessing plan. 
It computes target spacing, intensity normalisation statistics, patch sizes,
and architecture configurations. It then preprocesses all 72 training cases
accordingly. This step is CPU-bound, not GPU-bound.

```shell
python -m src.models.plan_and_preprocess
```

[!CAUTION] WARNING: This is highly CPU intensive.

### 3. Model Training

Configure and train nnU-Net using its default 3D full-resolution 
configuration with five-fold cross-validation on the VALDO training set.

```shell
python -m src.models.training
```

[!CAUTION] WARNING: This is highly GPU intensive.

---

## References & Citations
* [Logger](https://github.com/MatthiasMifsud/Utility/blob/main/logger)
* [nnUNet](https://github.com/mic-dkfz/nnunet?tab=readme-ov-file)
* [Python Libraries for Medical Imaging](https://pycad.medium.com/the-best-python-libraries-for-medical-imaging-3327df061c0a)
* [NiBabel Documentation](https://nipy.org/nibabel/reference/nibabel.dataobj_images.html)
* Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2021). [nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation.](https://www.nature.com/articles/s41592-020-01008-z) Nature methods, 18(2), 203-211

---