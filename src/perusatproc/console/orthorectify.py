# -*- coding: utf-8 -*-
"""
Adds projection and RPC tags to an image from its metadata files, and them
orthorectifies it using the RPC data and a DEM image.

If no DEM is provided, a DEM from SRTM is used (1-arc second / 30m aprox GSD).

"""

import argparse
import logging
import os
import sys
import tempfile

from perusatproc import __version__
from perusatproc.orthorectification import reproject, add_rpc_tags, orthorectify

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def process_image(rpc_metadata_path=None,
                  *,
                  src_path,
                  dst_path,
                  metadata_path,
                  dem_path):

    with tempfile.NamedTemporaryFile(suffix='.tif') as tempf2:
        with tempfile.NamedTemporaryFile(suffix='.tif') as tempf1:
            _logger.info("Reproject %s and write %s", src_path, tempf1.name)
            reproject(src_path=src_path,
                      dst_path=tempf1.name,
                      metadata_path=metadata_path)

            _logger.info("Add RPC tags from %s and write %s", tempf1.name,
                         tempf2.name)
            add_rpc_tags(src_path=tempf1.name,
                         dst_path=tempf2.name,
                         metadata_path=rpc_metadata_path)

        _logger.info("Orthorectify %s and write %s", tempf2.name, dst_path)
        orthorectify(src_path=tempf2.name,
                     dst_path=dst_path,
                     metadata_path=metadata_path,
                     dem_path=dem_path)


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
    parser.add_argument("-m",
                        "--metadata",
                        required=True,
                        help="path to metadata DIMAP XML file")
    parser.add_argument("--rpc-metadata",
                        help="path to RPC metadata XML file " + \
                             "(default: get path from DIMAP metadata file)")
    parser.add_argument("--dem", help="path to directory containing DEM files")

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

    process_image(src_path=args.src,
                  dst_path=args.dst,
                  metadata_path=args.metadata,
                  rpc_metadata_path=args.rpc_metadata,
                  dem_path=args.dem)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
