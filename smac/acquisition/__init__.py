# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Acquisition setup and session management objects.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

from smac.acquisition.setup import AcquisitionSetup
from smac.acquisition.session import AcquisitionSession
from smac.acquisition.register import SessionRegister

__all__ = ('AcquisitionSetup', 'AcquisitionSession', 'SessionRegister', 'errors')