# -*- coding: utf-8 -*-
"""Helper utilities for logging."""
import logging
import sys
import time


def configure_logging() -> None:
    """Apply standard configuration to logging."""
    logging.Formatter.converter = time.gmtime  # ensure all logging timestamps are UTC
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s UTC] %(name)s-{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
    )
