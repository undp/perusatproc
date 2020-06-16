===========
perusatproc
===========

Process PeruSat-1 primary scenes into calibrated, orthorectified and
pansharpened images.

Description
===========

This package allows you to process PeruSat-1 primary scenes. You can perform
the following processing steps:

- Radiometric calibration (top-of-atmosphere)
- Orthorectification
- Pansharpening

It depends on Orfeo Toolbox and some Python packages:

- rasterio
- xmltodict

Modes
=====

Scripts
-------

`perusat_calibrate`: Calibrates image to top-of-atmosphere (ToA).

`perusat_orthorectify`: Adds projection and RPC tags to an image from its
metadata files, and then orthorectifies it using the RPC data and a DEM image.
If no DEM is provided, a DEM from SRTM is used (1-arc second / 30m aprox GSD).

`perusat_pansharpen`: Bundles a pancromatic (P) and multispectral (MS) image to
form a pansharpened image.

`perusat_process`: Given a path to a PeruSat-1 product, it peforms all required
steps to form a single calibrated, orthorectified and pansharpened image. Final
output can be a virtual raster or a tiff file.


Note
====

This project has been set up using PyScaffold 4.0a1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
