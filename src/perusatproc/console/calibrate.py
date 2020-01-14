# -*- coding: utf-8 -*-
"""
This script performs ToA optical calibration to an image

"""

from glob import glob
import argparse
import logging
import os
import sys
import tempfile

from perusatproc import __version__
from perusatproc.calibration import calibrate

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def process_image(src, dst, metadata=None):
    if not metadata:
        _logger.info(
            "Metadata file not provided. Going to look for XML file in src image directory."
        )
        src_dirname = os.path.dirname(src)
        metadata_glob_path = os.path.join(src_dirname, 'DIM_*.XML')
        metadata_paths = glob(metadata_glob_path)
        if not metadata_paths:
            raise RuntimeError(
                'No metadata file found at {}. ' \
                'Please provide one with -m/--metadata.'.format(src_dirname))
        metadata = metadata_paths[0]

    _logger.info("Metadata file: {}".format(metadata))

    calibrate(src_path=src, dst_path=dst, metadata_path=metadata)


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

    parser.add_argument("src", help="path to input image")
    parser.add_argument("dst", help="path to output image")
    parser.add_argument("-m", "--metadata", help="path to metadata XML file")

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

    process_image(args.src, args.dst, metadata=args.metadata)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
