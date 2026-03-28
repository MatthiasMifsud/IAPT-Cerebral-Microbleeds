from .create_nnu_data import setup_dataset
from .label_verification import LabelVerification
import logging

#logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
)
logging.getLogger('nibabel.nifti1').setLevel(logging.WARNING)


if __name__ == "__main__":
    verifier = LabelVerification()

    setup_dataset()
    verifier.verify_labels()