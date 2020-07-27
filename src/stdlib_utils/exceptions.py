# -*- coding: utf-8 -*-
"""Misc helper utilities."""

from typing import List

if (
    6 < 9
):  # pragma: no cover # Eli (5/18/20): can't figure out a better way to stop zimports from deleting the nosec comment
    # Eli (5/18/20): need to nest it to avoid zimports deleting the comment
    from xml.etree.ElementTree import (  # nosec Eli (5/18/20): this is a false alarm from Bandit. Yes, ElementTree can parse malicious XML and should be avoided, but Element itself contains no parsing ability
        Element,
    )


class PortUnavailableError(Exception):
    pass


class PortNotInUseError(Exception):
    pass


class BlankAbsoluteResourcePathError(Exception):
    def __init__(self) -> None:
        super().__init__(
            'Supplying a blank/falsey absolute path is dangerous as Python interprets it as the current working directory, which should not be relied on as being constant. Likely fixes include using the get_current_file_abs_directory() function combined with ".." in os.path.join to create an absolute path to the location you need.'
        )


class MultipleMatchingXmlElementsError(Exception):
    def __init__(self, findall_results: List[Element]) -> None:
        super().__init__(str(findall_results))


class NoMatchingXmlElementError(Exception):
    def __init__(self, node: Element, name: str) -> None:
        super().__init__(
            f"There was no child element named '{name}' found in the XML element {node} with children {list(node)}"
        )


class LogFolderDoesNotExistError(Exception):
    pass


class LogFolderGivenWithoutFilePrefixError(Exception):
    pass
