# Copyright (C) 2005-2009  MISG/ICTI/EIA-FR
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Collection of utilities to manage the SMAC system.
This module contains the base command line interface and all commands
implementations

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

from interface import ICommand
from twisted.python import usage
import inspect

class BaseOptions(usage.Options):
    def getSynopsis(self):
        spec = inspect.getargspec(self.parseArgs)
        
        r = ""
        for i, arg in enumerate(spec.args[1:], 2):
            if spec.defaults and len(spec.args) - i < len(spec.defaults):
                r += " [{0}]".format(arg)
            else:
                r += " {0}".format(arg)
        
        if spec.varargs:
            r += " [...]"
        
        return super(BaseOptions, self).getSynopsis() + r

__all__ = ['ICommand','BaseOptions']