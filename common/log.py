import os
import cv2
import json
import datetime
import base64
import logging
import numpy as np
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from threading import Lock

LOG_BASE_PATH = '../log/'
now = datetime.datetime.now()
nowtime = now.strftime("%Y-%m-%d")
LOG_PATH = LOG_BASE_PATH + nowtime + "/"
try:
    os.makedirs(LOG_PATH, exist_ok=True)
except Exception as e:
    pass


class LoggerProject(object):

    def __init__(self, name):
        self.mutex = Lock()
        self.name = name
        self.formatter = '%(asctime)s -<>- %(filename)s -<>- [line]:%(lineno)d -<>- %(levelname)s -<>- %(message)s'

    def _create_logger(self):
        _logger = logging.getLogger(self.name + __name__)
        _logger.setLevel(level=logging.INFO)
        return _logger

    def _file_logger(self):
        time_rotate_file = TimedRotatingFileHandler(filename=LOG_BASE_PATH + self.name, when='D', interval=1,
                                                    backupCount=30)
        time_rotate_file.setFormatter(logging.Formatter(self.formatter))
        time_rotate_file.setLevel(logging.INFO)
        return time_rotate_file

    def _console_logger(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level=logging.INFO)
        console_handler.setFormatter(logging.Formatter(self.formatter))
        return console_handler

    def pub_logger(self):
        logger = self._create_logger()
        self.mutex.acquire()
        logger.addHandler(self._file_logger())
        logger.addHandler(self._console_logger())
        self.mutex.release()
        return logger


log_api = LoggerProject('Langchain-ChatBI')
logger = log_api.pub_logger()
