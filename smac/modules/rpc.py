# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Interfaces and base classes to extend to implement an RPC based service
handler.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from zope.interface import Attribute, Interface, implements
from twisted.internet import task, defer

from smac.conf import settings
from smac.modules import Module


class IRPCServiceHandler(Interface):
    """
    Service handlers which implement this interface are supposed to be able
    to receive thrift requests over an RPC connection.
    """
    
    def rpc_start(service):
        """
        Called by the L{ThriftRPCService} once the underlying communication
        infrastructure is in place and the handler can begin to receive thrift
        requests over RPC.
        
        @param service: The C{ThriftRPCService} instance responsible for the
                        RPC messaging.
        """
    
    def rpc_stop():
        """
        Called by the L{ThriftRPCService} just before the underlying RPC
        communication channel will be closed.
        
        This method can return a deferred and the C{ThriftRPCService} instance
        will try to wait for it to complete before proceding with the
        teardown procedure.
        """
    


class RPCModule(Module):
    """
    Basic implementation of the L{IRPCServiceHandler} interface.
    """
    
    implements(IRPCServiceHandler)
    
    def rpc_start(self, service):
        pass
    
    def rpc_stop(self):
        pass
    

