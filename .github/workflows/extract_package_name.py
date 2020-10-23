# -*- coding: utf-8 -*-
"""A cross-platform way in GitHub workflows to extract package version."""
import inspect
import os
import re

PATH_OF_CURRENT_FILE = os.path.dirname((inspect.stack()[0][1]))

# python3 .github/workflows/extract_package_name.py


def main() -> None:
    package_name_regex = re.compile(r"    name=\"(\w+)\"")
    with open(
        os.path.join(PATH_OF_CURRENT_FILE, os.pardir, os.pardir, "setup.py"), "r"
    ) as in_file:
        content = in_file.read()
        match = re.search(package_name_regex, content)
        if match is None:
            raise NotImplementedError("A match in setup.py should always be found.")
        print(match.group(1))  # allow-print


if __name__ == "__main__":
    main()
