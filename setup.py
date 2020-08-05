# -*- coding: utf-8 -*-
"""Setup configuration."""
from setuptools import find_packages
from setuptools import setup


setup(
    name="stdlib_utils",
    version="0.2.1",
    description="Various utility functions and classes using only the Python standard lib",
    url="https://github.com/CuriBio/stdlib-utils",
    author="Curi Bio",
    author_email="contact@curibio.com",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[],
)
