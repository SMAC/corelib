# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Interfaces and base classes to extend to implement an generic SMAC module.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


import socket

from twisted.internet import defer, reactor
from zope.interface import implements, Attribute, Interface, providedBy

from smac.api.ttypes import GeneralModuleInfo
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
    
    def __init__(self, id, implementation=None, interface=None, *args, **kwargs):
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
            interface = utils.get_interface_from_instance(self)
            log.debug("Interface guessed to be '{0}'".format(interface))
        self.interface = interface
        
        super(Module, self).__init__(*args, **kwargs)
    
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
    
    @defer.inlineCallbacks
    def info(self):
        if not hasattr(self, '_info'):
            hostname = socket.getfqdn()
            """@warning: C{socket.getfqdn} may block"""
            
            address = self.address.to_moduleaddress()
            ip_address = yield reactor.resolve(socket.gethostname())
            
            self._info = GeneralModuleInfo(address, ip_address, hostname)
        
        defer.returnValue(self._info)
    


    