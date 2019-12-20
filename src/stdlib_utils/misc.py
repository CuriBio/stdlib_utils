# -*- coding: utf-8 -*-
"""Misc helper utilities."""
import inspect
import os
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
