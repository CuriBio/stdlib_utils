# -*- coding: utf-8 -*-
from stdlib_utils import InfiniteProcess
from stdlib_utils import InfiniteThread


class InfiniteProcessThatCannotBeSoftStopped(InfiniteProcess):
    def _commands_for_each_run_iteration(self):
        self._process_can_be_soft_stopped = False


class InfiniteProcessThatRasiesError(InfiniteProcess):
    def _commands_for_each_run_iteration(self):
        raise ValueError("test message")


class InfiniteThreadThatRasiesError(InfiniteThread):
    def _commands_for_each_run_iteration(self):
        raise ValueError("test message")


class InfiniteThreadThatCannotBeSoftStopped(InfiniteThread):
    def _commands_for_each_run_iteration(self):
        self._process_can_be_soft_stopped = False
