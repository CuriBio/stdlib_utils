# -*- coding: utf-8 -*-
"""Functionality to enhance checking of queue mainly during unit testing.

This module should not need to import from any other modules in
stdlib_utils.
"""
from __future__ import annotations

import multiprocessing
import multiprocessing.queues
import queue
from queue import Empty
from queue import Queue
import time
from typing import Any
from typing import Dict
from typing import Union

from .exceptions import LogMessageNotFoundError


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
    start_time = time.process_time()
    while time.process_time() - start_time < 0.2:
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


def safe_get(the_queue: Queue[Any]) -> Any:  # pylint: disable=unsubscriptable-object
    try:
        return the_queue.get(block=True, timeout=0.02)
    except Empty:
        return None


def find_log_message_in_queue(
    the_queue: multiprocessing.queues.Queue[
        Dict[str, Any]
    ],  # pylint: disable=unsubscriptable-object
    expected_message: Union[str, Dict[Any, Any]],
) -> Union[str, Dict[Any, Any]]:
    """Find a similar log message in the given queue and return it.

    This allows for flexibility in testing so that a similar but not exact match can be provided

    This should only be used to find items put into queues using put_log_message_into_queue.
    """
    log_message: Union[str, Dict[Any, Any], None] = None
    while is_queue_eventually_not_empty(the_queue):
        item = the_queue.get_nowait()
        item_message = item["message"]
        if isinstance(expected_message, str):
            if isinstance(item_message, str):
                log_message = item_message if expected_message in item_message else None
        elif isinstance(item_message, dict):
            log_message = (
                item_message
                if all(key in item_message.keys() for key in expected_message.keys())
                else None
            )
        if log_message is not None:
            return log_message
    raise LogMessageNotFoundError(
        f"Log Message: '{expected_message}' not found in queue"
    )


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

    def put_nowait(self, obj: Any) -> None:
        """Put without waiting/blocking.

        This is the only option with a SimpleQueue, but this is aliased
        to put to make the interface compatible with the regular
        multiprocessing.Queue interface.
        """
        self.put(obj)
