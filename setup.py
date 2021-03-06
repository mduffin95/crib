#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup  # type: ignore


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="crib",
    version="0.1.0",
    license="GPLv3",
    description="Scrape properties on rightmove.co.uk",
    long_description="%s\n%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="David Zuber",
    author_email="zuber.david@gmx.de",
    url="https://github.com/storax/crib",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ],
    keywords=[],
    setup_requires=["pytest-runner"],
    install_requires=[
        "attrs",
        "cattrs",
        "cerberus",
        "chardet",
        "click",
        "click_log",
        "cmocean",
        "flask-jwt-extended",
        "geopandas",
        "matplotlib",
        "numpy",
        "pluggy",
        "pymongo",
        "pyyaml",
        "quart",
        "quart_cors",
        "requests_async",
        "scipy",
        "scrapy",
        "shapely",
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-black",
        "pytest-flake8",
        "pytest-isort",
        "pytest-mypy",
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={"console_scripts": ["crib = crib.cli:main"]},
)
