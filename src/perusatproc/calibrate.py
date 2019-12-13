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
import tempfile
from datetime import datetime

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def run_command(cmd):
    _logger.info(cmd)
    subprocess.run(cmd, shell=True, check=True)


def extract_metadata(metadata_path):
    with open(metadata_path) as f:
        body = xmltodict.parse(f.read())

    doc = body['Dimap_Document']

    # Image date and time
    strip_source = doc['Dataset_Sources']['Source_Identification'][
        'Strip_Source']
    date_str, time_str = strip_source['IMAGING_DATE'], strip_source[
        'IMAGING_TIME']
    date = datetime.strptime(date_str, "%Y-%m-%d")
    time = datetime.strptime(time_str, "%H:%M:%S")

    geom_values = doc['Geometric_Data']['Use_Area']['Located_Geometric_Values']

    # Sun elevation and azimuth angles
    solar_incidences = geom_values['Solar_Incidences']
    sun_elev = float(solar_incidences['SUN_ELEVATION'])
    sun_azim = float(solar_incidences['SUN_AZIMUTH'])

    # Viewing elevation and azimuth angles
    acquisition_angles = geom_values['Acquisition_Angles']
    view_elev = float(acquisition_angles['VIEWING_ANGLE'])
    view_azim = float(acquisition_angles['AZIMUTH_ANGLE'])

    # Gains and biases for each band
    band_spectral_range = doc['Radiometric_Data']['Radiometric_Calibration'][
        'Instrument_Calibration']['Band_Measurement_List']
    band_radiances = band_spectral_range['Band_Radiance']
    gains = [float(r['GAIN']) for r in band_radiances]
    biases = [float(r['BIAS']) for r in band_radiances]

    # Solar irradiance values for each band
    band_solar_irradiances = band_spectral_range['Band_Solar_Irradiance']
    solar_irradiances = [float(r['VALUE']) for r in band_solar_irradiances]

    return dict(minute=time.minute,
                hour=time.hour,
                day=date.day,
                month=date.month,
                year=date.year,
                sun_elev=sun_elev,
                sun_azim=sun_azim,
                view_elev=view_elev,
                view_azim=view_azim,
                gains=gains,
                biases=biases,
                solar_irradiances=solar_irradiances)


def calibrate(*, src_path, dst_path, metadata_path):
    base_cmd = """otbcli_OpticalCalibration \
      -in {src} \
      -out {dst} uint16 \
      -milli true \
      -level toa \
      -acqui.minute {minute} \
      -acqui.hour {hour} \
      -acqui.day {day} \
      -acqui.month {month} \
      -acqui.year {year} \
      -acqui.sun.elev {sun_elev} \
      -acqui.sun.azim {sun_azim} \
      -acqui.view.elev {view_elev} \
      -acqui.view.azim {view_azim} \
      -acqui.gainbias {gainbias_path} float \
      -acqui.solarilluminations {solarillum_path} float
    """
    metadata = extract_metadata(metadata_path)

    with tempfile.NamedTemporaryFile() as gf:
        for k in ('gains', 'biases'):
            line = "{}\n".format(" : ".join(str(v) for v in metadata[k]))
            gf.write(line.encode())
            gf.flush()

        with tempfile.NamedTemporaryFile() as sf:
            line = "{}\n".format(" : ".join(str(v) for v in metadata['solar_irradiances']))
            sf.write(line.encode())
            sf.flush()

            cmd = base_cmd.format(src=src_path,
                                  dst=dst_path,
                                  gainbias_path=gf.name,
                                  solarillum_path=sf.name,
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

    calibrate(src_path=args.src,
              dst_path=args.dst,
              metadata_path=args.metadata)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
