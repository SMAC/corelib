# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Collection of classes and utilities to assure the whole AMQP connection
handling, including authentication, queue creation and so on.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

from thrift.protocol import TBinaryProtocol

from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList
from twisted.python import log

from txamqp import queue

class Dispatcher(object):
    """
    
    """
    
    def __init__(self):
        """
        """
        self.channel = None
        self.client = None
        
        self.exchanges = {}
        self.queues = []
        self.exclusive_queue = None
        """The last found exclusive queue, used to add more bindings manually"""
    
    @inlineCallbacks
    def add_binding(self, exchange_id, routing_key):
        queue = yield self.channel.queue_declare(queue='', exclusive=True, auto_delete=True)
        exchange = self.exchanges[exchange_id]
        
        log.msg(("Adding binding for queue '{0}' to exchange '{1}' with " +
                "routing_key '{2}'").format(queue.queue, exchange, routing_key))
                
        c = yield self.channel.queue_bind(queue=queue.queue, exchange=exchange,
                routing_key=routing_key)
        
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        yield self.listen_queue(self.client, self.processor, pfactory, queue)
        
        returnValue(queue)
    
    @inlineCallbacks
    def remove_binding(self, queue):
        yield self.channel.queue_delete()
    
    def remove_queues(self):
        return DeferredList([self.channel.queue_delete(queue=q.queue) for q in self.queues])
    
    @inlineCallbacks
    def set_up_exchanges(self, exchanges, kws):
        for ex in exchanges.values():
            ex.format_name(**kws)
            if ex.name.split('.', 1)[0] != 'amq':
                log.msg("Declaring exchange '{0}'".format(ex.name))
                yield ex.declare(self.channel)
        self.exchanges = exchanges
    
    @inlineCallbacks
    def set_up_queues(self, queues, kws):
        for q in queues:
            name = q['name']
        
            if name:
                name = name.format(**kws)
            else:
                name = ''
                
            queue = yield self.channel.queue_declare(queue=name, **q['extra'])
            log.msg("Declared queue '{0}'".format(queue.queue))
            
            self.queues.append(queue)
            
            if 'exclusive' in q['extra'] and q['extra']['exclusive'] == True:
                self.exclusive_queue = queue
            
            for b in q['bindings']:
                e = self.exchanges[b[0]]
                rk = b[1].format(**kws)
                
                log.msg("Binding '{0}' to '{1}' with routing key '{2}'".format(queue.queue, e, rk))
                
                yield self.channel.queue_bind(queue=queue.queue, exchange=e.name, routing_key=rk)
            
    @inlineCallbacks
    def set_up(self, channel, exchanges, queues, **kws):
        self.channel = channel
        yield self.set_up_exchanges(exchanges, kws)
        yield self.set_up_queues(queues, kws)
    
    @inlineCallbacks
    def listen_queue(self, client, processor, pfactory, queue):
        r = yield self.channel.basic_consume(queue=queue.queue)
        q = yield self.client.queue(r.consumer_tag)
        d = q.get()
        d.addCallback(self.client.parseServerMessage, self.channel,
                self.exchanges['responses'].name, q, processor, pfactory, pfactory)
        d.addErrback(self.handle_closed_queue, queue)
        
    @inlineCallbacks
    def listen(self, client, processor):
        self.client = client
        self.processor = processor
        
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        log.msg("Start listening")
        for queue in self.queues:
            yield self.listen_queue(client, processor, pfactory, queue)
        
    def handle_closed_queue(self, failure, _queue):
        # The queue is closed. Catch the exception and cleanup as needed.
        failure.trap(queue.Closed)
        
        log.msg("Queue '{0}' closed".format(_queue.queue))
        