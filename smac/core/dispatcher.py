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
Collection of classes and utilities to assure the whole AMQP connection
handling, including authentication, queue creation and so on.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

from thrift.protocol import TBinaryProtocol

from twisted.internet.defer import inlineCallbacks
from twisted.python import log

from txamqp import queue

from smac.amqp import RESPONSES

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
        
    @inlineCallbacks
    def set_up_exchanges(self, exchanges, kws):
        for e in exchanges:
            name = e['name'].format(**kws)
            log.msg("Declaring exchange '{0}'".format(name))
            yield self.channel.exchange_declare(exchange=name, type=e['type'])
            self.exchanges[e['id']] = name
    
    @inlineCallbacks
    def set_up_queues(self, queues, kws):
        for q in queues:
            name = q['name']
        
            if name:
                name = name.format(**kws)
            else:
                name = ''
                
            log.msg("Declaring queue '{0}'".format(name))
            queue = yield self.channel.queue_declare(queue=name, **q['extra'])
            
            self.queues.append(queue)
            
            for b in q['bindings']:
                e = self.exchanges[b[0]]
                rk = b[1].format(**kws)
                
                log.msg("--> Binding to '{0}' with routing key '{1}'".format(e, rk))
                
                yield self.channel.queue_bind(queue=queue.queue, exchange=e, routing_key=rk)
            
    @inlineCallbacks
    def set_up(self, channel, exchanges, queues, namespace, interface,
            implementation, instance_id):
        
        self.channel = channel
        
        kws = {
            'namespace': namespace,
            'interface': interface,
            'implementation': implementation,
            'instance_id': instance_id,
        }
        
        yield self.set_up_exchanges(exchanges, kws)
        yield self.set_up_queues(queues, kws)
    
    @inlineCallbacks
    def listen(self, client, processor):
        self.client = client
        
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        log.msg("Start listening")
        for queue in self.queues:
            r = yield self.channel.basic_consume(queue=queue.queue)
            q = yield self.client.queue(r.consumer_tag)
            d = q.get()
            d.addCallback(self.client.parseServerMessage, self.channel,
                    self.exchanges[RESPONSES], q, processor, pfactory, pfactory)
            d.addErrback(self.handle_closed_queue, queue)
        
    def handle_closed_queue(self, failure, _queue):
        # The queue is closed. Catch the exception and cleanup as needed.
        failure.trap(queue.Closed)
        
        log.msg("Queue '{0}' closed".format(_queue.queue))
        
        
        
        #####
        #def getResult(result):
        #    print result
        #
        #def doCommand(client):
        #    d = client.xxx_yyy()
        #    d.addCallback(getResult)
        #
        #def connected(result):
        #  result.started.addCallback(doCommand)
        #
        #d = ClientCreator(reactor, ThriftClientProtocol, Client, TBinaryProtocol.TBinaryProtocolFactory()).connectTCP(host, port)
        #d.addCallback(connected)
        #reactor.run()
        #####
        