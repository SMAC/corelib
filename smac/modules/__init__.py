from smac.amqp.routing import IAddress
from smac.amqp import factory
from smac import amqp
from smac.core.dispatcher import Dispatcher
from smac.util.proxy import ProxyDeferred
from smac.modules import utils
from smac.conf import settings
from smac.conf.topology import queue, exchange
from twisted.internet import defer
from zope.interface import providedBy

class RemoteService(object):
    """
    A remote module which holds a client attribute (for service calls) and the
    actual address of the remote object.
    
    The client attribute is lazily created on the first request and uses a
    C{ProxyDeferred} to be always useable without to wait for the callback to
    fire. Refer to the C{ProxyDeferred} documentation for more information.
    """
    
    def __init__(self, address, distribution='unicast', client_class=None):
        self.address = IAddress(address)
        self.distribution = distribution
        self.client_class = client_class
    
    @property
    def client(self):
        d = factory.client_factory.build_client(self.address, self.distribution, self.client_class)
        self._client = ProxyDeferred(d)
        self._client.addCallback(lambda c: setattr(self, '_client', c) or c)
        
        return self._client
    
    def __str__(self):
        return str(self.address)
    
    def __repr__(self):
        return '<%s remote object at %d>' % (self.address, id(self))
    

class LocalService(object):
    
    queues = (
        queue('', (('services', '{routing_key}'),), extra={
            'exclusive': True,
            'auto_delete': True
        }),
    )
    
    def __init__(self, address, processor=None):
        self.address = IAddress(address)
        
        if processor is None:
            interface = list(providedBy(self))[0]
            processor = utils.get_processor_for_interface(interface)
        
        self.processor = processor(self)
        self.dispatcher = Dispatcher()
    
    @defer.inlineCallbacks
    def setup(self):
        self.channel = yield amqp.client.channel(settings.amqp.channel)
        yield self.dispatcher.set_up(
            self.channel, exchanges, self.queues,
            namespace=self.address.namespace,
            routing_key=self.address.routing_key()
        )
        yield self.dispatcher.listen(amqp.client, self.processor)
    
    def unbind(self):
        return self.dispatcher.remove_queues()

