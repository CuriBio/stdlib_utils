# -*- coding: utf-8 -*-
from stdlib_utils import SECONDS_TO_SLEEP_BETWEEN_CHECKING_QUEUE_SIZE


def test_polling_times():

    assert SECONDS_TO_SLEEP_BETWEEN_CHECKING_QUEUE_SIZE == 0.05
