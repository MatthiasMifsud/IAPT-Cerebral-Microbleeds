import subprocess
import platform
from ..config import K_FOLDS

os_name = platform.system()
if __name__ == "__main__":
    subprocess.run(['cd', 'nnUNet'])
    for k in range(K_FOLDS):
        subprocess.run([
            'nnUNetv2_train', '001', '3d_fullres', 
            str(k), '-device', 'mps'
        ])