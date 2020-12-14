# -*- coding: utf-8 -*-
"""Controlling communication with the OpalKelly FPGA Boards."""
from __future__ import annotations

import logging
import queue
import threading
from typing import Optional
from typing import Union

from .parallelism_framework import InfiniteLoopingParallelismMixIn


class InfiniteThread(InfiniteLoopingParallelismMixIn, threading.Thread):
    """Thread for running infinitely in the background.

    Contains some enhanced functionality for stopping.

    Args:
        fatal_error_reporter: set up as a queue to be thread/process safe. If any error is unhandled during run, it is fed into this queue so that calling thread can know the full details about the problem in this process.
    """

    def __init__(
        self,
        fatal_error_reporter: queue.Queue,  # type: ignore[type-arg] # noqa: F821 # Eli (3/10/20) can't figure out why queue.Queue doesn't have type arguments defined in the stdlib(?)
        lock: Optional[threading.Lock] = None,
        logging_level: int = logging.INFO,
        minimum_iteration_duration_seconds: Union[float, int] = 0.01,
    ) -> None:
        threading.Thread.__init__(self)
        InfiniteLoopingParallelismMixIn.__init__(
            self,
            fatal_error_reporter,
            logging_level,
            threading.Event(),
            threading.Event(),
            threading.Event(),
            threading.Event(),
            threading.Event(),
            minimum_iteration_duration_seconds=minimum_iteration_duration_seconds,
        )
        self._lock = lock

    # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
    def run(  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
        self,
        num_iterations: Optional[int] = None,
        perform_setup_before_loop: bool = True,  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
        perform_teardown_after_loop: bool = True,
    ) -> None:  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
        # For some reason pylint freaks out if this method is only defined in the MixIn https://github.com/PyCQA/pylint/issues/1233
        # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
        super().run(
            num_iterations=num_iterations,
            perform_setup_before_loop=perform_setup_before_loop,
            perform_teardown_after_loop=perform_teardown_after_loop,
        )
