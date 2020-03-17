# -*- coding: utf-8 -*-
"""Helper utilities for logging."""
import datetime
import logging
import os
import sys
import time
from typing import Optional

from .misc import create_directory_if_not_exists
from .misc import resource_path


def configure_logging(
    log_file_prefix: Optional[str] = None, log_level: int = logging.INFO
) -> None:
    """Apply standard configuration to logging.

    Args:
        log_file_prefix: if set, will write logs to file in a subfolder (logs). By default it will create a subfolder in the current working directory (if running from source) or in the path that the EXE was installed to for pyinstaller.
        log_level: set the desired logging threshold level
    """
    logging.Formatter.converter = time.gmtime  # ensure all logging timestamps are UTC
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]
    if log_file_prefix is not None:
        log_folder = resource_path("logs", base_path=os.getcwd())
        create_directory_if_not_exists(log_folder)
        file_handler = logging.FileHandler(
            os.path.join(
                log_folder,
                f'{log_file_prefix}__{datetime.datetime.utcnow().strftime("%Y_%m_%d_%H%M%S")}.txt',
            )
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s UTC] %(name)s-{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
    )
