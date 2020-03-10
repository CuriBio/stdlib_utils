# -*- coding: utf-8 -*-
"""Functionality to enhance parallelism.

This module can import things from both threading_utils and
multiprocessing_utils.
"""
import queue

from .multiprocessing_utils import InfiniteLoopingParallelismMixIn


def invoke_process_run_and_check_errors(
    the_process: InfiniteLoopingParallelismMixIn,
    num_iterations: int = 1,
    perform_setup_before_loop: bool = False,
) -> None:
    """Call the run method of a process and raise any errors.

    This is often useful in unit testing. This should only be used on
    processes that have not been started.
    """
    the_process.run(
        num_iterations=num_iterations,
        perform_setup_before_loop=perform_setup_before_loop,
        perform_teardown_after_loop=False,
    )
    try:
        err_info = the_process.get_fatal_error_reporter().get_nowait()  # type: ignore # the subclasses all have an instance of fatal error reporter. there may be a more elegant way to handle this to make mypy happy though... (Eli 2/12/20)
        the_process.__class__.log_and_raise_error_from_reporter(err_info)
    except queue.Empty:
        pass
