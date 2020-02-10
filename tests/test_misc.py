# -*- coding: utf-8 -*-
import ctypes
import functools
import inspect
import os
import signal
import tempfile
import time

from stdlib_utils import create_directory_if_not_exists
from stdlib_utils import is_system_windows
from stdlib_utils import misc
from stdlib_utils import raise_alarm_signal
from stdlib_utils import resource_path

PATH_OF_CURRENT_FILE = os.path.dirname((inspect.stack()[0][1]))


def test_resource_path__returns_from_path_of_current_file_by_default():
    actual_path = resource_path("my_file")
    expected_path = os.path.join(PATH_OF_CURRENT_FILE, "my_file")
    assert actual_path == expected_path


def test_resource_path__returns_from_supplied_base_path_when_provided():
    expected_base = os.path.join("linux", "eli")
    actual_path = resource_path("my_file2", base_path=expected_base)
    expected_path = os.path.join(expected_base, "my_file2")
    assert actual_path == expected_path


def test_resource_path__returns_from_path_of_meipass_when_frozen(mocker):
    mocker.patch.object(misc, "is_frozen_as_exe", autospec=True, return_value=True)
    expected_base = os.path.join("root_dir", "sub_dir")
    mocker.patch.object(
        misc, "get_path_to_frozen_bundle", autospec=True, return_value=expected_base
    )
    actual_path = resource_path("my_file3")
    expected_path = os.path.join(expected_base, "my_file3")
    assert actual_path == expected_path


def test_resource_path__returns_from_path_of_meipass_when_frozen_even_when_base_path_supplied(
    mocker,
):
    mocker.patch.object(misc, "is_frozen_as_exe", autospec=True, return_value=True)
    expected_base = os.path.join("root_dir2", "sub_dir88")
    mocker.patch.object(
        misc, "get_path_to_frozen_bundle", autospec=True, return_value=expected_base
    )
    actual_path = resource_path("my_file4", base_path="somethingcrazy")
    expected_path = os.path.join(expected_base, "my_file4")
    assert actual_path == expected_path


def test_is_system_windows__true_when_true(mocker):
    mocker.patch("os.name", "nt")
    assert is_system_windows() is True


def test_is_system_windows__false_when_linux(mocker):
    mocker.patch("os.name", "posix")
    assert is_system_windows() is False


def dummy_signal_handler(my_list, arg1, arg2):
    my_list[0] = True


def test_raise_alarm_signal__raises_on_linux(mocker):
    is_windows = is_system_windows()
    # Eli (1/9/20) can't really figure out how to mock this very well, so creating a funky call out to a dummy signal handler
    mocker.patch.object(misc, "is_system_windows", autospec=True, return_value=False)
    if is_windows:
        mocked_setitimer = mocker.patch.object(
            signal, "setitimer"
        )  # Eli (1/9/20): intentionally leaving out autospec=True because on windows it doesn't appear that setitimer exists at all in the module
    else:
        mocked_setitimer = mocker.spy(signal, "setitimer")
    a_list = [False]
    signal.signal(14, functools.partial(dummy_signal_handler, a_list))
    if is_windows:
        mocker.patch.object(signal,)
    raise_alarm_signal()
    time.sleep(0.01)
    if not is_windows:
        # if the system is actually linux, make sure to check the live result
        assert a_list[0] is True
    # make sure it was done in a linux-compatible way
    mocked_setitimer.assert_called_once()


def test_raise_alarm_signal__raises_on_windows(mocker):
    is_windows = is_system_windows()
    # Eli (1/9/20) can't really figure out how to mock this very well, so creating a funky call out to a dummy signal handler
    mocker.patch.object(misc, "is_system_windows", autospec=True, return_value=True)
    a_list = [False]
    if is_windows:
        mocked_cdll = mocker.spy(ctypes, "CDLL")
    else:
        mocked_cdll = mocker.patch.object(
            ctypes, "CDLL", autospec=True, return_value={"raise": lambda x: None}
        )

    signal.signal(14, functools.partial(dummy_signal_handler, a_list))
    raise_alarm_signal()
    time.sleep(0.01)
    if is_windows:
        # if the system is actually linux, make sure to check the live result
        assert a_list[0] is True
    # make sure it was done in a windows-compatible way
    mocked_cdll.assert_called_once_with("ucrtbase")


def test_create_directory_if_not_exists__when_no_directory_present():
    with tempfile.TemporaryDirectory() as tmp_dir:
        the_dir = os.path.join(tmp_dir, "logs")
        create_directory_if_not_exists(the_dir)
        assert os.path.isdir(the_dir) is True


def test_create_directory_if_not_exists__when_directory_already_present():
    # would raise a FileExistsError if failing
    with tempfile.TemporaryDirectory() as tmp_dir:
        the_dir = os.path.join(tmp_dir, "logs")
        os.makedirs(the_dir)
        create_directory_if_not_exists(the_dir)
        assert os.path.isdir(the_dir) is True
