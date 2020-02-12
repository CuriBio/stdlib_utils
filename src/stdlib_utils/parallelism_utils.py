# -*- coding: utf-8 -*-
"""Functionality to enhance parallelism."""
from typing import Optional


class InfiniteLoopingParallelismMixIn:
    """Mix-in for infinite looping."""

    def _report_fatal_error(self, the_err: Exception) -> None:
        self._fatal_error_reporter.put(the_err)  # type: ignore # the subclasses all have an instance of fatal error reporter. there may be a more elegant way to handle this to make mypy happy though... (Eli 2/12/20)

    def run(self, num_iterations: Optional[int] = None):
        """Run the thread.

        Args:
            num_iterations: typically used for unit testing to just execute one or a few cycles. if left as None will loop infinitely

        This sets up the basic flow control and error handling for the thread.
        Subclasses should implement functionality to be executed during each
        cycle in the _commands_for_each_run_iteration method.
        """
        if num_iterations is None:
            num_iterations = -1
        completed_iterations = 0
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

    def _commands_for_each_run_iteration(self):
        """Execute additional commands inside the run loop."""

    def stop(self):
        """Safely stops the process."""
        self._stop_event.set()

    def soft_stop(self):
        """Stop the process when the process indicates it is OK to do so.

        Typically useful for unit testing. For example waiting until all
        queued up items have been handled.
        """
        self._soft_stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def is_preparing_for_soft_stop(self):
        return self._soft_stop_event.is_set()
