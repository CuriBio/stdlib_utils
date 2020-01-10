# -*- coding: utf-8 -*-
"""Misc helper utilities."""
import ctypes
import inspect
import os
import signal
import sys
from typing import Optional


def is_frozen_as_exe() -> bool:
    """Check if script is frozen as an exe using PyInstaller.

    Eli (12/20/19) cannot figure out how to mock sys, so this is not
    unit tested.
    """
    return hasattr(sys, "_MEIPASS")


def get_path_to_frozen_bundle() -> str:
    """Return path to the running bundle made by PyInstaller.

    Eli (12/20/19) cannot figure out how to mock sys, so this is not
    unit tested.
    """
    return getattr(sys, "_MEIPASS")


def resource_path(relative_path: str, base_path: Optional[str] = None):
    """Get a path to a resource that works for development and frozen files.

    Args:
        relative_path: an additional path to append
        base_path: If left blank, this will default to the path to the file that called this function. When frozen as EXE, this will always be the path to the Pyinstaller directory.

    For use specifically with files compiled to windows EXE by pyinstaller.
    """
    if base_path is None:
        path_to_file_that_called_this_function = os.path.dirname(  # pylint: disable=invalid-name
            (inspect.stack()[1][1])
        )
        base_path = path_to_file_that_called_this_function
    if is_frozen_as_exe():
        base_path = get_path_to_frozen_bundle()
    return os.path.join(base_path, relative_path)


def is_system_windows() -> bool:
    """Check if running on windows."""
    system_type = os.name
    return system_type == "nt"


def raise_alarm_signal():
    """Raise signal in a UNIX and Windows compatible manner.

    Raises signal.SIGALRM which may not exist on windows, but is 14 as
    an int. Raise it as fast as possible. In Python 3.8, raise_signal
    may be a cross-platform option.
    """
    if is_system_windows():
        # from https://stackoverflow.com/questions/14457723/can-i-raise-a-signal-from-python
        ucrtbase = ctypes.CDLL("ucrtbase")
        c_raise = ucrtbase["raise"]
        c_raise(14)
    else:
        signal.setitimer(signal.ITIMER_REAL, 0.001)
