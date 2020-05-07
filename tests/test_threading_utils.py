# -*- coding: utf-8 -*-
import logging
import queue
import threading

import pytest
from stdlib_utils import get_formatted_stack_trace
from stdlib_utils import InfiniteLoopingParallelismMixIn
from stdlib_utils import InfiniteThread

from .fixtures_parallelism import InfiniteThreadThatCannotBeSoftStopped
from .fixtures_parallelism import InfiniteThreadThatRasiesError
from .fixtures_parallelism import init_test_args_InfiniteLoopingParallelismMixIn


def test_InfiniteThread__init__calls_Thread_super(mocker):
    error_queue = queue.Queue()
    mocked_super_init = mocker.spy(threading.Thread, "__init__")
    t = InfiniteThread(error_queue)
    mocked_super_init.assert_called_once_with(t)


def test_InfiniteThread__init__calls_InfiniteLoopingParallelismMixIn_super(mocker):
    error_queue = queue.Queue()
    mocked_super_init = mocker.patch.object(InfiniteLoopingParallelismMixIn, "__init__")
    t = InfiniteThread(error_queue)
    mocked_super_init.assert_called_once_with(
        t,
        error_queue,
        *init_test_args_InfiniteLoopingParallelismMixIn,
        minimum_iteration_duration_seconds=0.01,
    )


def test_InfiniteThread_internal_logging_level_can_be_set():
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue, logging_level=logging.DEBUG)
    assert t.get_logging_level() == logging.DEBUG


@pytest.mark.timeout(5)
def test_InfiniteThread_can_be_run_and_stopped():
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)
    t.start()
    assert t.is_alive() is True
    t.stop()
    t.join()
    assert t.is_alive() is False


@pytest.mark.timeout(2)  # set a timeout because the test can hang as a failure mode
def test_InfiniteThread_can_be_run_and_soft_stopped():
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)
    t.start()
    assert t.is_alive() is True
    t.soft_stop()
    t.join()
    assert error_queue.empty() is True
    assert t.is_alive() is False


def test_InfiniteThread__will_not_soft_stop_when_told_not_to():
    error_queue = queue.Queue()
    t = InfiniteThreadThatCannotBeSoftStopped(error_queue)
    t.soft_stop()
    t.run(num_iterations=1)
    assert t.is_stopped() is False


@pytest.mark.timeout(2)  # set a timeout because the test can hang as a failure mode
def test_InfiniteThread__run_can_be_executed_just_once(mocker):
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)
    spied_is_stopped = mocker.spy(t, "is_stopped")
    t.run(num_iterations=1)
    spied_is_stopped.assert_called_once()


@pytest.mark.timeout(2)  # set a timeout because the test can hang as a failure mode
def test_InfiniteThread__run_can_be_executed_just_four_cycles(mocker):
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)
    spied_is_stopped = mocker.spy(t, "is_stopped")
    t.run(num_iterations=4)
    assert spied_is_stopped.call_count == 4


def test_InfiniteThread_run_calls___commands_for_each_run_iteration(mocker):
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)
    spied_commands_for_each_run_iteration = mocker.spy(
        t, "_commands_for_each_run_iteration"
    )
    mocker.patch.object(t, "is_stopped", autospec=True, return_value=True)
    t.run()
    assert spied_commands_for_each_run_iteration.call_count == 1


def test_InfiniteThread__queue_is_populated_with_error_occuring_during_run__and_stop_is_called(
    mocker,
):
    expected_error = ValueError("test message")
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)

    mocker.patch.object(
        t, "_commands_for_each_run_iteration", autospec=True, side_effect=expected_error
    )
    spied_stop = mocker.spy(t, "stop")
    t.run()
    assert error_queue.empty() is False
    assert spied_stop.call_count == 1
    actual_error = error_queue.get()
    assert isinstance(actual_error, type(expected_error))
    assert str(actual_error) == str(expected_error)
    # assert actual_error == expected_error # Eli (12/24/19): for some reason this asserting doesn't pass...not sure why....so testing class type and str instead


def test_InfiniteThread__queue_is_populated_with_error_occuring_during_live_spawned_run():
    expected_error = ValueError("test message")
    error_queue = queue.Queue()
    t = InfiniteThreadThatRasiesError(error_queue)
    t.start()
    t.join()
    assert error_queue.empty() is False
    actual_error = error_queue.get()
    assert isinstance(actual_error, type(expected_error))
    assert str(actual_error) == str(expected_error)
    actual_stack_trace = get_formatted_stack_trace(actual_error)
    # assert actual_error == expected_error # Eli (12/24/19): for some reason this asserting doesn't pass...not sure why....so testing class type and str instead
    assert 'raise ValueError("test message")' in actual_stack_trace


def test_InfiniteThread__calls_setup_before_loop(mocker):
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)
    spied_setup = mocker.spy(t, "_setup_before_loop")
    t.run(num_iterations=1)
    assert error_queue.empty() is True
    assert spied_setup.call_count == 1


def test_InfiniteThread__calls_teardown_after_loop(mocker):
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue)
    spied_teardown = mocker.spy(t, "_teardown_after_loop")
    t.run(num_iterations=1)
    assert error_queue.empty() is True
    assert spied_teardown.call_count == 1


def test_InfiniteThread_can_set_minimum_iteration_duration():
    error_queue = queue.Queue()
    t = InfiniteThread(error_queue, minimum_iteration_duration_seconds=0.23)

    assert t.get_minimum_iteration_duration_seconds() == 0.23
