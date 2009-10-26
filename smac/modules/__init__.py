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
Various utility functions to work with the SMAC modules.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

import inspect

def get_class_instance(klass, module=None):
    """
    Returns the first found instance of C{klass} from the module C{module}
    or in the C{implementation} module if no module is passed as argument.
    
    @param klass: The class to search an instance for
    @type  klass: A C{class}
    
    @param module: The module containing the searched instance
    @type  module: A C{module}
    """
    
    if not module:
        import implementation as module
    
    try:
        return inspect.getmembers(module, lambda v: isinstance(v, klass))[0][1]
    except IndexError:
        return None

def get_processor_for_interface(interface):
    """
    Returns the thrift processor class for the given interface. This allows to
    retrieve the Processor of a defined handler on runtime by introspecting
    his interface.
    
    @param interface: The interface for which to retrieve the C{Processor}
    @type  interface: A L{zope.interface.Interface} class
    """
    
    module = __import__(interface.__module__, fromlist=['Processor'], level=0)
    
    return getattr(module, 'Processor', None)
    
    