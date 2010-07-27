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
AMQP client factory to create amqp based twisted services.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

## Twisted libraries
#from twisted.internet.protocol import ClientFactory
#from twisted.internet.defer import inlineCallbacks, succeed
#from twisted.internet.error import ConnectionDone, ReactorNotRunning
#from twisted.internet import reactor
#from twisted.python import log
#
## txAMQP libraries
#from txamqp.contrib.thrift.protocol import ThriftAMQClient
#from txamqp.contrib.thrift.client import ThriftTwistedDelegate
#from txamqp.spec import load as load_spec
#from txamqp import client
#
## Thrift libraries
#from thrift.protocol import TBinaryProtocol
#
#
#from smac.conf.topology import exchanges, queues
#from smac.core.dispatcher import Dispatcher
#
#PKG_CLS_SEPARATION = '-'
#
#client_factory = None
#
#class AMQServerFactory(ClientFactory):
#    
#    protocol = ThriftAMQClient
##    
##    def __init__(self, processor, spec, vhost, channel, user, password, *args,
##            **kwargs):
##        self.vhost = vhost
##        self.spec = load_spec(spec)
##        self.processor = processor
##        self.handler = self.processor._handler
##        self.channel = channel
##        self.username = user
##        self.password = password
##        self._closed = True
##    
##    def buildProtocol(self, addr):
##        delegate = ThriftTwistedDelegate()
##        self.client = self.protocol(delegate=delegate, vhost=self.vhost,
##                spec=self.spec)
##        
##        self._closed = False
##        log.msg("Connection to the AMQP broker OK.")
##        
##        reactor.addSystemEventTrigger('before', 'shutdown',
##                self._closeConnection)
##        
##        self.client.authenticate(self.username, self.password).addCallbacks(
##                self._setupAMQP, self._authError)
##        
##        return self.client
##    
##    def clientConnectionFailed(self, connector, reason):
##        log.msg("Connection to the AMQP broker failed.")
##        log.msg(reason.getErrorMessage())
##        
##        if reactor.running:
##            reactor.stop()
##    
##    def startedConnecting(self, connector):
##        log.msg("Trying to connect to the AMQP broker...")
##    
##    def clientConnectionLost(self, connector, reason):
##        if reason.type is ConnectionDone and self._closed:
##            # Connection was closed cleanly
##            return
##        
##        log.msg("Connection to the AMQP broker lost.")
##        log.msg(reason.getErrorMessage())
##        
##        #log.err(reason)
##        
##        try:
##            reactor.stop()
##        except ReactorNotRunning:
##            pass
##    
##    def startFactory(self):
##        self.handler.pre_startup()
##        
##    def stopFactory(self):
##        pass
##    
##    @inlineCallbacks
##    def _closeConnection(self):
##        yield self.handler.teardown()
##        
##        c = yield self.client.channel(0)
##        
##        try:
##            yield c.connection_close()
##        except client.Closed:
##            self._closed = True
##            log.msg("Connection to the AMQP broker closed.")
##    
##    def _authError(self, failure):
##        log.msg("Autentication failure (user: %s)" % self.username)
#    
#    @inlineCallbacks
#    def _setupAMQP(self, _):
#        log.msg("Logged in, setting global available client")
#        
#        from smac import amqp
#        amqp.client = self.client
#        
#        channel = yield self.client.channel(self.channel)
#        log.msg("Got channel number %d" % self.channel)
#        try:
#            yield channel.channel_open()
#        except:
#            pass
#        log.msg("Opened channel number %d" % self.channel)
#        
#        global client_factory
#        
#        self.handler.client_factory = client_factory = AMQClientFactory(self.client, self.channel)
#        
#        self.dispatcher = Dispatcher()
#        
#        yield self.dispatcher.set_up(channel, exchanges, queues, **{
#            'namespace': self.handler.namespace,
#            'interface': self.handler.interface,
#            'implementation': self.handler.implementation,
#            'instance_id': self.handler.id,
#        })
#        yield self.dispatcher.listen(self.client, self.processor)
#        
#        self.handler.dispatcher = self.dispatcher
#        
#        self.handler.post_startup()
#    
##class AMQClientFactory(object):
##    def __init__(self, amqp_client, amqp_channel):
##        self.amqp_client = amqp_client
##        self.channel = amqp_channel
##        
##        # @TODO: Find some neat way to do this, the queues have to be closed when the 
##        # client isn't used anymore!
##        self.clients = {}
##    
##    def build_client(self, address, distribution=None, client_class=None):
##        distribution = address.distribution() or distribution
##        
##        if distribution is None:
##            raise ValueError('The message distribution mode was not ' +
##                    'specified and could not be inferred from the address.')
##        
##        client_class = self._thrift_client(address, client_class)
##        
##        key = (address.routing_key(), distribution, client_class)
##        
##        if key in self.clients:
##            log.msg("Using cached client for %s with %s distribution" % (
##                address.routing_key(), distribution))
##            return succeed(self.clients[key])
##        
##        serv_ex = self._exchange_name(address, distribution)
##        resp_ex = self._exchange_name(address, 'responses')
##        
##        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
##        
##        client = self.amqp_client.createThriftClient(resp_ex, serv_ex,
##                    address.routing_key(), client_class, self.channel,
##                    iprot_factory=pfactory, oprot_factory=pfactory)
##        
##        client.addCallback(self._register_client, key)
##        
##        return client
##    
##    def _register_client(self, client, key):
##        def handleClientQueueError(self, failure):
##            log.err("CLIENT QUEUE ERROR")
##        
##        def handleClosedClientQueue(self, failure):
##            log.err("CLOSED CLIENT QUEUE")
##        
##        self.clients[key] = client
##        
##        client.handleClientQueueError = handleClientQueueError
##        client.handleClosedClientQueue = handleClosedClientQueue
##        
##        return client
##    
##    def _thrift_client(self, address, client_class=None):
##        if client_class:
##            if isinstance(client_class, basestring):
##                module = client_class
##            else:
##                return client_class
##        else:
##            try:
##                module = "smac.api.{0}.{1}".format(address.interface.lower(), address.interface.capitalize())
##            except AttributeError:
##                module = "smac.api.base.Module"
##            
##        imported = __import__(module, fromlist=['Client',], level=0)
##        client = getattr(imported, 'Client')
##        
##        return client
##    
##    def _exchange_name(self, address, distribution):
##        try:
##            e = exchanges[distribution]
##            return e.name.format(**address._asdict())
##        except KeyError:
##            raise ValueError(
##                    'Invalid message distribution mode: {0}'.format(distribution))
##
##