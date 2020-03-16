# -*- coding: utf-8 -*-

import logging
import os

import rasterio

from perusatproc.metadata import extract_projection_metadata, extract_rpc_metadata
from perusatproc.util import run_command

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
GEOID_PATH = os.path.join(DATA_PATH, 'egm96.grd')
DEM_PATH = os.path.join(DATA_PATH, 'dem')
RPC_COEFF_KEYS = [
    'err_bias',
    'err_rand',
    'line_offset',
    'samp_offset',
    'lat_offset',
    'lon_offset',
    'height_offset',
    'line_scale',
    'samp_scale',
    'lat_scale',
    'lon_scale',
    'height_scale',
    'line_num_coeffs',
    'line_den_coeffs',
    'samp_num_coeffs',
    'samp_den_coeffs',
]


def add_rpc_tags(*, src_path, dst_path, metadata_path):
    metadata = extract_rpc_metadata(metadata_path)

    keys = [
        ('ERR_BIAS', 'err_bias'),
        ('ERR_RAND', 'err_rand'),
        ('LINE_OFF', 'line_offset'),
        ('SAMP_OFF', 'samp_offset'),
        ('LAT_OFF', 'lat_offset'),
        ('LONG_OFF', 'lon_offset'),
        ('HEIGHT_OFF', 'height_offset'),
        ('LINE_SCALE', 'line_scale'),
        ('SAMP_SCALE', 'samp_scale'),
        ('LAT_SCALE', 'lat_scale'),
        ('LONG_SCALE', 'lon_scale'),
        ('HEIGHT_SCALE', 'height_scale'),
    ]
    tags = {k1: metadata[k2] for k1, k2 in keys}
    coeffs_keys = [('LINE_NUM_COEFF', 'line_num_coeffs'),
                   ('LINE_DEN_COEFF', 'line_den_coeffs'),
                   ('SAMP_NUM_COEFF', 'samp_num_coeffs'),
                   ('SAMP_DEN_COEFF', 'samp_den_coeffs')]
    for k, v in coeffs_keys:
        tags[k] = ' '.join([str(v2) for v2 in metadata[v]])

    with rasterio.open(src_path) as src:
        with rasterio.open(dst_path, 'w', **src.profile) as dst:
            dst.write(src.read())
            dst.update_tags(ns='RPC', **tags)


def orthorectify(dem_path=None, geoid_path=None, *, src_path, dst_path):
    base_cmd = """otbcli_OrthoRectification \
      -io.in \"{src}?&skipcarto=true\" \
      -io.out {dst} uint16 \
      -outputs.mode auto \
      -elev.geoid {geoid_path} \
      -elev.dem {dem_path}
    """

    if not geoid_path:
        geoid_path = GEOID_PATH
    if not dem_path:
        dem_path = DEM_PATH

    cmd = base_cmd.format(src=src_path,
                          dst=dst_path,
                          geoid_path=geoid_path,
                          dem_path=dem_path)
    run_command(cmd)
