from . import utils
from ..config import IMAGES_DIR, LABELS_DIR
if __name__ == "__main__":
    # creating target data directory
    utils.create_dirs()

    # converting source data to target data
    utils.valdo_to_nnu()

    # adding metadata
    utils.add_metadata()