# -*- coding: utf-8 -*-
"""
This script bundles a pancromatic (P) and multispectral (MS) image to form a
pansharpened image.

"""

from glob import glob
import argparse
import logging
import os
import sys
import tempfile

from perusatproc import __version__
from perusatproc.pansharpening import pansharpen

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description=
        "Perform radiometric calibration from Level 2A to Top-of-Atmosphere (ToA)"
    )

    parser.add_argument("--version",
                        action="version",
                        version="perusatproc {ver}".format(ver=__version__))

    parser.add_argument("-v",
                        "--verbose",
                        dest="loglevel",
                        help="set loglevel to INFO",
                        action="store_const",
                        const=logging.INFO)
    parser.add_argument("-vv",
                        "--very-verbose",
                        dest="loglevel",
                        help="set loglevel to DEBUG",
                        action="store_const",
                        const=logging.DEBUG)

    parser.add_argument("ms_src", help="path to input MS (multispectral) image")
    parser.add_argument("p_src", help="path to input P (panchromatic) image")
    parser.add_argument("dst", help="path to output image")

    parser.add_argument("-co",
                        "--create-options",
                        nargs="+",
                        help="GDAL create options")

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel,
                        stream=sys.stdout,
                        format=logformat,
                        datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    _logger.debug("Args: %s", args)

    pansharpen(args.p_src, args.ms_src, args.dst, create_options=args.create_options)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
