# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

import pytest
from stdlib_utils import find_exactly_one_xml_element
from stdlib_utils import MultipleMatchingXmlElementsError
from stdlib_utils import NoMatchingXmlElementError


def test_find_exactly_one_xml_element__raises_error_if_no_matching_element():
    root_node = Element("CustomProgram")
    SubElement(root_node, "blah")
    with pytest.raises(NoMatchingXmlElementError, match=r".*notthere.*blah.*"):
        find_exactly_one_xml_element(root_node, "notthere")


def test_find_exactly_one_xml_element__raises_error_if_multiple_matching_elements():
    root_node = Element("CustomProgram")
    SubElement(root_node, "blah")
    SubElement(root_node, "blah")
    with pytest.raises(MultipleMatchingXmlElementsError, match=r".*blah.*blah.*"):
        find_exactly_one_xml_element(root_node, "blah")


def test_find_exactly_one_xml_element__returns_matching_element():
    root_node = Element("CustomProgram")
    blah_node = SubElement(root_node, "blah")
    expected_text = "mytext"
    blah_node.text = expected_text
    SubElement(root_node, "blah4")
    actual_node = find_exactly_one_xml_element(root_node, "blah")
    assert actual_node.text == expected_text
