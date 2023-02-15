
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
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from pillow_heif import register_heif_opener


logging.captureWarnings(True)

warnings.simplefilter("default")


# TODO attach this bit to indexer
SUPPORTED_IMAGE_FORMATS = ['jpeg', 'jpg', 'NEF', 'GPR']
CWD = pathlib.Path(os.getcwd())
LAVIS = pathlib.Path(CWD).joinpath('LAVIS').as_posix()
DLIB = next(pathlib.Path(CWD).joinpath('dlib').glob('dist/*.egg')).as_posix()
FACE_RECOGNITION_MODELS = pathlib.Path(CWD).joinpath('face_recognition_models').as_posix()
FACE_RECOGNITION = pathlib.Path(CWD).joinpath('face_recognition').as_posix()

sys.path.append(LAVIS)
sys.path.append(DLIB)
sys.path.append(FACE_RECOGNITION_MODELS)
sys.path.append(FACE_RECOGNITION)


def load_logger():
    log_file = Path(__file__).parent / "logger.yml"

    with open(log_file, 'r') as stream:
        dictConfig(yaml.safe_load(stream))

thread_pool_executor = ThreadPoolExecutor(max_workers=8)
process_pool_executor = ProcessPoolExecutor(max_workers=8)

load_logger()
register_heif_opener()
