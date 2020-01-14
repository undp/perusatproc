# -*- coding: utf-8 -*-

import xmltodict
import logging
from datetime import datetime

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)

RPC_COEFF_PAIRS = [
    ('samp_num_coeffs', 'COL_NUM_COEFF'),
    ('samp_den_coeffs', 'COL_DEN_COEFF'),
    ('line_num_coeffs', 'ROW_NUM_COEFF'),
    ('line_den_coeffs', 'ROW_DEN_COEFF'),
]


def extract_calibration_metadata(metadata_path):
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
    if not isinstance(band_radiances, list):
        band_radiances = [band_radiances]
    gains = [float(r['GAIN']) for r in band_radiances]
    biases = [float(r['BIAS']) for r in band_radiances]

    # Solar irradiance values for each band
    band_solar_irradiances = band_spectral_range['Band_Solar_Irradiance']
    if not isinstance(band_solar_irradiances, list):
        band_solar_irradiances = [band_solar_irradiances]
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


def extract_projection_metadata(metadata_path):
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


def extract_rpc_metadata(metadata_path):
    with open(metadata_path) as f:
        body = xmltodict.parse(f.read())

    doc = body['Rpc_Document']

    inverse_model = doc['Inverse_Model']
    err_bias = -1.0  # unknown?
    err_rand = -1.0  # unknown?

    coeffs = dict()
    for key, xml_key in RPC_COEFF_PAIRS:
        coeffs[key] = [
            float(inverse_model['{}_{}'.format(xml_key, v)])
            for v in range(1, 21)
        ]

    validity = doc['Validity']
    lon_scale = float(validity['LON_SCALE'])
    lon_offset = float(validity['LON_OFF'])
    lat_scale = float(validity['LAT_SCALE'])
    lat_offset = float(validity['LAT_OFF'])
    height_scale = float(validity['HEIGHT_SCALE'])
    height_offset = float(validity['HEIGHT_OFF'])
    samp_scale = float(validity['COL_SCALE'])
    samp_offset = float(validity['COL_OFF'])
    line_scale = float(validity['ROW_SCALE'])
    line_offset = float(validity['ROW_OFF'])

    return dict(err_bias=err_bias,
                err_rand=err_rand,
                lon_scale=lon_scale,
                lon_offset=lon_offset,
                lat_scale=lat_scale,
                lat_offset=lat_offset,
                height_scale=height_scale,
                height_offset=height_offset,
                samp_scale=samp_scale,
                samp_offset=samp_offset,
                line_scale=line_scale,
                line_offset=line_offset,
                **coeffs)
