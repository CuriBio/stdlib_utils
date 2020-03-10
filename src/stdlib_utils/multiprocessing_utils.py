# -*- coding: utf-8 -*-
"""Utilities for multiprocessing."""
import logging
import multiprocessing
from multiprocessing import Event
from multiprocessing import Process
import multiprocessing.queues
import queue
from typing import Any
from typing import Optional
from typing import Tuple

from .misc import get_formatted_stack_trace
from .parallelism_framework import InfiniteLoopingParallelismMixIn


class SimpleMultiprocessingQueue(multiprocessing.queues.SimpleQueue):  # type: ignore[type-arg] # noqa: F821 # Eli (3/10/20) can't figure out why SimpleQueue doesn't have type arguments defined in the stdlib(?)
    """Some additional basic functionality.

    Since SimpleQueue is not technically a class, there are some tricks to subclassing it: https://stackoverflow.com/questions/39496554/cannot-subclass-multiprocessing-queue-in-python-3-5
    """

    def __init__(self) -> None:
        ctx = multiprocessing.get_context()
        super().__init__(ctx=ctx)

    def get_nowait(self) -> Any:
        """Get value or raise error if empty."""
        if self.empty():
            raise queue.Empty()
        return self.get()


# pylint: disable=duplicate-code
class InfiniteProcess(InfiniteLoopingParallelismMixIn, Process):
    """Process with some enhanced functionality.

    Because of the more explict error reporting/handling during the run method, the Process.exitcode value will still be 0 when the process exits after handling an error.

    Args:
        fatal_error_reporter: set up as a queue to be thread/process safe. If any error is unhandled during run, it is fed into this queue so that calling thread can know the full details about the problem in this process.
    """

    # pylint: disable=duplicate-code

    def __init__(self, fatal_error_reporter: SimpleMultiprocessingQueue) -> None:
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

    # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
    def run(  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
        self,  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
        num_iterations: Optional[  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
            int  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
        ] = None,  # pylint: disable=duplicate-code # pylint is freaking out and requiring the method to be redefined
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

    @staticmethod
    def log_and_raise_error_from_reporter(error_info: Tuple[Exception, str]) -> None:
        err, formatted_traceback = error_info
        logging.exception(formatted_traceback)
        raise err
