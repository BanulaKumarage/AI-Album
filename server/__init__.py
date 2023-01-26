
"""
Server side code for AI-ALBUM
"""

__title__ = 'AI-ALBUM'
__version__ = VERSION = '0.0.1'
__author__ = 'Anuradha Wickramarachchi'
__license__ = 'TBD'
__copyright__ = 'TBD'


import logging
import warnings
from logging.config import dictConfig
from pathlib import Path
import yaml
import sys
import pathlib
import os


logging.captureWarnings(True)
warnings.simplefilter("default")


# TODO attach this bit to indexer
SUPPORTED_IMAGE_FORMATS = ['jpeg', 'jpg', 'NEF', 'GPR']
CWD = pathlib.Path(os.getcwd())
LAVIS = str(pathlib.Path(CWD).joinpath('LAVIS'))

sys.path.append(LAVIS)

def load_logger():
    log_file = Path(__file__).parent / "logger.yml"

    with open(log_file, 'r') as stream:
        dictConfig(yaml.safe_load(stream))