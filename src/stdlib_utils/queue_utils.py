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
from time import process_time
from typing import Any
from typing import List
from typing import Union

from .exceptions import QueueStillEmptyError


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
    timeout_seconds: Union[float, int] = 0.2,
) -> bool:
    """Help to determine if queue is eventually empty or not."""
    start_time = process_time()
    while process_time() - start_time < timeout_seconds:
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
    ],
    timeout_seconds: Union[float, int] = 0.2,
) -> bool:
    """Check if queue is empty prior to timeout occurring."""
    return _eventually_empty(True, the_queue, timeout_seconds=timeout_seconds)


def is_queue_eventually_not_empty(
    the_queue: Union[
        Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
        multiprocessing.queues.Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
    ],
    timeout_seconds: Union[float, int] = 0.2,
) -> bool:
    """Check if queue is not empty prior to timeout occurring."""
    return _eventually_empty(False, the_queue, timeout_seconds=timeout_seconds)


def put_object_into_queue_and_raise_error_if_eventually_still_empty(  # pylint: disable=invalid-name # Eli (10/22/20): I know this is long, but it's a combined helper function for unit testing
    obj: object,
    the_queue: Union[
        Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
        multiprocessing.queues.Queue[  # pylint: disable=unsubscriptable-object # Eli (3/12/20) not sure why pylint doesn't recognize this type annotation
            Any
        ],
    ],
    timeout_seconds: Union[float, int] = 0.2,
) -> None:
    """Put an object into a queue and wait until queue is populated.

    Raises an error if queue is still empty and the end of
    timeout_seconds. This is primarily/exclusively used in unit testing.
    """
    the_queue.put(obj)
    if not is_queue_eventually_not_empty(the_queue, timeout_seconds=timeout_seconds):
        raise QueueStillEmptyError()


def safe_get(the_queue: Queue[Any]) -> Any:  # pylint: disable=unsubscriptable-object
    try:
        return the_queue.get(block=True, timeout=0.02)
    except Empty:
        return None


def drain_queue(
    the_queue: Queue[Any],  # pylint: disable=unsubscriptable-object
) -> List[Any]:
    items = list()
    while not the_queue.empty():
        item = safe_get(the_queue)
        if item is not None:
            items.append(item)
    return items


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
