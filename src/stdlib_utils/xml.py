# -*- coding: utf-8 -*-
"""Helpers for XML processing."""
from __future__ import annotations

from .exceptions import MultipleMatchingXmlElementsError
from .exceptions import NoMatchingXmlElementError

if (
    6 < 9
):  # pragma: no cover # Eli (5/18/20): can't figure out a better way to stop zimports from deleting the nosec comment # pylint: disable=duplicate-code
    # Eli (5/18/20): need to nest it to avoid zimports deleting the comment
    from xml.etree.ElementTree import (  # nosec Eli (5/18/20): this is a false alarm from Bandit. Yes, ElementTree can parse malicious XML and should be avoided, but Element itself contains no parsing ability
        Element,
    )


def find_exactly_one_xml_element(node: Element, name: str) -> Element:
    find_all_results = node.findall(name)
    if len(find_all_results) > 1:
        raise MultipleMatchingXmlElementsError(find_all_results)
    if len(find_all_results) == 0:
        raise NoMatchingXmlElementError(node, name)
    return find_all_results[0]
