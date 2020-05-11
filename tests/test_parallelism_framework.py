# -*- coding: utf-8 -*-
import logging
import queue
import threading
import time

import pytest
from stdlib_utils import InfiniteLoopingParallelismMixIn


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
        side_effect=[expected_first_return, expected_second_return, 0],
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
        side_effect=[0, time_of_first_iter_ns, 0, time_of_second_iter_ns, 0, 0],
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
