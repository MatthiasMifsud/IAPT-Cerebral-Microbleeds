# IAPT Cerebral Microbleeds

---

## Running project

### MacOS

```bash
python3.11 -m venv iapt_env
source iapt_env/bin/activate
pip install -r requirements.txt
```

---

## Commands

### Preprocessing 

During the preprocessing the dataset is converted to the nnUNet format
and a metadata JSON file is generated. 

Additionally we also have verification of the subjects in the dataset and
after verification, a summary of the subjects is stored as JSON.

```
python3 -m src.data_preprocessing.process
```

---

## Citations

[nnUNet](https://github.com/mic-dkfz/nnunet?tab=readme-ov-file)
[medial imaging libs](https://pycad.medium.com/the-best-python-libraries-for-medical-imaging-3327df061c0a)
[nibabel](https://nipy.org/nibabel/reference/nibabel.dataobj_images.html)
---