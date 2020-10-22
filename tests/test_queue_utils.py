# -*- coding: utf-8 -*-
import multiprocessing
import queue
from queue import Queue
import time

import pytest
from stdlib_utils import drain_queue
from stdlib_utils import is_queue_eventually_empty
from stdlib_utils import is_queue_eventually_not_empty
from stdlib_utils import queue_utils
from stdlib_utils import safe_get
from stdlib_utils import SimpleMultiprocessingQueue


def test_SimpleMultiprocessingQueue__get_nowait__returns_value_if_present():
    test_queue = SimpleMultiprocessingQueue()
    expected = "blah"
    test_queue.put(expected)
    actual = test_queue.get_nowait()
    assert actual == expected


def test_SimpleMultiprocessingQueue__put_nowait__adds_value_to_queue():
    test_queue = SimpleMultiprocessingQueue()
    expected = "blah7"
    test_queue.put_nowait(expected)
    actual = test_queue.get_nowait()
    assert actual == expected


@pytest.mark.timeout(0.1)  # set a timeout because the test can hang as a failure mode
def test_SimpleMultiprocessingQueue__get_nowait__raises_error_if_empty():
    test_queue = SimpleMultiprocessingQueue()
    with pytest.raises(queue.Empty):
        test_queue.get_nowait()


def test_is_queue_eventually_empty__returns_true_with_empty_threading_queue():
    q = queue.Queue()
    assert is_queue_eventually_empty(q) is True


def test_is_queue_eventually_empty__returns_true_with_empty_multiprocessing_queue__after_just_one_call(
    mocker,
):
    q = multiprocessing.Queue()
    spied_empty = mocker.spy(q, "empty")
    assert is_queue_eventually_empty(q) is True
    assert spied_empty.call_count == 1


def test_is_queue_eventually_empty__returns_false_with_not_empty_threading_queue(
    mocker,
):
    q = queue.Queue()
    mocked_empty = mocker.patch.object(q, "empty", autospec=True, return_value=False)
    assert is_queue_eventually_empty(q) is False
    assert mocked_empty.call_count > 10


def test_is_queue_eventually_empty__returns_false_with_not_empty_threading_queue__after_kwarg_timeout_is_met(
    mocker,
):
    q = queue.Queue()
    mocked_empty = mocker.patch.object(q, "empty", autospec=True, return_value=False)
    mocker.patch.object(
        queue_utils,
        "process_time",
        autospec=True,
        side_effect=[0, 0.1, 0.15, 0.2, 0.3, 0.35, 0.4],
    )
    assert is_queue_eventually_empty(q, timeout_seconds=0.36) is False
    assert mocked_empty.call_count == 5


def test_is_queue_eventually_empty__returns_true_after_multiple_attempts_with_eventually_empty_threading_queue(
    mocker,
):
    q = queue.Queue()
    mocked_empty = mocker.patch.object(
        q, "empty", autospec=True, side_effect=[False, False, False, False, True]
    )
    assert is_queue_eventually_empty(q) is True
    assert mocked_empty.call_count == 5


def test_is_queue_eventually_not_empty__returns_true_with_not_empty_threading_queue__after_just_one_call(
    mocker,
):
    q = queue.Queue()
    q.put("bob")
    spied_empty = mocker.spy(q, "empty")
    time.sleep(0.1)  # just to be safe make sure thread is definitely populated
    assert is_queue_eventually_not_empty(q) is True
    assert spied_empty.call_count == 1


def test_is_queue_eventually_not_empty__returns_true_with_not_empty_multiprocessing_queue():
    q = multiprocessing.Queue()
    q.put("bill")
    time.sleep(0.1)  # just to be safe make sure thread is definitely populated
    assert is_queue_eventually_not_empty(q) is True


def test_is_queue_eventually_not_empty__returns_false_with_empty_threading_queue(
    mocker,
):
    q = queue.Queue()
    spied_empty = mocker.spy(q, "empty")
    assert is_queue_eventually_not_empty(q) is False
    assert spied_empty.call_count > 10


def test_is_queue_eventually_not_empty__returns_false_with_empty_threading_queue__after_kwarg_timeout_is_met(
    mocker,
):
    q = queue.Queue()
    spied_empty = mocker.spy(q, "empty")
    mocker.patch.object(
        queue_utils, "process_time", autospec=True, side_effect=[0, 0.1, 0.15, 0.2, 0.3]
    )
    assert is_queue_eventually_not_empty(q, timeout_seconds=0.25) is False
    assert spied_empty.call_count == 3


def test_is_queue_eventually_not_empty__returns_true_after_multiple_attempts_with_eventually_not_empty_threading_queue(
    mocker,
):
    q = queue.Queue()
    mocked_empty = mocker.patch.object(
        q, "empty", autospec=True, side_effect=[True, True, True, False]
    )
    assert is_queue_eventually_not_empty(q) is True
    assert mocked_empty.call_count == 4


def test_safe_get__returns_expected_items():
    expected_items = ["item1", "item2", "item3"]
    actual_items = []

    q = Queue()
    for item in expected_items:
        q.put(item)

    num_items = len(expected_items)
    for _ in range(num_items + 1):
        next_item = safe_get(q)
        actual_items.append(next_item)

    expected_items.append(None)
    assert actual_items == expected_items


def test_drain_queue__returns_list_of_expected_items__and_ignores_None_objects():
    expected_items = [100, 200, 300]

    q = Queue()
    for item in expected_items:
        q.put(None)
        q.put(item)

    actual = drain_queue(q)
    assert actual == expected_items
