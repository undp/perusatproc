# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         fibonacci = perusatproc.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

from glob import glob
import argparse
import logging
import os
import sys
import tempfile

from perusatproc import __version__
from perusatproc.calibration import calibrate
from perusatproc.orthorectification import reproject

import rasterio
import rasterio.transform

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

    with tempfile.NamedTemporaryFile(suffix='.tif') as tempf:
        calibrate(src_path=src, dst_path=tempf.name, metadata_path=metadata)
        reproject(src_path=tempf.name, dst_path=dst, metadata_path=metadata)


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

    subparsers = parser.add_subparsers(dest='mode', required=True)

    image_parser = subparsers.add_parser("image", help="calibrate an image")
    image_parser.add_argument("src", help="path to input image")
    image_parser.add_argument("dst", help="path to output image")
    image_parser.add_argument("-m",
                              "--metadata",
                              help="path to metadata XML file")

    product_parser = subparsers.add_parser("product",
                                           help="calibrate a product")
    product_parser.add_argument("src",
                                help="path to directory containing product")
    product_parser.add_argument("dst", help="path to output image")

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

    if args.mode == 'image':
        process_image(args.src, args.dst, metadata=args.metadata)
    else:
        process_product(args.src, args.dst)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
