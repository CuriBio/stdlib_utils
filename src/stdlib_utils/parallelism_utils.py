# -*- coding: utf-8 -*-
"""Functionality to enhance parallelism.

This module can import things from both threading_utils and
multiprocessing_utils.
"""
from __future__ import annotations

import multiprocessing
import multiprocessing.queues
from queue import Queue
import time
from typing import Any
from typing import Dict
from typing import Union

from .multiprocessing_utils import InfiniteProcess
from .multiprocessing_utils import SimpleMultiprocessingQueue
from .parallelism_framework import InfiniteLoopingParallelismMixIn
from .threading_utils import InfiniteThread


def put_log_message_into_queue(
    log_level_of_this_message: int,
    the_message: Any,
    the_queue: Union[
        Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Dict[str, Any]
        ],
        SimpleMultiprocessingQueue,
        multiprocessing.queues.Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Dict[str, Any]
        ],
    ],
    log_level_threshold: int,
    pause_after_put: bool = False,
) -> None:
    """Put a log message into a queue.

    The message is only put in if the log level of the message meets the
    threshold of the queue.
    """
    if log_level_of_this_message >= log_level_threshold:
        comm_dict = {
            "communication_type": "log",
            "log_level": log_level_of_this_message,
            "message": the_message,
        }
        the_queue.put_nowait(comm_dict)
    if not isinstance(the_queue, SimpleMultiprocessingQueue) and pause_after_put:
        is_queue_eventually_not_empty(the_queue)


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

    error_queue = the_process.get_fatal_error_reporter()
    is_item_in_queue = not error_queue.empty()
    if not isinstance(error_queue, SimpleMultiprocessingQueue):
        is_item_in_queue = is_queue_eventually_not_empty(error_queue)
    if is_item_in_queue:
        err_info = the_process.get_fatal_error_reporter().get_nowait()
        if isinstance(the_process, InfiniteProcess):
            if not isinstance(err_info, tuple):
                raise NotImplementedError(
                    "Errors from InfiniteProcess must be Tuple[Exception,str]"
                )
            excp, trace = err_info
            if not isinstance(excp, Exception):
                raise NotImplementedError(
                    "Errors from InfiniteProcess must be Tuple[Exception,str]"
                )
            if not isinstance(trace, str):
                raise NotImplementedError(
                    "Errors from InfiniteProcess must be Tuple[Exception,str]"
                )
            InfiniteProcess.log_and_raise_error_from_reporter((excp, trace))
        if not isinstance(err_info, Exception):

            raise NotImplementedError("Errors from InfiniteThread must be Exceptions")

        InfiniteThread.log_and_raise_error_from_reporter(err_info)


def _eventually_empty(
    should_be_empty: bool,
    the_queue: Union[
        Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
        multiprocessing.queues.Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
    ],
) -> bool:
    """Help to determine if queue is eventually empty or not."""
    start_time = time.perf_counter()
    while time.perf_counter() - start_time < 0.05:
        is_empty = the_queue.empty()
        value_to_check = is_empty
        if not should_be_empty:
            value_to_check = not value_to_check
        if value_to_check:
            return True
    return False


def is_queue_eventually_empty(
    the_queue: Union[
        Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
        multiprocessing.queues.Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
    ]
) -> bool:
    """Check if queue is empty prior to timeout occurring."""
    return _eventually_empty(True, the_queue)


def is_queue_eventually_not_empty(
    the_queue: Union[
        Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
        multiprocessing.queues.Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
    ]
) -> bool:
    """Check if queue is not empty prior to timeout occurring."""
    return _eventually_empty(False, the_queue)
