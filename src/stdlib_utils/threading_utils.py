# -*- coding: utf-8 -*-
"""Controlling communication with the OpalKelly FPGA Boards."""
import queue
import threading
from typing import Optional

from .parallelism_utils import InfiniteLoopingParallelismMixIn


class InfiniteThread(InfiniteLoopingParallelismMixIn, threading.Thread):
    """Thread for running infinitely in the background.

    Contains some enhanced functionality for stopping.

    Args:
        fatal_error_reporter: set up as a queue to be thread/process safe. If any error is unhandled during run, it is fed into this queue so that calling thread can know the full details about the problem in this process.
    """

    def __init__(
        self, fatal_error_reporter: queue.Queue, lock: Optional[threading.Lock] = None
    ):
        super().__init__()
        self._lock = lock
        self._stop_event = threading.Event()
        self._fatal_error_reporter = fatal_error_reporter

        self._process_can_be_soft_stopped: bool
        self._soft_stop_event = threading.Event()

    def get_fatal_error_reporter(self) -> queue.Queue:
        return self._fatal_error_reporter

    def run(self, num_iterations: Optional[int] = None):
        # For some reason pylint freaks out if this method is only defined in the MixIn https://github.com/PyCQA/pylint/issues/1233
        super().run(num_iterations=num_iterations)
