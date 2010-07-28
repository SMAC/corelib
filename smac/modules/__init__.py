# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
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
Interfaces and base classes to extend to implement an generic SMAC module.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2010 MISG/ICTI/EIA-FR
@license: GPLv3
"""


from zope.interface import implements, Attribute, Interface, providedBy

from smac.python import log
from smac.modules import utils


class IModule(Interface):
    """
    Most basic interface to be implemented by a module to be recognized as
    such and to be adressable in a mixed environment.
    """
    
    interface = Attribute("""Interface implemented by this module""")
    
    implementation = Attribute("""Implementation of this module""")
    
    id = Attribute("""Instance ID of this module""")


class Module(object):
    """
    A generic module on connected to a SMAC system through various interfaces
    such as AMQP or RPC.
    """
    
    implements(IModule)
    
    def __init__(self, id, implementation=None, interface=None):
        """
        Creates a new service handler for a generic module.
        
        @param id: The instance ID of this module on the system.
        @param implementation: The interface specific implementation of this
                               module. If the value is not provided, the class
                               name will be used as default.
        @param interface: The interface of this module. If the value is not
                          provided, the module name of the last implemented
                          interface is used.
        """
        self.id = id
        
        if not implementation:
            implementation = utils.get_implementation_from_instance(self)
            log.debug("Implementation guessed to be '{0}'".format(implementation))
        self.implementation = implementation
        
        if not interface:
            self.interface = utils.get_interface_from_instance(self)
            log.debug("Interface guessed to be '{0}'".format(interface))
        self.interface = interface
    
    def ping(self):
        """
        The ping service method does not have to do any processing as it only
        acts as a flag to mark this module as online.
        """
    
    def announce(self, info):
        """
        Each method implements this method since each component is intended to
        be able to announce itself to any other, but only specific module
        implementations (such as controllers) react upon it.
        """
    


    