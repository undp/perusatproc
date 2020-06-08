# -*- coding: utf-8 -*-

import logging
import os
import subprocess

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def run_command(cmd):
    _logger.info(cmd)
    subprocess.run(cmd, shell=True, check=True)


def run_otb_command(cmd):
    otb_dir = os.getenv("OTB_DIR")
    if otb_dir:
        otbenv_path = os.path.join(otb_dir, "bin", "otbenv")
        fullcmd = f"{otbenv_path} && {cmd}"
    else:
        fullcmd = cmd
    _logger.info(fullcmd)
    subprocess.run(fullcmd, shell=True, check=True)
