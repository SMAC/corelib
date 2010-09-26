# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Factories for AMQ clients, Thrift clients and SMAC Clients and servers.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


import weakref

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import defer, error
from txamqp.protocol import AMQClient
from txamqp.contrib.thrift.client import ThriftTwistedDelegate
from txamqp.queue import TimeoutDeferredQueue, Closed
from txamqp.contrib.thrift.transport import TwistedAMQPTransport
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from smac.python import log
from smac.amqp.models import Exchange, Queue, IAddress
from smac.conf import topology
from smac.modules import utils


class SMACServerFactory(object):
    
    iprot_factory = TBinaryProtocol.TBinaryProtocolFactory()
    oprot_factory = TBinaryProtocol.TBinaryProtocolFactory()
    
    def __init__(self, client, channel=None):
        self.client = client
        self.channel = channel or 1
        
        if client.check_0_8():
            self.reply_to = "reply to"
        else:
            self.reply_to = "reply-to"
    
    @defer.inlineCallbacks
    def build_server(self, delegate, processor, handler, address, queues=None, standalone=True):
        processor_name = processor.__name__
        
        log.debug("Creating new server for {0} with ID {1}".format(
                processor_name, address.instance))
        
        address = IAddress(address)
        
        if not queues:
            queues = topology.queues
        
        if isinstance(self.channel, int):
            channel = yield self.client.channel(self.channel)
            yield channel.channel_open()
        else:
            # Assume it's already open!
            channel = self.channel
        
        deferreds = []
        
        # Declare all exchanges
        exchanges = {}
        for k, e in topology.exchanges.iteritems():
            e = Exchange(channel, **e)
            e.format_name(**dict(address))
            e.declare()
            exchanges[k] = e
        
        self.responses = Exchange(channel, **topology.exchanges['responses'])
        
        # Declare all queues
        qs = []
        for q in queues:
            q = q.copy()
            bindings = q.pop('bindings')
            q = Queue(channel, **q)
            q.format_name(**dict(address))
            q.declare()
            deferreds += [q.bind(exchanges[e], k.format(**dict(address))) for e, k in bindings]
            qs.append(q)
        
        # Wait for declarations and bindings
        yield defer.DeferredList(deferreds)
        
        log.debug("All queues and needed exchanges declared and bound, start listening")
        
        tags = []
        
        for queue in qs:
            tag = yield queue.consume()
            tags.append(tag)
        
        @defer.inlineCallbacks
        def destroy(ref):
            log.debug("Server for {0} garbage collected, removing " \
                    "subscriptions".format(processor_name))
            try:
                yield defer.DeferredList([channel.basic_cancel(t) for t in tags])
            except Exception as e:
                pass
        
        if not standalone:
            handler = weakref.proxy(handler, destroy)
        
        processor = processor.Processor(handler)
        
        for tag in tags:
            queue = yield self.client.queue(tag)
            self.get_next_message(channel, queue, processor, delegate)
        
    
    def parse_message(self, msg, channel, queue, processor, delegate):
        tag = msg.delivery_tag
        
        try:
            sender = msg.content[self.reply_to]
        except KeyError:
            sender = None
        
        transport_in = TTransport.TMemoryBuffer(msg.content.body)
        transport_out = TwistedAMQPTransport(channel, str(self.responses), sender)
        
        iprot = self.iprot_factory.getProtocol(transport_in)
        oprot = self.oprot_factory.getProtocol(transport_out)
        
        d = processor.process(iprot, oprot)
        d.addErrback(delegate.processing_error)
        
        channel.basic_ack(tag, True)
        
        self.get_next_message(channel, queue, processor, delegate)
    
    def get_next_message(self, channel, queue, processor, delegate):
        d = queue.get()
        d.addCallback(self.parse_message, channel, queue, processor, delegate)
        d.addErrback(self.catch_closed_queue, delegate)
        d.addErrback(delegate.queue_error)
    
    def catch_closed_queue(self, failure, delegate):
        failure.trap(Closed)
        delegate.queue_closed(failure)
    


class SMACClientFactory(object):
    
    iprot_factory = TBinaryProtocol.TBinaryProtocolFactory()
    oprot_factory = TBinaryProtocol.TBinaryProtocolFactory()
    
    def __init__(self, client, channel=None):
        self.client = client
        self.client_lock = defer.DeferredLock()
        self.clients = {}
        
        if client.check_0_8():
            self.reply_to = "reply to"
        else:
            self.reply_to = "reply-to"
        
        self.channel = channel or 1
    
    @defer.inlineCallbacks
    def build_client(self, address, service=None, distribution=None, cache=True):
        yield self.client_lock.acquire()
        try:
            address = IAddress(address)
            
            if not service:
                service = utils.get_module_from_address(address)
            
            service_name = service.__name__ + address.routing_key
            distribution = distribution or address.distribution
            
            if not distribution:
                raise ValueError("The distribution mode was not defined and " \
                        "could not be inferred from the address.")
            
            key = (service, address.routing_key, distribution)
            
            try:
                client = self.clients[key]
            except KeyError:
                log.debug("Creating new client for {0} with routing key {1} and distribution {2}".format(
                        service.__name__, address.routing_key, distribution))
                
                if isinstance(self.channel, int):
                    channel = yield self.client.channel(self.channel)
                    yield channel.channel_open()
                else:
                    # Assume it's already open!
                    channel = self.channel
                
                response_exchange = Exchange(channel, **topology.exchanges['responses'])
                response_queue = Queue(channel, exclusive=True, auto_delete=True)
                
                yield response_queue.declare()
                yield response_queue.bind(response_exchange)
                consumer_tag = yield response_queue.consume()
                
                service_exchange = Exchange(channel, **topology.exchanges[distribution])
                service_exchange.format_name(**dict(address))
                yield service_exchange.declare()
                
                amqp_transport = TwistedAMQPTransport(channel, str(service_exchange),
                        address.routing_key, service_name,
                        str(response_queue), self.reply_to)
                
                client = service.Client(amqp_transport, self.oprot_factory)
                client.address = address
                client.factory = self
                
                if cache:
                    weak_client = client
                    self.clients[key] = client
                else:
                    @defer.inlineCallbacks
                    def destroy(ref):
                        log.debug("Client for {0} garbage collected, removing " \
                                "subscriptions".format(service_name))
                        try:
                            yield channel.basic_cancel(consumer_tag)
                        except Exception as e:
                            pass
                    
                    weak_client = weakref.proxy(client, destroy)
                
                queue = yield self.client.queue(consumer_tag)
                self.get_next_message(channel, queue, weak_client)
                
                queue = yield self.client.get_return_queue(service_name)
                self.get_next_unroutable_message(channel, queue, weak_client)
            else:
                log.debug("Using cached client for {0} with routing key {1} and distribution {2}".format(
                        service.__name__, address.routing_key, distribution))
        finally:
            self.client_lock.release()
        
        defer.returnValue(client)
    
    def parse_message(self, msg, channel, queue, client):
        tag = msg.delivery_tag
        
        transport = TTransport.TMemoryBuffer(msg.content.body)
        iprot = self.iprot_factory.getProtocol(transport)
        
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        
        if rseqid not in client._reqs:
            log.warn('Missing rseqid! fname = %r, rseqid = %s, mtype = %r, routing key = %r, client = %r, msg.content.body = %r' % (fname, rseqid, mtype, msg.routing_key, client, msg.content.body))
            
        method = getattr(client, 'recv_' + fname)
        method(iprot, mtype, rseqid)
        channel.basic_ack(tag, True)
        
        self.get_next_message(channel, queue, client)
    
    def unrouteable_message(self, msg, channel, queue, client):
        transport = TTransport.TMemoryBuffer(msg.content.body)
        iprot = self.iprot_factory.getProtocol(transport)
        
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        
        try:
            d = client._reqs.pop(rseqid)
        except KeyError:
            # KeyError will occur if the remote Thrift method is oneway,
            # since there is no outstanding local request deferred for
            # oneway calls.
            pass
        else:
            type = TTransport.TTransportException.NOT_OPEN,
            msg = 'Unrouteable message, routing key = %r calling function %r' % (msg.routing_key, fname)
            d.errback(TTransport.TTransportException(type, msg))
        
        self.get_next_unroutable_message(channel, queue, client)
    
    def get_next_unroutable_message(self, channel, queue, client):
        d = queue.get()
        d.addCallback(self.unrouteable_message, channel, queue, client)
        d.addErrback(self.catch_closed_queue)
        d.addErrback(self.handle_queue_error)
    
    def get_next_message(self, channel, queue, client):
        d = queue.get()
        d.addCallback(self.parse_message, channel, queue, client)
        d.addErrback(self.catch_closed_queue)
        d.addErrback(self.handle_queue_error)
    
    def catch_closed_queue(self, failure):
        failure.trap(Closed)
        self.handle_closed_queue(failure)
    
    def handle_queue_error(self, failure):
        log.err("Error in queue")
        log.err(failure)
        pass
    
    def handle_closed_queue(self, failure):
        log.debug("Queue closed")
    


class ThriftAMQClient(AMQClient, object):
    def __init__(self, *args, **kwargs):
        super(ThriftAMQClient, self).__init__(*args, **kwargs)
        
        self.return_queues_lock = defer.DeferredLock()
        self.return_queues = {}
    
    @defer.inlineCallbacks
    def get_return_queue(self, key):
        yield self.return_queues_lock.acquire()
        try:
            try:
                q = self.return_queues[key]
            except KeyError:
                q = TimeoutDeferredQueue()
                self.return_queues[key] = q
        finally:
            self.return_queues_lock.release()
        defer.returnValue(q)
    thriftBasicReturnQueue = get_return_queue # compatibility with
                                              # ThriftTwistedDelegate


class AMQClientFactory(ReconnectingClientFactory, object):
    """
    Factory for AMQP connections intended to be used by thrift clients.
    Overriding the C{protocol} property with a more general C{AMQClient} class
    should allow a more generic use of the factory.
    """
    
    protocol = ThriftAMQClient
    
    def __init__(self, spec, vhost):
        self.spec = spec
        self.vhost = vhost
        self.closed = False
        
    def buildProtocol(self, _):
        client = self.protocol(ThriftTwistedDelegate(), self.vhost, self.spec)
        client.factory = self
        
        return client
        
    def clientConnectionLost(self, connector, reason):
        if self.closed:
            log.info("Connection to the AMQP broker closed.")
            return
        
        log.error('Connection to AMQP broker lost. Reason {0}'.format(reason))
        super(AMQClientFactory, self).clientConnectionLost(connector, reason)
        
    def clientConnectionFailed(self, connector, reason):
        log.error('Connection to AMQP broker failed. Reason {0}'.format(reason))
        super(AMQClientFactory, self).clientConnectionFailed(connector, reason)
    

