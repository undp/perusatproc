# -*- coding: utf-8 -*-

import logging
import os
import struct

from functools import reduce

from osgeo import gdal, gdalconst
import rasterio

from perusatproc.metadata import extract_projection_metadata, extract_rpc_metadata
from perusatproc.util import run_command

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..',
                         '..', 'data')
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


def encode_double(value):
    return struct.pack("<d", value)


def encode_rpc_tag(metadata):
    res = None
    for key in RPC_COEFF_KEYS:
        value = metadata[key]
        if isinstance(value, list):
            enc_values = [encode_double(v) for v in value]
            encoded_value = reduce((lambda x, y: x + y), enc_values)
        else:
            encoded_value = encode_double(value)
        res = res + encoded_value if res else encoded_value
    return res


def add_rpc_tags(*, src_path, dst_path, metadata_path):
    metadata = extract_rpc_metadata(metadata_path)
    tag_value = encode_rpc_tag(metadata)

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
            #dst.update_tags({'RPCCoefficientTag', tag_value})
            dst.write(src.read())
            dst.update_tags(ns='RPC', **tags)


def orthorectify(dem_path=None,
                 geoid_path=None,
                 *,
                 src_path,
                 dst_path,
                 metadata_path):
    base_cmd = """otbcli_OrthoRectification \
      -io.in \"{src}?&skipcarto=true\" \
      -io.out {dst} uint16 \
      -outputs.mode auto \
      -elev.geoid {geoid_path} \
      -elev.dem {dem_path}
    """
    metadata = extract_projection_metadata(metadata_path)

    if not geoid_path:
        geoid_path = GEOID_PATH
    if not dem_path:
        dem_path = DEM_PATH

    cmd = base_cmd.format(src=src_path,
                          dst=dst_path,
                          geoid_path=GEOID_PATH,
                          dem_path=dem_path,
                          **metadata)
    run_command(cmd)