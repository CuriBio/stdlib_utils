# -*- coding: utf-8 -*-
import logging
import queue
import threading
import time

import pytest
from stdlib_utils import InfiniteLoopingParallelismMixIn
from stdlib_utils import is_queue_eventually_empty
from stdlib_utils import is_queue_eventually_not_empty
from stdlib_utils import SimpleMultiprocessingQueue


@pytest.fixture(scope="function", name="patch_init_performance_metrics")
def fixture_patch_init_performance_metrics(mocker):
    mocker.patch.object(
        InfiniteLoopingParallelismMixIn, "_init_performance_measurements", autospec=True
    )


def generic_infinte_looper():
    p = InfiniteLoopingParallelismMixIn(
        queue.Queue(),
        logging.INFO,
        threading.Event(),
        threading.Event(),
        threading.Event(),
        threading.Event(),
        minimum_iteration_duration_seconds=0.01,
    )
    return p


def test_InfiniteLoopingParallelismMixIn__sleeps_during_loop_for_time_remaining_if_minimum_iteration_duration_not_met(
    mocker, patch_init_performance_metrics
):
    mocked_length_of_time_to_execute_ns = 10 ** 6
    mocker.patch.object(
        time,
        "perf_counter_ns",
        autospec=True,
        side_effect=[0, mocked_length_of_time_to_execute_ns, 0],
    )
    mocked_sleep = mocker.patch.object(time, "sleep", autospec=True)
    generic_infinte_looper().run(num_iterations=2, perform_setup_before_loop=False)
    expected_time_to_sleep_seconds = round(
        0.01 - mocked_length_of_time_to_execute_ns / 10 ** 9, 10
    )
    mocked_sleep.assert_called_once_with(expected_time_to_sleep_seconds)


def test_InfiniteLoopingParallelismMixIn__does_not_sleep_during_loop_if_minimum_iteration_duration_already_met(
    mocker, patch_init_performance_metrics
):

    mocker.patch.object(
        time, "perf_counter_ns", autospec=True, side_effect=[0, 0.1 * 10 ** 9, 0],
    )
    mocked_sleep = mocker.patch.object(time, "sleep", autospec=True)
    generic_infinte_looper().run(num_iterations=2, perform_setup_before_loop=False)
    assert mocked_sleep.call_count == 0


def test_InfiniteLoopingParallelismMixIn__reset_performance_tracker__initially_returns_value_from_init__then_last_reset_value(
    mocker,
):
    expected_first_return = 12345
    expected_second_return = 54321
    mocker.patch.object(
        time,
        "perf_counter_ns",
        autospec=True,
        side_effect=[expected_first_return, 0, expected_second_return, 0, 0],
    )

    p = generic_infinte_looper()

    actual_first_return = p.reset_performance_tracker()
    assert "start_timepoint_of_measurements" in actual_first_return
    assert (
        actual_first_return["start_timepoint_of_measurements"] == expected_first_return
    )
    assert "idle_iteration_time_ns" in actual_first_return
    assert actual_first_return["idle_iteration_time_ns"] == 0

    actual_second_return = p.reset_performance_tracker()
    assert "start_timepoint_of_measurements" in actual_second_return
    assert (
        actual_second_return["start_timepoint_of_measurements"]
        == expected_second_return
    )


def test_InfiniteLoopingParallelismMixIn__reset_performance_tracker__counts_idle_time(
    mocker,
):
    p = generic_infinte_looper()
    time_of_first_iter_ns = 2 * 10 ** 6
    time_of_second_iter_ns = 1 * 10 ** 6
    mocker.patch.object(
        time,
        "perf_counter_ns",
        autospec=True,
        side_effect=[0, time_of_first_iter_ns, 0, time_of_second_iter_ns, 0, 0, 0],
    )
    mocker.patch.object(time, "sleep", autospec=True)

    p.run(num_iterations=3, perform_setup_before_loop=False)

    performance_metrics = p.reset_performance_tracker()
    total_idle_time = performance_metrics["idle_iteration_time_ns"]
    allowed_time_per_iter_ns = 10 * 10 ** 6
    expected_idle_time = (
        allowed_time_per_iter_ns * 2 - time_of_first_iter_ns - time_of_second_iter_ns
    )
    assert total_idle_time == expected_idle_time


def test_InfiniteLoopingParallelismMixIn__reset_performance_tracker__returns_and_stores_percent_use(
    mocker,
):
    expected_first_return = 11000
    expected_second_return = 12000
    idle_time = 10000
    expected_percent_use_1 = 100 * (1 - idle_time / expected_first_return)
    expected_percent_use_2 = 100 * (1 - idle_time / expected_second_return)
    mocker.patch.object(
        time,
        "perf_counter_ns",
        autospec=True,
        side_effect=[0, expected_first_return, 0, expected_second_return, 0],
    )

    p = generic_infinte_looper()

    p._idle_iteration_time_ns = idle_time  # pylint:disable=protected-access
    actual_first_return = p.reset_performance_tracker()
    assert actual_first_return["percent_use"] == expected_percent_use_1

    p._idle_iteration_time_ns = idle_time  # pylint:disable=protected-access
    actual_second_return = p.reset_performance_tracker()
    assert actual_second_return["percent_use"] == expected_percent_use_2


def test_InfiniteLoopingParallelismMixIn__get_start_timepoint_of_performance_measurement(
    mocker,
):
    expected_timepoint = 123554
    mocker.patch.object(
        time, "perf_counter_ns", autospec=True, side_effect=[expected_timepoint],
    )

    p = generic_infinte_looper()

    actual_timepoint = p.get_start_timepoint_of_performance_measurement()
    assert actual_timepoint == expected_timepoint


def test_InfiniteLoopingParallelismMixIn__hard_stop__calls_stop():
    p = generic_infinte_looper()
    p.hard_stop()

    stop_event = p._stop_event  # pylint:disable=protected-access
    assert stop_event.is_set() is True


def test_InfiniteLoopingParallelismMixIn__hard_stop__waits_for_teardown_complete_event_to_drain_error_queue(
    mocker,
):
    expected_error = "dummy_error"

    p = generic_infinte_looper()
    error_queue = p._fatal_error_reporter  # pylint:disable=protected-access
    teardown_event = p._teardown_complete_event  # pylint:disable=protected-access

    def side_effect(*args, **kwargs):
        assert is_queue_eventually_not_empty(error_queue) is True
        teardown_event.set()

    mocker.patch.object(
        p, "_teardown_after_loop", autospec=True, side_effect=side_effect
    )
    error_queue.put(expected_error)

    actual = p.hard_stop()
    assert actual["fatal_error_reporter"] == [expected_error]

    assert is_queue_eventually_empty(error_queue) is True


def test_InfiniteLoopingParallelismMixIn__hard_stop__waits_for_teardown_complete_event_to_drain_error_queue_with_SimpleMultiprocessingQueue(
    mocker,
):
    expected_error = "dummy_error"

    p = generic_infinte_looper()
    error_queue = SimpleMultiprocessingQueue()
    p._fatal_error_reporter = error_queue  # pylint:disable=protected-access
    teardown_event = p._teardown_complete_event  # pylint:disable=protected-access

    def side_effect(*args, **kwargs):
        assert is_queue_eventually_not_empty(error_queue) is True
        teardown_event.set()

    mocker.patch.object(
        p, "_teardown_after_loop", autospec=True, side_effect=side_effect
    )
    error_queue.put(expected_error)

    actual = p.hard_stop()
    assert teardown_event.is_set() is True

    assert actual["fatal_error_reporter"] == [expected_error]
    assert error_queue.empty() is True


@pytest.mark.timeout(1)
def test_InfiniteLoopingParallelismMixIn__hard_stop__timeout_overrides_waiting_for_teardown_complete_event_to_drain_error_queue(
    mocker,
):
    expected_error = "dummy_error"

    p = generic_infinte_looper()
    error_queue = p._fatal_error_reporter  # pylint:disable=protected-access
    teardown_event = p._teardown_complete_event  # pylint:disable=protected-access

    def side_effect(*args, **kwargs):
        assert is_queue_eventually_not_empty(error_queue) is True

    mocker.patch.object(
        p, "_teardown_after_loop", autospec=True, side_effect=side_effect
    )
    error_queue.put(expected_error)

    actual = p.hard_stop(timeout=0.2)
    assert teardown_event.is_set() is False

    assert actual["fatal_error_reporter"] == [expected_error]
    assert error_queue.empty() is True


@pytest.mark.parametrize(
    "perform_setup_before_loop,test_description",
    [
        (False, "sets start_up_complete_event with no setup before loop"),
        (True, "sets start_up_complete_event with setup before loop"),
    ],
)
def test_InfiniteLoopingParallelismMixIn__always_sets_start_up_complete_event_before_entering_loop(
    perform_setup_before_loop, test_description, mocker
):
    p = generic_infinte_looper()
    start_up_complete_event = (
        p._start_up_complete_event  # pylint:disable=protected-access
    )
    spied_set = mocker.spy(start_up_complete_event, "set")

    assert start_up_complete_event.is_set() is False
    assert p.is_start_up_complete() is False

    p.run(num_iterations=2, perform_setup_before_loop=perform_setup_before_loop)
    assert start_up_complete_event.is_set() is True
    assert p.is_start_up_complete() is True
    assert spied_set.call_count == 1
