# -*- coding: utf-8 -*-
import inspect
import logging
import multiprocessing
import queue
import time

import pytest
from stdlib_utils import InfiniteProcess
from stdlib_utils import invoke_process_run_and_check_errors
from stdlib_utils import is_queue_eventually_empty
from stdlib_utils import is_queue_eventually_not_empty
from stdlib_utils import put_log_message_into_queue
from stdlib_utils import SimpleMultiprocessingQueue
from stdlib_utils import sleep_so_queue_processes_change

from .fixtures_parallelism import InfiniteProcessThatRasiesError
from .fixtures_parallelism import InfiniteThreadThatRasiesError


def test_invoke_process_run_and_check_errors__passes_values_for_InfiniteProcess(mocker):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_run = mocker.spy(p, "_commands_for_each_run_iteration")
    invoke_process_run_and_check_errors(p)  # runs once by default
    assert spied_run.call_count == 1

    invoke_process_run_and_check_errors(p, num_iterations=2)
    assert spied_run.call_count == 3


def test_invoke_process_run_and_check_errors__pauses_long_enough_to_process_standard_multiprocessing_queue(
    mocker,
):
    error_queue = multiprocessing.Queue()
    p = InfiniteProcessThatRasiesError(error_queue)

    with pytest.raises(ValueError, match="test message"):
        invoke_process_run_and_check_errors(p)


def test_invoke_process_run_and_check_errors__raises_and_logs_error_for_InfiniteProcess(
    mocker,
):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcessThatRasiesError(error_queue)
    mocked_log = mocker.patch.object(logging, "exception", autospec=True)
    with pytest.raises(ValueError, match="test message"):
        invoke_process_run_and_check_errors(p)
    assert error_queue.empty() is True  # the error should have been popped off the queu
    assert mocked_log.call_count == 1


def test_invoke_process_run_and_check_errors__does_not_run_setup_or_teardown_by_default(
    mocker,
):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_run = mocker.spy(p, "_commands_for_each_run_iteration")
    spied_setup = mocker.spy(p, "_setup_before_loop")
    spied_teardown = mocker.spy(p, "_teardown_after_loop")
    invoke_process_run_and_check_errors(p)  # runs once by default
    assert spied_run.call_count == 1
    assert spied_setup.call_count == 0
    assert spied_teardown.call_count == 0

    invoke_process_run_and_check_errors(p, num_iterations=2)
    assert spied_run.call_count == 3


def test_invoke_process_run_and_check_errors__raises_and_logs_error_for_InfiniteThread(
    mocker,
):
    error_queue = queue.Queue()
    p = InfiniteThreadThatRasiesError(error_queue)
    mocked_log = mocker.patch.object(logging, "exception", autospec=True)
    with pytest.raises(ValueError, match="test message"):
        invoke_process_run_and_check_errors(p)
    assert (
        error_queue.empty() is True
    )  # the error should have been popped off the queue
    assert mocked_log.call_count == 1


def test_put_log_message_into_queue__puts_message_in_when_at_threshold():
    q = queue.Queue()
    msg = "hey"
    put_log_message_into_queue(logging.INFO, msg, q, logging.INFO)
    the_comm = q.get_nowait()
    assert isinstance(the_comm, dict)
    assert the_comm["communication_type"] == "log"
    assert the_comm["log_level"] == logging.INFO
    assert the_comm["message"] == msg


def test_put_log_message_into_queue__puts_message_in_when_above_threshold():
    q = queue.Queue()
    msg = "hey jude"
    put_log_message_into_queue(logging.ERROR, msg, q, logging.WARNING)
    the_comm = q.get_nowait()
    assert the_comm["message"] == msg
    assert the_comm["log_level"] == logging.ERROR


def test_put_log_message_into_queue__does_not_put_message_in_when_below_threshold():
    q = queue.Queue()
    msg = "hey there"
    put_log_message_into_queue(logging.DEBUG, msg, q, logging.INFO)
    assert q.empty() is True


def test_put_log_message_into_queue__sleeps_after_putting_message_into_regular_queue(
    mocker,
):
    spied_sleep = mocker.spy(time, "sleep")
    q = queue.Queue()
    msg = "hey there"
    put_log_message_into_queue(
        logging.ERROR, msg, q, logging.WARNING, pause_after_put=True,
    )
    spied_sleep.assert_called_once_with(0.001)


def test_put_log_message_into_queue__does_not_sleep_after_putting_message_into_simplequeue(
    mocker,
):
    spied_sleep = mocker.spy(time, "sleep")
    sq = SimpleMultiprocessingQueue()
    msg = "hey there"
    put_log_message_into_queue(
        logging.ERROR, msg, sq, logging.WARNING, pause_after_put=True,
    )
    spied_sleep.assert_not_called()


def test_put_log_message_into_queue__does_not_sleep_with_default_pause_value_and_regular_queue(
    mocker,
):
    spied_sleep = mocker.spy(time, "sleep")
    q = queue.Queue()
    msg = "hey there"
    put_log_message_into_queue(logging.ERROR, msg, q, logging.WARNING)
    spied_sleep.assert_not_called()


def test_sleep_so_queue_processes_change(mocker):
    spied_sleep = mocker.spy(time, "sleep")
    sleep_so_queue_processes_change()
    spied_sleep.assert_called_once_with(0.001)


def test_sleep_so_queue_processes_change__raises_deprecation_warning(mocker):
    # mock inpsect.stack so that it does not appear to be coming internally from inside stdlib_utils
    mocker.patch.object(
        inspect, "stack", autospec=True, return_value=[None, [None, "blah"]]
    )
    with pytest.warns(DeprecationWarning, match="is_queue_eventually_empty"):
        sleep_so_queue_processes_change()


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
