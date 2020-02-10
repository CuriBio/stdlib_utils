# -*- coding: utf-8 -*-
import logging
import os
import tempfile
import time

from freezegun import freeze_time
from stdlib_utils import configure_logging
from stdlib_utils import loggers
from stdlib_utils import misc


def test_configure_logging__default_args(mocker):
    mocked_basic_config = mocker.patch.object(logging, "basicConfig", autospec=True)
    configure_logging()

    assert (
        logging.Formatter.converter  # pylint: disable=comparison-with-callable
        == time.gmtime  # pylint: disable=comparison-with-callable
    )

    assert mocked_basic_config.call_count == 1
    _, kwargs = mocked_basic_config.call_args_list[0]
    assert set(kwargs.keys()) == set(["level", "format", "handlers"])
    assert kwargs["level"] == logging.DEBUG
    assert (
        kwargs["format"]
        == "[%(asctime)s UTC] %(name)s-{%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    )
    actual_handlers = kwargs["handlers"]
    assert len(actual_handlers) == 1

    # if pytest is automatically capturing stdout, then it does some adjustments to change the output, so the second or clause is needed
    assert actual_handlers[
        0
    ].stream.name == "<stdout>" or "_pytest.capture.EncodedFile" in str(
        type(actual_handlers[0].stream)
    )


@freeze_time("2020-02-10 13:17:22")
def test_configure_logging__with_file_name__creates_dir_using_resource_path(mocker):
    with tempfile.TemporaryDirectory() as tmp_dir:
        mocker.patch.object(misc, "is_frozen_as_exe", autospec=True, return_value=True)
        mocker.patch.object(
            misc, "get_path_to_frozen_bundle", autospec=True, return_value=tmp_dir
        )
        spied_create_dir = mocker.spy(loggers, "create_directory_if_not_exists")
        spied_resource_path = mocker.spy(loggers, "resource_path")
        mocked_basic_config = mocker.patch.object(logging, "basicConfig", autospec=True)
        configure_logging(log_file_prefix="my_log")

        spied_resource_path.assert_called_once_with("logs")
        spied_create_dir.assert_called_once_with(os.path.join(tmp_dir, "logs"))

        assert mocked_basic_config.call_count == 1
        _, kwargs = mocked_basic_config.call_args_list[0]
        assert set(kwargs.keys()) == set(["level", "format", "handlers"])

        actual_handlers = kwargs["handlers"]
        assert len(actual_handlers) == 2
        file_handler = actual_handlers[1]
        assert file_handler.baseFilename == os.path.join(
            tmp_dir, "logs", "my_log__2020_02_10_131722.txt"
        )
