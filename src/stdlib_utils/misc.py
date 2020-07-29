# -*- coding: utf-8 -*-
"""Misc helper utilities."""
import ctypes
import inspect
import os
import signal
import struct
import sys
import traceback
from typing import IO
from typing import Optional
from typing import Union
from uuid import UUID
from zlib import crc32

from .exceptions import BlankAbsoluteResourcePathError


def calculate_crc32_bytes_of_large_file(
    file_handle: IO[bytes], skip_first_n_bytes: int = 0
) -> bytes:
    """Calculate the CRC32 checksum in a memory-efficient manner.

    Modified from: https://stackoverflow.com/questions/1742866/compute-crc-of-file-in-python

    Args:
        file_handle: the file handle to process. Should be opened in 'rb' mode
        skip_first_n_bytes: For cases when a checksum has been written in as the first bytes of a file (e.g. in an H5 userblock), the calculation can skip those bytes

    Returns:
        The CRC32 checksum as bytes
    """
    checksum = 0
    if skip_first_n_bytes > 0:
        file_handle.read(skip_first_n_bytes)
    while True:
        itered_bytes = file_handle.read(65536)
        if not itered_bytes:
            break
        checksum = crc32(itered_bytes, checksum)
    return struct.pack(">I", checksum)


def calculate_crc32_hex_of_large_file(
    file_handle: IO[bytes], skip_first_n_bytes: int = 0
) -> str:
    """Calcuates the lowercase zero-padded hex string of a file."""
    checksum_bytes = calculate_crc32_bytes_of_large_file(
        file_handle, skip_first_n_bytes=skip_first_n_bytes
    )
    checksum_int = struct.unpack(">I", checksum_bytes)[0]
    return ("%08X" % (checksum_int & 0xFFFFFFFF)).lower()


def write_crc32_to_file_head(file_handle: IO[bytes]) -> None:
    """Write a CRC32 checksum over the first 4 bytes of the file.

    This is often used to facilitate encoding a CRC32 checksum in the Userblock of an H5 file.

    Args:
        file_handle: the file should be opened in 'rb+' mode
    """
    checksum_bytes = calculate_crc32_bytes_of_large_file(
        file_handle, skip_first_n_bytes=4
    )
    file_handle.seek(0)
    file_handle.write(checksum_bytes)


def get_current_file_abs_path() -> str:
    """Return the absolute path of the file that called this function."""
    return inspect.stack()[1][1]


def get_current_file_abs_directory() -> str:
    """Return the absolute directory of the file that called this function.

    The implementation cannot make a subcall to
    get_current_file_abs_path because that would add an additional item
    to the call stack.
    """
    return os.path.dirname((inspect.stack()[1][1]))


def is_frozen_as_exe() -> bool:
    """Check if script is frozen as an exe using PyInstaller.

    Eli (12/20/19) cannot figure out how to mock sys, so this is not
    unit tested.
    """
    return hasattr(sys, "_MEIPASS")


def get_path_to_frozen_bundle() -> str:  # pragma: no cover
    """Return path to the running bundle made by PyInstaller.

    Eli (12/20/19) cannot figure out how to mock sys, so this is not
    unit tested.
    """
    path_to_bundle = getattr(sys, "_MEIPASS")
    if not isinstance(path_to_bundle, str):
        raise NotImplementedError(
            "The _MEIPASS sys attribute should always be a string."
        )
    return path_to_bundle


def resource_path(relative_path: str, base_path: Optional[str] = None) -> str:
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
    if base_path == "":
        raise BlankAbsoluteResourcePathError()
    if is_frozen_as_exe():
        base_path = get_path_to_frozen_bundle()
    return os.path.join(base_path, relative_path)


def is_system_windows() -> bool:
    """Check if running on windows."""
    system_type = os.name
    return system_type == "nt"


def raise_alarm_signal() -> None:
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


def create_directory_if_not_exists(the_dir: str) -> None:
    if not os.path.exists(the_dir):
        os.makedirs(the_dir)


def get_formatted_stack_trace(e: Exception) -> str:
    # format the stack trace (Eli 2/7/20 couldn't figure out a way to get the stack trace from the exception itself once it had passed back into the main process, so need to grab it explicitly here) https://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st
    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(
        e.__traceback__
    )  # add limit=??
    pretty = traceback.format_list(stack)
    formatted_stack_trace = "".join(pretty) + "\n  {} {}".format(e.__class__, e)
    return formatted_stack_trace


def print_exception(the_exception: Exception, call_id: Union[UUID, str]) -> None:
    print_warning_msg = "IMPORTANT: This fatal error message is being printed to the console before attempting to be logged. Confirm it is in the log file before closing the console. Screenshot or copy the console to save the error if it is not in the log!"
    stack_trace = get_formatted_stack_trace(the_exception)
    msg = f"{print_warning_msg}\nID of call to print: {call_id}\n{stack_trace}"
    print(msg)  # allow-print
