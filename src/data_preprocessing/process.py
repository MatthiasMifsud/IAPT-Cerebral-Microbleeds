from .create_nnu_data import setup_dataset
import logging

#logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
)

if __name__ == "__main__":
    setup_dataset()