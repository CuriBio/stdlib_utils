# -*- coding: utf-8 -*-
import logging
from unittest import mock

from stdlib_utils import InfiniteProcess
from stdlib_utils import InfiniteThread

# Eli (5/7/20): pylint was complaining about duplicate code, so moved to common fixtrue
init_test_args_InfiniteLoopingParallelismMixIn = [
    logging.INFO,
    mock.ANY,
    mock.ANY,
    mock.ANY,
    mock.ANY,
]


class InfiniteProcessThatRaisesError(InfiniteProcess):
    def _commands_for_each_run_iteration(self):
        raise ValueError("test message")


class InfiniteProcessThatRaisesErrorInTeardown(InfiniteProcess):
    def _teardown_after_loop(self):
        raise ValueError("error during teardown")


class InfiniteProcessThatCannotBeSoftStopped(InfiniteProcess):
    def _commands_for_each_run_iteration(self):
        self._process_can_be_soft_stopped = False


class InfiniteProcessThatCountsIterations(InfiniteProcess):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_iterations: int = 0

    def _commands_for_each_run_iteration(self):
        self._num_iterations += 1

    def get_num_iterations(self) -> int:
        return self._num_iterations


class InfiniteProcessThatTracksSetup(InfiniteProcessThatCountsIterations):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_setup: bool = False

    def _setup_before_loop(self):
        self._is_setup = True

    def is_setup(self) -> bool:
        return self._is_setup


class InfiniteProcessThatRaisesErrorInSetup(InfiniteProcessThatCountsIterations):
    def _setup_before_loop(self):
        raise ValueError("error during setup")


class InfiniteThreadThatRaisesError(InfiniteThread):
    def _commands_for_each_run_iteration(self):
        raise ValueError("test message")


class InfiniteThreadThatCannotBeSoftStopped(InfiniteThread):
    def _commands_for_each_run_iteration(self):
        self._process_can_be_soft_stopped = False


class InfiniteThreadThatCountsIterations(InfiniteThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_iterations: int = 0

    def _commands_for_each_run_iteration(self):
        self._num_iterations += 1

    def get_num_iterations(self) -> int:
        return self._num_iterations


class InfiniteThreadThatTracksSetup(InfiniteThreadThatCountsIterations):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_setup: bool = False

    def _setup_before_loop(self):
        self._is_setup = True

    def is_setup(self) -> bool:
        return self._is_setup
