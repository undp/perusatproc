=========
Changelog
=========

Version 0.1.6
=============

- Rename OTB_ENV_PATH for OTB_PROFILE_PATH
- Fix OTB profile activation on Linux/OSX

Version 0.1.5
=============

- Store intermediate results on destination directory when using perusat_process.
- Delete temporary files if processes (and subprocesses) finish successfully.
- Upgrade default SRTM DEM files with 1-arc second (~30m GSD) instead of 90m.
  Also now they are stored with no compression for faster orthorectification
  processing.
- Add new --spacing argument for orthorectify and process console scripts to
  set resampling spacing size (by default uses 15m, which is half the GSD of
  the bundled SRTM DEM files).

Version 0.1.4
=============

- Bugfixes related to perusat_orthorectify CLI script.

Version 0.1.3
=============

- Applied nodata fill algorithm to SRTM DEM to avoid artifacts when
  orthorectifying.

Version 0.1.2
=============

- Support optional OTB_ENV_PATH environment variable, to load OTB environment
  only when running OTB CLI commands internally.
- Various bugfixes for making it work on Windows.

Version 0.1.0
=============

- Basic processing scripts for calibration, orthorectification and
  pansharpening.
