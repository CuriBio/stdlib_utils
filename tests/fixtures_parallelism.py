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
]


class InfiniteProcessThatCannotBeSoftStopped(InfiniteProcess):
    def _commands_for_each_run_iteration(self):
        self._process_can_be_soft_stopped = False


class InfiniteProcessThatRaisesError(InfiniteProcess):
    def _commands_for_each_run_iteration(self):
        raise ValueError("test message")


class InfiniteThreadThatRaisesError(InfiniteThread):
    def _commands_for_each_run_iteration(self):
        raise ValueError("test message")


class InfiniteThreadThatCannotBeSoftStopped(InfiniteThread):
    def _commands_for_each_run_iteration(self):
        self._process_can_be_soft_stopped = False
