# -*- coding: utf-8 -*-
"""Functionality to enhance parallelism."""
from __future__ import annotations

import logging
import multiprocessing
import multiprocessing.queues
import multiprocessing.synchronize
import queue
import threading
from typing import Optional
from typing import Tuple
from typing import Union

from .misc import get_formatted_stack_trace


class InfiniteLoopingParallelismMixIn:
    """Mix-in for infinite looping."""

    def __init__(
        self,
        fatal_error_reporter: Union[
            queue.Queue[str], multiprocessing.queues.SimpleQueue[Tuple[Exception, str]]
        ],
        logging_level: int,
        stop_event: Union[threading.Event, multiprocessing.synchronize.Event],
        soft_stop_event: Union[threading.Event, multiprocessing.synchronize.Event],
        minimum_iteration_duration_seconds: Union[float, int] = 0.01,
    ) -> None:
        self._stop_event = stop_event
        self._soft_stop_event = soft_stop_event
        self._fatal_error_reporter = fatal_error_reporter
        self._process_can_be_soft_stopped = True
        self._logging_level = logging_level
        self._minimum_iteration_duration_seconds = minimum_iteration_duration_seconds

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
        queue.Queue[str], multiprocessing.queues.SimpleQueue[Tuple[Exception, str]]
    ]:
        return self._fatal_error_reporter

    def _report_fatal_error(self, the_err: Exception) -> None:
        self._fatal_error_reporter.put(the_err)  # type: ignore # the subclasses all have an instance of fatal error reporter. there may be a more elegant way to handle this to make mypy happy though... (Eli 2/12/20)

    def _setup_before_loop(self) -> None:
        """Perform any necessary setup prior to initiating the infinite loop.

        This can be overridden by the subclass.
        """

    def _teardown_after_loop(self) -> None:
        """Perform any necessary teardown after the infinite loop has exited.

        This can be overridden by the subclass.
        """

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
                print(
                    e
                )  # sometimes fatal errors really mess things up and can't even be reported correctly...so at least print it to STDOUT
                self._report_fatal_error(e)
                return
        while True:
            self._process_can_be_soft_stopped = True
            try:
                self._commands_for_each_run_iteration()
            except Exception as e:  # pylint: disable=broad-except # The deliberate goal of this is to catch everything and put it into the error queue
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
        if perform_teardown_after_loop:
            try:
                self._teardown_after_loop()
            except Exception as e:  # pylint: disable=broad-except # The deliberate goal of this is to catch everything and put it into the error queue
                self._report_fatal_error(e)

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
