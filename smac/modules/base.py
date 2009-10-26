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
The base class for a SMAC module implementation. This class offers many
already implemented methods and is thus advised to extend from this class for
a new implementation.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

import abc
import socket

from zope.interface import * #implements, implementedBy

from twisted.python import log
from twisted.internet.reactor import callLater
from twisted.internet.defer import inlineCallbacks

from smac.modules.imodule import IModule
from smac.amqp.routing import Address
from smac.api.base.ttypes import GeneralModuleInfo, ModuleAddress
from smac.api.logger.constants import LOGGER_ROUTING_KEY
from smac.contrib.twisted.log import TxAMQPLoggingObserver

class ModuleBase(object):
    __metaclass__ = abc.ABCMeta
    
    implements(IModule)
    
    def set_channel(self, channel):
        self.channel = channel
    
    def set_client_factory(self, factory):
        self.client_factory = factory
    
    ##
    # Properties
    ##
    @property
    def interface(self):
        return str(list(providedBy(self))[0].__module__).split('.')[-1]
        #return PKG_CLS_SEPARATION.join(str(list(providedBy(self))[0].__module__).split('.')[-2:])
    
    @property
    def implementation(self):
        return str(self.__class__.__name__).split('.')[-1]
    
    @property
    def namespace(self):
        return self.settings.amqp.namespace
    
    @property
    def address(self):
        return Address(
            namespace=self.namespace,
            interface=self.interface,
            implementation=self.implementation,
            instance_id=self.id
        )
    
    ##
    # Hooks
    ##
    def _pre_startup(self):
        self.pre_startup()
    
    def pre_startup(self):
        pass
    
    def _post_startup(self):
        # Send announce message to all modules
        self.client_factory.build_client(Address(self.namespace)).addCallback(self.do_announce)
        
        # Startup logging observer
        routing_key = LOGGER_ROUTING_KEY.format(**self.address._asdict())
        self.client_factory.build_client(Address(self.namespace, 'logger', key=routing_key)).addCallback(self.start_log_streaming)
        
        self.post_startup()
    
    def post_startup(self):
        pass
        
    def _tear_down(self):
        self.tear_down()
    
    def tear_down(self):
        pass
        
    ##
    # API Methods
    ##
    
    def announce(self, info):
        pass
        
    ##
    # Utility methods
    ##
    def start_log_streaming(self, client):
        observer = TxAMQPLoggingObserver(client, self.address)
        
        if (self.settings.stream_logs):
            observer.start()
            
            # Some extra formatting to see the startup in the log file
            log.msg("")
            log.msg("----------------- AMQP log streaming started -----------------")
            log.msg("")
    
    def do_announce(self, client):
        info = GeneralModuleInfo(
            hostname=socket.gethostname(),
            address=self.address.to_module_address(),
            ip_address=socket.gethostbyname(socket.gethostname()))
        
        client.announce(info)
        
        callLater(self.settings.ping_interval, self.do_announce, client)


