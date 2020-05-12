# -*- coding: utf-8 -*-
"""Functionality to enhance parallelism."""
from __future__ import annotations

import logging
import multiprocessing
import multiprocessing.queues
import multiprocessing.synchronize
import queue
import threading
import time
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

from .misc import get_formatted_stack_trace
from .misc import print_exception


class InfiniteLoopingParallelismMixIn:
    """Mix-in for infinite looping."""

    def __init__(
        self,
        fatal_error_reporter: Union[
            queue.Queue[str],
            multiprocessing.queues.Queue[Tuple[Exception, str]],
            multiprocessing.queues.SimpleQueue[Tuple[Exception, str]],
        ],
        logging_level: int,
        stop_event: Union[threading.Event, multiprocessing.synchronize.Event],
        soft_stop_event: Union[threading.Event, multiprocessing.synchronize.Event],
        teardown_complete_event: Union[
            threading.Event, multiprocessing.synchronize.Event
        ],
        minimum_iteration_duration_seconds: Union[float, int] = 0.01,
    ) -> None:
        self._stop_event = stop_event
        self._soft_stop_event = soft_stop_event
        self._teardown_complete_event = teardown_complete_event
        self._fatal_error_reporter = fatal_error_reporter
        self._process_can_be_soft_stopped = True
        self._logging_level = logging_level
        self._minimum_iteration_duration_seconds = minimum_iteration_duration_seconds
        self._idle_iteration_time_ns = 0
        self._init_performance_measurements()

    def _init_performance_measurements(self) -> None:
        # separate to make mocking easier
        self._reset_performance_measurements()

    def _reset_performance_measurements(self) -> None:
        self._start_timepoint_of_last_performance_measurement = time.perf_counter_ns()
        self._idle_iteration_time_ns = 0

    def get_start_timepoint_of_performance_measurement(self) -> int:
        return self._start_timepoint_of_last_performance_measurement

    def reset_performance_tracker(self) -> Dict[str, int]:
        out_dict: Dict[str, int] = {}
        out_dict[
            "start_timepoint_of_measurements"
        ] = self._start_timepoint_of_last_performance_measurement
        out_dict["idle_iteration_time_ns"] = self._idle_iteration_time_ns
        self._reset_performance_measurements()
        return out_dict

    def get_minimum_iteration_duration_seconds(self) -> Union[float, int]:
        return self._minimum_iteration_duration_seconds

    def get_logging_level(self) -> int:
        return self._logging_level

    @staticmethod
    def log_and_raise_error_from_reporter(error_info: Exception) -> None:
        err = error_info
        if not isinstance(err, Exception):
            raise NotImplementedError(
                "Error in the code, this should always be an Exception."
            )
        formatted_traceback = get_formatted_stack_trace(err)
        logging.exception(formatted_traceback)
        raise err

    def get_fatal_error_reporter(
        self,
    ) -> Union[
        queue.Queue[str],
        multiprocessing.queues.Queue[Tuple[Exception, str]],
        multiprocessing.queues.SimpleQueue[Tuple[Exception, str]],
    ]:
        return self._fatal_error_reporter

    def _report_fatal_error(self, the_err: Exception) -> None:
        self._fatal_error_reporter.put_nowait(the_err)  # type: ignore # the subclasses all have an instance of fatal error reporter. there may be a more elegant way to handle this to make mypy happy though... (Eli 2/12/20)

    def _setup_before_loop(self) -> None:
        """Perform any necessary setup prior to initiating the infinite loop.

        This can be overridden by the subclass.
        """

    def _teardown_after_loop(self) -> None:
        """Perform any necessary teardown after the infinite loop has exited.

        It's the responsibility of this method and parent process to make sure all queues get emptied before join is called.

        This can be overridden by the subclass, but the super method should always be called at the end of the subclass's implementation.
        """
        if not hasattr(self, "_teardown_complete_event"):
            raise NotImplementedError(
                "Classes using this mixin must have a _stop_event attribute."
            )
        teardown_complete_event = getattr(self, "_teardown_complete_event")

        teardown_complete_event.set()

    def run(
        self,
        num_iterations: Optional[int] = None,
        perform_setup_before_loop: bool = True,
        perform_teardown_after_loop: bool = True,
    ) -> None:
        """Run the thread.

        Args:
            num_iterations: typically used for unit testing to just execute one or a few cycles. if left as None will loop infinitely
            perform_setup_before_loop: this can be disabled when needed during unit testing
            perform_teardown_after_loop: this can be disabled when needed during unit testing

        This sets up the basic flow control and error handling for the thread.
        Subclasses should implement functionality to be executed during each
        cycle in the _commands_for_each_run_iteration method.
        """
        if num_iterations is None:
            num_iterations = -1
        completed_iterations = 0
        if perform_setup_before_loop:
            try:
                self._setup_before_loop()
            except Exception as e:  # pylint: disable=broad-except # The deliberate goal of this is to catch everything and put it into the error queue
                print_exception(e, "cf477f32-9797-417e-a157-ea6e0c4f25d1")
                self._report_fatal_error(e)
                return
        while True:
            start_timepoint_of_iteration = time.perf_counter_ns()
            self._process_can_be_soft_stopped = True
            try:
                self._commands_for_each_run_iteration()
            except Exception as e:  # pylint: disable=broad-except # The deliberate goal of this is to catch everything and put it into the error queue
                print_exception(e, "88a25177-b2a1-4bbb-ba92-bf5810594a99")
                self._report_fatal_error(e)
                self.stop()
            if self.is_preparing_for_soft_stop() and self._process_can_be_soft_stopped:
                self.stop()

            if self.is_stopped():
                # Having the check for is_stopped after the first iteration of run allows easier unit testing.
                break
            completed_iterations += 1
            if completed_iterations == num_iterations:
                break
            # only decide to sleep if there are more iterations to do. this will keep unit tests executing more quickly
            self._sleep_for_idle_time_during_iteration(start_timepoint_of_iteration)
        if perform_teardown_after_loop:
            try:
                self._teardown_after_loop()
            except Exception as e:  # pylint: disable=broad-except # The deliberate goal of this is to catch everything and put it into the error queue
                print_exception(e, "bd9a8587-e79b-43cb-8ffe-0bf45740599d")
                self._report_fatal_error(e)

    def _sleep_for_idle_time_during_iteration(
        self, start_timepoint_of_iteration: int
    ) -> None:
        stop_timepoint_of_iteration = time.perf_counter_ns()
        iteration_time_ns = stop_timepoint_of_iteration - start_timepoint_of_iteration

        idle_time_ns = (
            int(self.get_minimum_iteration_duration_seconds() * 10 ** 9)
            - iteration_time_ns
        )
        if idle_time_ns > 0:
            self._idle_iteration_time_ns += idle_time_ns
            time.sleep(idle_time_ns / 10 ** 9)

    def _commands_for_each_run_iteration(self) -> None:
        """Execute additional commands inside the run loop."""

    def stop(self) -> None:
        """Safely stops the process."""
        if not hasattr(self, "_stop_event"):
            raise NotImplementedError(
                "Classes using this mixin must have a _stop_event attribute."
            )
        stop_event = getattr(self, "_stop_event")

        stop_event.set()

    def soft_stop(self) -> None:
        """Stop the process when the process indicates it is OK to do so.

        Typically useful for unit testing. For example waiting until all
        queued up items have been handled.
        """
        if not hasattr(self, "_soft_stop_event"):
            raise NotImplementedError(
                "Classes using this mixin must have a _soft_stop_event attribute."
            )
        soft_stop_event = getattr(self, "_soft_stop_event")

        soft_stop_event.set()

    def hard_stop(self) -> Dict[str, Any]:
        """Stop the process and drain all queues.

        Timeout can be specified which will override waiting for process to tear itself down.

        Items in queues will be returned in a dict
        """
        self.stop()
        item_dict = self._drain_all_queues()

        error_queue = self.get_fatal_error_reporter()
        error_items = list()
        while not error_queue.empty():
            # Tanner (4/12/20): cannot import is_queue_eventually_not_empty for some reason
            error_items.append(error_queue.get_nowait())  # type: ignore

        item_dict["fatal_error_reporter"] = error_items
        return item_dict

    def _drain_all_queues(self) -> Dict[str, Any]:
        """Drain all queues of the process except the fatal_error_reporter.

        Should be overriden by subclasses
        """
        # pylint:disable=no-self-use # Tanner (4/12/20): this is neede so method signature matches subclass implementation
        return dict()

    def is_stopped(self) -> bool:
        """Check if the parallel instance is stopped."""
        if not hasattr(self, "_stop_event"):
            raise NotImplementedError(
                "Classes using this mixin must have a _stop_event attribute."
            )
        stop_event = getattr(self, "_stop_event")

        is_set = stop_event.is_set()
        if not isinstance(is_set, bool):
            raise NotImplementedError(
                "The return value from this should always be a bool."
            )
        return is_set

    def is_preparing_for_soft_stop(self) -> bool:
        """Check if the parallel instance is preparing to soft stop."""
        if not hasattr(self, "_soft_stop_event"):
            raise NotImplementedError(
                "Classes using this mixin must have a _soft_stop_event attribute."
            )
        soft_stop_event = getattr(self, "_soft_stop_event")
        if not isinstance(
            soft_stop_event, (threading.Event, multiprocessing.synchronize.Event)
        ):
            raise NotImplementedError(
                "Classes using this mixin must have a _soft_stop_event as either a threading.Event or multiprocessing.Event"
            )
        return soft_stop_event.is_set()
