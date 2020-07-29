# -*- coding: utf-8 -*-
"""Setup configuration."""
from setuptools import find_packages
from setuptools import setup


setup(
    name="stdlib_utils",
    version="0.1.31",
    description="CREATE A DESCRIPTION",
    url="https://git-codecommit.us-east-1.amazonaws.com/v1/repos/stdlib_utils",
    author="Curi Bio",
    author_email="eli@curibio.com",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[],
)
