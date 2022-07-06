#!/usr/bin/env python
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
    author_email="krz.liszka@gmail.com"
)
