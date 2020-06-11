# -*- coding: utf-8 -*-

import re

from setuptools import find_packages, setup


with open("fetch_generated_data/__init__.py") as f:
    txt = f.read()
    try:
        version = re.findall(r'^__version__ = "([^"]+)"\r?$', txt, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

setup(
    name="fetch-generated-data",
    version=version,
    python_requires=">=3.7.0",
    install_requires=[
        "numpy==1.18.5",
        "opencv-python==4.2.0.34",
        "argparse-path @ git+ssh://git@github.com/Synthesis-AI-Dev/argparse-path#egg=argparse-path-0.1",
    ],
    include_package_data=True,
    description="Creates synthesis model from pca coefficients",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "fetch-generated-data=fetch_generated_data.main:main",
        ]
    },
)
