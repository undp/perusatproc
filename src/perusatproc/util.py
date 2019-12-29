# -*- coding: utf-8 -*-

import logging
import subprocess

__author__ = "Damián Silvani"
__copyright__ = "Dymaxion Labs"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def run_command(cmd):
    _logger.info(cmd)
    subprocess.run(cmd, shell=True, check=True)
