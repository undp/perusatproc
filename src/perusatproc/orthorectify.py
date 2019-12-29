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

import argparse
import sys
import logging

from perusatproc import __version__

import subprocess
import xmltodict
from datetime import datetime
import os
import rasterio
import rasterio.transform


__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'data')
GEOID_PATH = os.path.join(DATA_PATH, 'egm96.grd')


def run_command(cmd):
    _logger.info(cmd)
    subprocess.run(cmd, shell=True, check=True)


def extract_metadata(metadata_path):
    with open(metadata_path) as f:
        body = xmltodict.parse(f.read())

    doc = body['Dimap_Document']

    # Raster size
    raster_dimensions = doc['Raster_Data']['Raster_Dimensions']
    sizex = int(raster_dimensions['NCOLS'])
    sizey = int(raster_dimensions['NROWS'])

    # Raster extent
    vertices = doc['Dataset_Content']['Dataset_Extent']['Vertex']
    lats = [float(v['LAT']) for v in vertices]
    lons = [float(v['LON']) for v in vertices]
    minx, maxx = min(lons), max(lons)
    miny, maxy = min(lats), max(lats)

    return dict(sizex=sizex,
                sizey=sizey,
                ulx=minx,
                uly=maxy,
                lrx=maxx,
                lry=miny)


def orthorectify(*, src_path, dst_path, metadata_path, dem_path):
    base_cmd = """otbcli_OrthoRectification \
      -io.in {src} \
      -io.out {dst} uint16 \
      -map wgs \
      -outputs.mode auto \
      -outputs.ulx {ulx} \
      -outputs.uly {uly} \
      -outputs.lrx {lrx} \
      -outputs.lry {lry} \
      -outputs.sizex {sizex} \
      -outputs.sizey {sizey} \
      -elev.geoid {geoid_path} \
      {elev_dem}
    """
    metadata = extract_metadata(metadata_path)

    elev_dem = '-elev.dem {}'.format(dem_path) if dem_path else ''
    cmd = base_cmd.format(src=src_path,
                          dst=dst_path,
                          geoid_path=GEOID_PATH,
                          elev_dem=elev_dem,
                          **metadata)
    run_command(cmd)


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
                        help="path to metadata XML file")
    parser.add_argument("--dem",
                        help="path to directory containing DEM files")

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

    orthorectify(src_path=args.src,
              dst_path=args.dst,
              metadata_path=args.metadata, 
              dem_path=args.dem)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
