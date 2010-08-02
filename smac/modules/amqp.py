# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Interfaces and base classes to extend to implement an AMQP based service
handler.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from zope.interface import Attribute, Interface, implements
from twisted.internet import task, defer

from smac.amqp import models
from smac.conf import settings
from smac.modules import Module


class IAMQServiceHandler(Interface):
    """
    Service handlers which implement this interface are supposed to be able
    to receive and send thrift requests over an AMQP connection.
    """
    
    address = Attribute("""An Address object identifying the module""")
    
    def amq_start(service):
        """
        Called by the L{ThriftAMQService} once the underlying communication
        infrastructure is in place and the handler can begin to send and
        receive thrift requests over AMQ.
        
        @param service: The C{ThriftAMQService} instance responsible for the
                        AMQP messaging.
        """
    
    def amq_stop():
        """
        Called by the L{ThriftAMQService} just before the underlying amqp
        communication channel will be closed.
        
        This method can return a deferred and the C{ThriftAMQService} instance
        will try to wait for it to complete before proceding with the
        teardown procedure.
        """
    


class AMQModule(Module):
    """
    Basic implementation of the L{IAMQServiceHandler} interface.
    """
    
    implements(IAMQServiceHandler)
    
    @property
    def address(self):
        if not hasattr(self, '_address'):
            self._address = models.Address(self.interface, self.implementation, self.id)
        return self._address
    
    @defer.inlineCallbacks
    def amq_start(self, service):
        self.amq_client = service.client
        self.amq_server = service.server
        self.amq_service = service
        
        target = models.Address('Controller')
        client = yield service.client(target, distribution='broadcast')
        call = task.LoopingCall(client.announce, str(self.address))
        call.start(settings.ping_interval)
    
    def amq_stop(self):
        pass
    

