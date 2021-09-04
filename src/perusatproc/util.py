# -*- coding: utf-8 -*-

import logging
import os
import subprocess
import sys

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def run_command(cmd):
    _logger.info(cmd)
    subprocess.run(cmd, shell=True, check=True)


def run_otb_command(cmd, cwd=None):
    _logger.info("Run command: %s", cmd)
    otb_profile_path = os.getenv("OTB_PROFILE_PATH")
    if otb_profile_path:
        _logger.info("Use OTB profile environment at %s", otb_profile_path)
        if sys.platform == "win32":
            cmd = f"{otb_profile_path} && {cmd}"
        else:
            # On Linux/OSX, profile path must be sourced, not executed
            cmd = f"/bin/bash -c 'source {otb_profile_path}; {cmd}'"
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)
