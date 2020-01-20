# -*- coding: utf-8 -*-
"""
    Setup file for perusatproc.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.0a1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from pkg_resources import VersionConflict, require
from setuptools import setup

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)


if __name__ == "__main__":
    setup(
        use_pyscaffold=True,
        data_files=[
            ('perusatproc/data/dem', ['data/dem/S12W077.hgt','data/dem/S12W078.hgt','data/dem/S13W077.hgt','data/dem/S13W078.hgt']),
            ('perusatproc/data', ['data/egm96.grd']),
        ]
    )
