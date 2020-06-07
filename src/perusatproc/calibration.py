# -*- coding: utf-8 -*-

import logging
import os
import tempfile

from perusatproc.metadata import extract_calibration_metadata
from perusatproc.util import run_command

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


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
    metadata = extract_calibration_metadata(metadata_path)

    gf = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    for k in ('gains', 'biases'):
        line = "{}\n".format(" : ".join(str(v) for v in metadata[k]))
        gf.write(line.encode())
    gf.close()

    sf = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    line = "{}\n".format(" : ".join(
        str(v) for v in metadata['solar_irradiances']))
    sf.write(line.encode())
    sf.close()

    cmd = base_cmd.format(src=src_path,
                          dst=dst_path,
                          gainbias_path=gf.name,
                          solarillum_path=sf.name,
                          **metadata)
    run_command(cmd)

    os.unlink(gf.name)
    os.unlink(sf.name)
