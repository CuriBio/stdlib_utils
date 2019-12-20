# -*- coding: utf-8 -*-
import inspect
import os

from stdlib_utils import misc
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
