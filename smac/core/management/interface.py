# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
The interface which each new command has to implement in order to be used
from the command line shell.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

from zope.interface import Interface, Attribute, invariant

class ICommand(Interface):
    config = Attribute("""Command line syntax validator for this command""")
    
    def execute(*args):
        """Run this command with the given arguments"""
    