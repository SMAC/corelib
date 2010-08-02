# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Collection of utilities to manage the SMAC system.
This module contains the base command line interface and all commands
implementations

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
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