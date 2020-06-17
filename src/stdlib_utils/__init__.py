# -*- coding: utf-8 -*-
"""Helper utilities only requiring the standard library."""
from . import loggers
from . import misc
from . import parallelism_utils
from . import ports
from .exceptions import BlankAbsoluteResourcePathError
from .exceptions import LogMessageNotFoundError
from .exceptions import MultipleMatchingXmlElementsError
from .exceptions import NoMatchingXmlElementError
from .exceptions import PortNotInUseError
from .exceptions import PortUnavailableError
from .loggers import configure_logging
from .misc import create_directory_if_not_exists
from .misc import get_current_file_abs_directory
from .misc import get_current_file_abs_path
from .misc import get_formatted_stack_trace
from .misc import get_path_to_frozen_bundle
from .misc import is_frozen_as_exe
from .misc import is_system_windows
from .misc import print_exception
from .misc import raise_alarm_signal
from .misc import resource_path
from .multiprocessing_utils import InfiniteProcess
from .parallelism_framework import InfiniteLoopingParallelismMixIn
from .parallelism_utils import invoke_process_run_and_check_errors
from .parallelism_utils import put_log_message_into_queue
from .ports import confirm_port_available
from .ports import confirm_port_in_use
from .ports import is_port_in_use
from .queue_utils import find_log_message_in_queue
from .queue_utils import is_queue_eventually_empty
from .queue_utils import is_queue_eventually_not_empty
from .queue_utils import safe_get
from .queue_utils import SimpleMultiprocessingQueue
from .threading_utils import InfiniteThread
from .xml import find_exactly_one_xml_element

__all__ = [
    "configure_logging",
    "resource_path",
    "is_frozen_as_exe",
    "get_formatted_stack_trace",
    "get_path_to_frozen_bundle",
    "is_system_windows",
    "create_directory_if_not_exists",
    "raise_alarm_signal",
    "misc",
    "loggers",
    "InfiniteProcess",
    "SimpleMultiprocessingQueue",
    "invoke_process_run_and_check_errors",
    "find_exactly_one_xml_element",
    "MultipleMatchingXmlElementsError",
    "NoMatchingXmlElementError",
    "ports",
    "confirm_port_in_use",
    "confirm_port_available",
    "is_queue_eventually_empty",
    "is_queue_eventually_not_empty",
    "is_port_in_use",
    "PortUnavailableError",
    "PortNotInUseError",
    "BlankAbsoluteResourcePathError",
    "InfiniteThread",
    "InfiniteLoopingParallelismMixIn",
    "put_log_message_into_queue",
    "print_exception",
    "get_current_file_abs_directory",
    "get_current_file_abs_path",
    "parallelism_utils",
    "safe_get",
    "find_log_message_in_queue",
    "LogMessageNotFoundError",
]
