from twisted.internet import defer, reactor, protocol
from twisted.application import service
from txamqp.contrib.thrift.client import ThriftTwistedDelegate
from txamqp.spec import load as load_spec
from txamqp import client

from smac.amqp.protocol import ThriftAMQClient, SMACServerFactory, SMACClientFactory
from smac.modules.amqp import IAMQServiceHandler
from smac.python import log


class AMQService(service.MultiService, object):
    def __init__(self, specs, host='localhost', port=5672, vhost='/',
            user='guest', password='guest', channel=1):
        
        self.specs = load_spec(specs)
        self.delegate = ThriftTwistedDelegate()
        self.protocol = ThriftAMQClient
        self.vhost = vhost
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.channel = channel
        
        super(AMQService, self).__init__()
    
    @defer.inlineCallbacks
    def startService(self):
        log.info("Starting {0} service".format(self.name))
        
        c = protocol.ClientCreator(reactor, self.protocol, self.delegate,
                self.vhost, self.specs)
        self.client = yield c.connectTCP(self.host, self.port)
        
        log.debug("Connection OK")
        
        yield self.client.authenticate(self.user, self.password)
        
        log.debug("Authentication OK")
        
        channel = yield self.client.channel(self.channel)
        yield channel.channel_open()
        
        self.client_factory = SMACClientFactory(self.client, channel)
        self.server_factory = SMACServerFactory(self.client, channel)
        
        super(AMQService, self).startService()
    
    @defer.inlineCallbacks
    def stopService(self):
        """
        @todo: Should we tear down the AMQP connection here or is this method
               called as a consequence of it?
        """
        
        c = yield self.client.channel(0)
        
        try:
            yield c.connection_close()
        except client.Closed:
            #self.factory.closed = True
            pass
        
        yield super(AMQService, self).stopService()
    

class ThriftAMQService(service.Service, object):
    def __init__(self, processor, handler, address=None):
        super(ThriftAMQService, self).__init__()
        
        self.processor = processor
        self.handler = IAMQServiceHandler(handler)
        self.address = address or handler.address
        
        self.setName("{0} over AMQP".format(self.handler.address))
    
    @defer.inlineCallbacks
    def server(self, address, processor, handler, queues=None):
        server = yield self.parent.server_factory.build_server(self,
                processor, handler, address, queues)
        # @todo: Make a new IService instance and add it to the parent as a
        #        child of me.
        defer.returnValue(server)
    
    @defer.inlineCallbacks
    def startService(self):
        self.client = self.parent.client_factory.build_client
        
        yield self.server(self.address, self.processor, self.handler)
        super(ThriftAMQService, self).startService()
        
        log.info("ThriftAMQService started, notifying handler")
        self.handler.amq_start(self)
    
    @defer.inlineCallbacks
    def stopService(self):
        log.info("ThriftAMQService stopping, notifying handler")
        yield self.handler.amq_stop()
        log.info("ThriftAMQService handler shutdown process terminated, stopping service")
        super(ThriftAMQService, self).stopService()
    
    def processing_error(self, failure):
        log.error("An error occurred while processing a message!")
        log.error(failure)
    
    def queue_closed(self, failure):
        pass
    
    def queue_error(self, failure):
        log.error("Queue error!")
        log.error(failure)
        
        
    
