# -*- coding: utf-8 -*-
"""Controlling communication with the OpalKelly FPGA Boards."""
import logging
import multiprocessing
from multiprocessing import Event
from multiprocessing import Process
import multiprocessing.queues
import queue
from typing import Optional
from typing import Tuple

from .misc import get_formatted_stack_trace
from .parallelism_framework import InfiniteLoopingParallelismMixIn


class SimpleMultiprocessingQueue(multiprocessing.queues.SimpleQueue):
    """Some additional basic functionality.

    Since SimpleQueue is not technically a class, there are some tricks to subclassing it: https://stackoverflow.com/questions/39496554/cannot-subclass-multiprocessing-queue-in-python-3-5
    """

    def __init__(self):
        ctx = multiprocessing.get_context()
        super().__init__(ctx=ctx)

    def get_nowait(self):
        """Get value or raise error if empty."""
        if self.empty():
            raise queue.Empty()
        return self.get()


class InfiniteProcess(InfiniteLoopingParallelismMixIn, Process):
    """Process with some enhanced functionality.

    Because of the more explict error reporting/handling during the run method, the Process.exitcode value will still be 0 when the process exits after handling an error.

    Args:
        fatal_error_reporter: set up as a queue to be thread/process safe. If any error is unhandled during run, it is fed into this queue so that calling thread can know the full details about the problem in this process.
    """

    def __init__(self, fatal_error_reporter: SimpleMultiprocessingQueue):
        super().__init__()
        self._stop_event = Event()
        self._fatal_error_reporter = fatal_error_reporter
        self._process_can_be_soft_stopped = True
        self._soft_stop_event = Event()

    def get_fatal_error_reporter(self) -> SimpleMultiprocessingQueue:
        return self._fatal_error_reporter

    def _report_fatal_error(self, the_err: Exception) -> None:
        formatted_stack_trace = get_formatted_stack_trace(the_err)
        self._fatal_error_reporter.put((the_err, formatted_stack_trace))

    def run(self, num_iterations: Optional[int] = None):
        # For some reason pylint freaks out if this method is only defined in the MixIn https://github.com/PyCQA/pylint/issues/1233
        super().run(num_iterations=num_iterations)

    @staticmethod
    def log_and_raise_error_from_reporter(error_info: Tuple[Exception, str]) -> None:
        err, formatted_traceback = error_info
        logging.exception(formatted_traceback)
        raise err
