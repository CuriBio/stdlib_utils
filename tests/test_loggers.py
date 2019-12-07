# -*- coding: utf-8 -*-
import logging
import time

from stdlib_utils import configure_logging


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
