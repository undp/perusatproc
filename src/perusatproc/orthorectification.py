# -*- coding: utf-8 -*-

import logging
import os

import rasterio

from perusatproc.metadata import extract_projection_metadata
from perusatproc.util import run_command

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..',
                         '..', 'data')
GEOID_PATH = os.path.join(DATA_PATH, 'egm96.grd')


def reproject(*, src_path, dst_path, metadata_path):
    metadata = extract_projection_metadata(metadata_path)

    with rasterio.open(src_path) as ds:
        profile = ds.profile.copy()
        transform = rasterio.transform.from_bounds(west=metadata['ulx'],
                                                   south=metadata['lry'],
                                                   east=metadata['lrx'],
                                                   north=metadata['uly'],
                                                   width=metadata['sizex'],
                                                   height=metadata['sizey'])

        profile.update(transform=transform, crs='epsg:4326')
        with rasterio.open(dst_path, 'w', **profile) as wds:
            wds.write(ds.read())


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
    metadata = extract_projection_metadata(metadata_path)

    elev_dem = '-elev.dem {}'.format(dem_path) if dem_path else ''
    cmd = base_cmd.format(src=src_path,
                          dst=dst_path,
                          geoid_path=GEOID_PATH,
                          elev_dem=elev_dem,
                          **metadata)
    run_command(cmd)
