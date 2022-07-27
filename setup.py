#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
from setuptools import setup


def read(*args):
    """
    Read file
    """

    file = os.path.join(os.path.abspath(os.path.dirname(__file__)), *args)
    sys.stdout.write(file)
    with io.open(file, encoding="utf-8", mode="rt") as fp:
        return fp.read()


with open("README.md") as readme_file:
    readme = readme_file.read()


setup(
    author="Krzysztof Liszka",
    author_email="krz.liszka@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    description="Python 3 API wrapper for Garmin Connect",
    name="garminconnect",
    keywords=["garmin connect", "api", "client"],
    license="MIT license",
    install_requires=["requests", "cloudscraper"],
    long_description_content_type="text/markdown",
    long_description=readme,
    url="https://github.com/krzliszka/garmin-connect",
    packages=["garminconnect"],
    version="0.1.46"
)
