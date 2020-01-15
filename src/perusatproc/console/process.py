# -*- coding: utf-8 -*-
"""
Given a path to a PeruSat-1 product, this script peforms all required steps to
form a single calibrated, orthorectified and pansharpened image.

Final output can be a virtual raster or a tiff file.

"""

import argparse
import sys
import logging

from perusatproc import __version__

import subprocess
import xmltodict
import tempfile
import rasterio
import os
from glob import glob
from datetime import datetime

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def process_image(*, src, dst):
    # TODO ...
    pass


def process_product(src, dst):
    volumes = glob(os.path.join(src, 'VOL_*'))
    _logger.info("Num. Volumes: {}".format(len(volumes)))

    os.makedirs(dst, exist_ok=True)

    for volume in volumes:
        ms_img = glob(os.path.join(volume, 'IMG_*_MS_*/*.TIF'))[0]
        p_img = glob(os.path.join(volume, 'IMG_*_P_*/*.TIF'))[0]

        for src_path in [ms_img]:
            name, ext = os.path.splitext(os.path.basename(src_path))
            dst_path = os.path.join(dst, name + ext)
            if not os.path.exists(dst_path):
                process_image(src=src_path, dst=dst_path)

    # TODO ...


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

    parser.add_argument("src", help="path to directory containing product")
    parser.add_argument("dst", help="path to output image")

    parser.add_argument("-co",
                        "--create-options",
                        default="",
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

    if args.mode == 'image':
        process_image(args.src, args.dst, metadata=args.dst)
    else:
        process_product(args.src, args.dst)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()