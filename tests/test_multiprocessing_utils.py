# -*- coding: utf-8 -*-
import logging
from multiprocessing import Process
import queue

import pytest
from stdlib_utils import InfiniteLoopingParallelismMixIn
from stdlib_utils import InfiniteProcess
from stdlib_utils import SimpleMultiprocessingQueue

from .fixtures_parallelism import InfiniteProcessThatCannotBeSoftStopped
from .fixtures_parallelism import InfiniteProcessThatRasiesError


def test_SimpleMultiprocessingQueue__get_nowait__returns_value_if_present():
    test_queue = SimpleMultiprocessingQueue()
    expected = "blah"
    test_queue.put(expected)
    actual = test_queue.get_nowait()
    assert actual == expected


@pytest.mark.timeout(0.1)  # set a timeout because the test can hang as a failure mode
def test_SimpleMultiprocessingQueue__get_nowait__raises_error_if_empty():
    test_queue = SimpleMultiprocessingQueue()
    with pytest.raises(queue.Empty):
        test_queue.get_nowait()


def test_InfiniteProcess_super_Process_is_called_during_init(mocker):
    mocked_init = mocker.patch.object(Process, "__init__")
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    mocked_init.assert_called_once_with(p)


def test_InfiniteProcess_super_InfiniteLoopingParallelismMixIn_is_called_during_init(
    mocker,
):
    mocked_init = mocker.patch.object(InfiniteLoopingParallelismMixIn, "__init__")
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    mocked_init.assert_called_once_with(p, error_queue, logging.INFO)


def test_InfiniteProcess_internal_logging_level_can_be_set():

    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue, logging_level=logging.DEBUG)
    assert p.get_logging_level() == logging.DEBUG


def test_InfiniteProcess_can_be_run_and_stopped():
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    p.start()
    assert p.is_alive() is True
    p.stop()
    p.join()
    assert p.is_alive() is False
    assert p.exitcode == 0


@pytest.mark.timeout(2)  # set a timeout because the test can hang as a failure mode
def test_InfiniteProcess_can_be_run_and_soft_stopped():
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    p.start()
    assert p.is_alive() is True
    p.soft_stop()
    p.join()
    assert p.is_alive() is False
    assert p.exitcode == 0


def test_InfiniteProcess__will_not_soft_stop_when_told_not_to():
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcessThatCannotBeSoftStopped(error_queue)
    p.soft_stop()
    p.run(num_iterations=1)
    assert p.is_stopped() is False


@pytest.mark.timeout(2)  # set a timeout because the test can hang as a failure mode
def test_InfiniteProcess__run_can_be_executed_just_once(mocker):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_is_stopped = mocker.spy(p, "is_stopped")
    p.run(num_iterations=1)
    spied_is_stopped.assert_called_once()


@pytest.mark.timeout(2)  # set a timeout because the test can hang as a failure mode
def test_InfiniteProcess__run_can_be_executed_just_four_cycles(mocker):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_is_stopped = mocker.spy(p, "is_stopped")
    p.run(num_iterations=4)
    assert spied_is_stopped.call_count == 4


def test_InfiniteProcess_run_calls___commands_for_each_run_iteration(mocker):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_commands_for_each_run_iteration = mocker.spy(
        p, "_commands_for_each_run_iteration"
    )
    mocker.patch.object(p, "is_stopped", autospec=True, return_value=True)
    p.run()
    assert spied_commands_for_each_run_iteration.call_count == 1


def test_InfiniteProcess__queue_is_populated_with_error_occuring_during_run__and_stop_is_called(
    mocker,
):
    expected_error = ValueError("test message")
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)

    mocker.patch.object(
        p, "_commands_for_each_run_iteration", autospec=True, side_effect=expected_error
    )
    spied_stop = mocker.spy(p, "stop")

    p.run()
    assert error_queue.empty() is False
    assert spied_stop.call_count == 1
    actual_error, _ = error_queue.get()
    assert isinstance(actual_error, type(expected_error))
    assert str(actual_error) == str(expected_error)
    # assert actual_error == expected_error # Eli (12/24/19): for some reason this asserting doesn't pass...not sure why....so testing class type and str instead


def test_InfiniteProcess__queue_is_populated_with_error_occuring_during_live_spawned_run():
    expected_error = ValueError("test message")
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcessThatRasiesError(error_queue)
    p.start()
    p.join()
    assert error_queue.empty() is False
    actual_error, actual_stack_trace = error_queue.get()

    assert isinstance(actual_error, type(expected_error))
    assert str(actual_error) == str(expected_error)
    assert p.exitcode == 0  # When errors are handled, the error code is 0
    # assert actual_error == expected_error # Eli (12/24/19): for some reason this asserting doesn't pass...not sure why....so testing class type and str instead
    assert 'raise ValueError("test message")' in actual_stack_trace


def test_InfiniteProcess__calls_setup_before_loop(mocker):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_setup = mocker.spy(p, "_setup_before_loop")
    p.run(num_iterations=1)
    assert error_queue.empty() is True
    assert spied_setup.call_count == 1


def test_InfiniteProcess__catches_error_in_setup_before_loop_and_does_not_run_iteration_or_teardown(
    mocker,
):
    expected_error = ValueError("error during setup")
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_run = mocker.spy(p, "_commands_for_each_run_iteration")
    spied_teardown = mocker.spy(p, "_teardown_after_loop")
    mocked_setup = mocker.patch.object(
        p, "_setup_before_loop", autospec=True, side_effect=expected_error
    )
    p.run(num_iterations=1)
    assert error_queue.empty() is False
    actual_error, _ = error_queue.get_nowait()
    assert mocked_setup.call_count == 1
    assert spied_run.call_count == 0
    assert spied_teardown.call_count == 0
    assert isinstance(actual_error, type(expected_error))
    assert str(actual_error) == str(expected_error)


def test_InfiniteProcess__calls_teardown_after_loop(mocker):
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)
    spied_teardown = mocker.spy(p, "_teardown_after_loop")
    p.run(num_iterations=1)
    assert error_queue.empty() is True
    assert spied_teardown.call_count == 1


def test_InfiniteProcess__catches_error_in_teardown_after(mocker):
    expected_error = ValueError("error during teardown")
    error_queue = SimpleMultiprocessingQueue()
    p = InfiniteProcess(error_queue)

    mocked_teardown = mocker.patch.object(
        p, "_teardown_after_loop", autospec=True, side_effect=expected_error
    )
    p.run(num_iterations=1)
    assert mocked_teardown.call_count == 1
    assert error_queue.empty() is False
    actual_error, _ = error_queue.get_nowait()
    assert isinstance(actual_error, type(expected_error))
    assert str(actual_error) == str(expected_error)
