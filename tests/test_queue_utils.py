# -*- coding: utf-8 -*-
import logging
import multiprocessing
import queue
from queue import Queue
import time

import pytest
from stdlib_utils import find_log_message_in_queue
from stdlib_utils import is_queue_eventually_empty
from stdlib_utils import is_queue_eventually_not_empty
from stdlib_utils import LogMessageNotFoundError
from stdlib_utils import put_log_message_into_queue
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


@pytest.mark.parametrize(
    "expected_item_number,expected_item,test_decsription",
    [
        (1, "message_1", "returns first log message"),
        (2, {"message": 2}, "returns second log message"),
    ],
)
def test_find_log_message_in_queue__returns_expected_item_from_queue_and_leaves_remaining_items(
    expected_item_number, expected_item, test_decsription, mocker
):
    test_items = ["message_1_string", {"message": 2, "other_key": True}, 3]

    spied_not_empty = mocker.spy(queue_utils, "is_queue_eventually_not_empty")

    q = multiprocessing.Queue()
    for item in test_items:
        put_log_message_into_queue(logging.INFO, item, q, logging.INFO)
    assert is_queue_eventually_not_empty(q) is True

    actual = find_log_message_in_queue(q, expected_item)
    if isinstance(expected_item, str):
        assert expected_item in actual
    if isinstance(expected_item, dict):
        assert actual["message"] == expected_item["message"]

    assert spied_not_empty.call_count == expected_item_number


def test_find_log_message_in_queue__raises_error_if_message_not_found():
    q = multiprocessing.Queue()
    for i in range(3):
        put_log_message_into_queue(logging.INFO, i, q, logging.INFO)

    test_item = "fake_item"
    with pytest.raises(
        LogMessageNotFoundError, match=f"Log Message: '{test_item}' not found in queue"
    ):
        find_log_message_in_queue(q, test_item)
