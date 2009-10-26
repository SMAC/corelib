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

# Twisted libraries
from twisted.internet.protocol import ClientFactory
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.error import ConnectionDone
from twisted.internet import reactor
from twisted.python import log

# txAMQP libraries
from txamqp.contrib.thrift.protocol import ThriftAMQClient
from txamqp.client import TwistedDelegate
from txamqp.spec import load as load_spec
from txamqp import client

# Thrift libraries
from thrift.protocol import TBinaryProtocol

from smac.conf.topology import EXCHANGES, QUEUES
from smac.core.dispatcher import Dispatcher
from smac.amqp import UNICAST, BROADCAST, RESPONSES, SERVICES

PKG_CLS_SEPARATION = '-'
CHANNEL = 1

class AMQServerFactory(ClientFactory):
    
    protocol = ThriftAMQClient
    
    def __init__(self, processor, spec, vhost, user, password, *args,
            **kwargs):
        self.vhost = vhost
        self.spec = load_spec(spec)
        self.processor = processor
        self.handler = self.processor._handler
        self.username = user
        self.password = password
        self._closed = True
    
    def buildProtocol(self, addr):
        delegate = TwistedDelegate()
        self.client = self.protocol(delegate=delegate, vhost=self.vhost,
                spec=self.spec)
        
        self._closed = False
        log.msg("Connection to the AMQP broker OK.")
        
        reactor.addSystemEventTrigger('before', 'shutdown',
                self._closeConnection)
        
        self.client.authenticate(self.username, self.password).addCallbacks(
                self._setupAMQP, self._authError)
        
        return self.client
    
    def clientConnectionFailed(self, connector, reason):
        log.msg("Connection to the AMQP broker failed.")
        log.msg(reason.getErrorMessage())
        
        #log.err(reason)
        
        if reactor.running:
            reactor.stop()
    
    def startedConnecting(self, connector):
        log.msg("Trying to connect to the AMQP broker...")
    
    def clientConnectionLost(self, connector, reason):
        if reason.type is ConnectionDone and self._closed:
            # Connection was closed cleanly
            return
        
        log.msg("Connection to the AMQP broker lost.")
        log.msg(reason.getErrorMessage())
        
        #log.err(reason)
        
        if reactor.running:
            reactor.stop()
    
    def startFactory(self):
        self.handler._pre_startup()
        
    def stopFactory(self):
        pass
    
    @inlineCallbacks
    def _closeConnection(self):
        self.handler._tear_down()
        
        c = yield self.client.channel(0)
        
        try:
            yield c.connection_close()
        except client.Closed as e:
            self._closed = True
            log.msg("Connection to the AMQP broker closed.")
    
    def _authError(self, failure):
        log.msg("Autentication failure (user: %s)" % self.username)
    
    @inlineCallbacks
    def _setupAMQP(self, _):
        log.msg("Logged in")
        
        channel = yield self.client.channel(CHANNEL)
        log.msg("Got channel number %d" % CHANNEL)
        
        yield channel.channel_open()
        log.msg("Opened channel number %d" % CHANNEL)
        
        # Set the channel attribute of the thrift handler instance to allow
        # the reuse of the amq connection for additional tasks
        self.handler.set_channel(channel)
        
        self.handler.set_client_factory(AMQClientFactory(self.client))
        
        self.dispatcher = Dispatcher()
        
        yield self.dispatcher.set_up(channel, EXCHANGES, QUEUES,
                self.handler.namespace, self.handler.interface,
                self.handler.implementation, self.handler.id)
        yield self.dispatcher.listen(self.client, self.processor)
        
        self.handler._post_startup()
    
class AMQClientFactory(object):
    def __init__(self, amqp_client):
        self.amqp_client = amqp_client
    
    def build_client(self, address, distribution=None):
        if address.is_domain():
            distribution = BROADCAST
        
        if address.is_instance():
            distribution = UNICAST
        
        if address.is_service():
            distribution = SERVICES
        
        if distribution is None:
            raise ValueError('The message distribution mode was not ' +
                    'specified and could not be inferred from the address.')
        
        serv_ex = self._exchange_name(address, distribution)
        resp_ex = self._exchange_name(address, RESPONSES)
        
        thrift_client = self._thrift_client(address)
        
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        return self.amqp_client.createThriftClient(resp_ex, serv_ex,
                address.routing_key(), thrift_client, CHANNEL,
                iprot_factory=pfactory, oprot_factory=pfactory)
    
    def _thrift_client(self, address):
        try:
            module = "smac.api.{0}.{1}".format(address.interface.lower(), address.interface.capitalize())
        except AttributeError:
            module = "smac.api.base.Module"
            
        imported = __import__(module, fromlist=['Client',], level=0)
        client = getattr(imported, 'Client')
        
        return client
    
    def _exchange_name(self, address, distribution):
        for e in EXCHANGES:
            if e['id'] == distribution:
                return e['name'].format(**address._asdict())
                
        raise ValueError(
                'Invalid message distribution mode: {0}'.format(distribution))

