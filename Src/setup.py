"""Setup.py file for installation without pip"""

#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="PyPLUTO",
    version="1.0",
    description="Python Visualisation module for PLUTO",
    author="G. Mattia, D. Crocco, ...",
    author_email="mattia@fi.infn.it",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
