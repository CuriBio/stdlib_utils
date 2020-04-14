# -*- coding: utf-8 -*-
"""Misc helper utilities."""


class PortUnavailableError(Exception):
    pass


class PortNotInUseError(Exception):
    pass


class BlankAbsoluteResourcePathError(Exception):
    def __init__(self) -> None:
        super().__init__(
            'Supplying a blank/falsey absolute path is dangerous as Python interprets it as the current working directory, which should not be relied on as being constant. Likely fixes include using the get_current_file_abs_directory() function combined with ".." in os.path.join to create an absolute path to the location you need.'
        )
