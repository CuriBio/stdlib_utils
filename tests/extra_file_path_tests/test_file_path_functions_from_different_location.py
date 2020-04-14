# -*- coding: utf-8 -*-
"""These extra tests ensure that file path functions work when called from different locations."""
import os

from stdlib_utils import get_current_file_abs_directory
from stdlib_utils import get_current_file_abs_path


def test_get_current_file_abs_path():
    expected_to_contain = os.path.join(
        "stdlib_utils",
        "tests",
        "extra_file_path_tests",
        "test_file_path_functions_from_different_location.py",
    )
    actual = get_current_file_abs_path()
    assert actual.endswith(expected_to_contain) is True

    # the actual beginning of the absolute path could vary system to system...so just make sure there is something in front of the known portion of the path
    minimum_length = len(expected_to_contain) + 1
    assert len(actual) > minimum_length


def test_get_current_file_abs_directory():
    expected_to_contain = os.path.join("stdlib_utils", "tests", "extra_file_path_tests")
    actual = get_current_file_abs_directory()
    assert actual.endswith(expected_to_contain)

    # the actual beginning of the absolute path could vary system to system...so just make sure there is something in front of the known portion of the path
    minimum_length = len(expected_to_contain) + 1
    assert len(actual) > minimum_length
