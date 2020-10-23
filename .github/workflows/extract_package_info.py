# -*- coding: utf-8 -*-
"""A cross-platform way in GitHub workflows to extract package version."""
import inspect
import os
import re
import sys
from typing import Pattern

PATH_OF_CURRENT_FILE = os.path.dirname((inspect.stack()[0][1]))

# python3 .github/workflows/extract_package_info.py package_name
# python3 .github/workflows/extract_package_info.py package_version


def _extract_info(regex: Pattern[str]) -> None:
    with open(
        os.path.join(PATH_OF_CURRENT_FILE, os.pardir, os.pardir, "setup.py"), "r"
    ) as in_file:
        content = in_file.read()
        match = re.search(regex, content)
        if match is None:
            raise NotImplementedError("A match in setup.py should always be found.")
        print(match.group(1))  # allow-print


def package_name() -> None:
    regex = re.compile(r"    name=\"(\w+)\"")
    _extract_info(regex)


def package_version() -> None:
    regex = re.compile(r"    version=\"(.+?)\"")
    _extract_info(regex)


if __name__ == "__main__":
    if sys.argv[1] == "package_name":
        package_name()
    elif sys.argv[1] == "package_version":
        package_version()
