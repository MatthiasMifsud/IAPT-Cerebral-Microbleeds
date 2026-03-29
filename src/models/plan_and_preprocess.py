import subprocess
import platform

os_name = platform.system()
if __name__ == "__main__":
    subprocess.run(['cd', 'nnUNet'])
    subprocess.run([
        'nnUNetv2_plan_and_preprocess', 
        '-d', '001', 
        '--verify_dataset_integrity', 
    ])