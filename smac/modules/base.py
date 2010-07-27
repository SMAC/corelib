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

from zope.interface import implements, providedBy

from twisted.internet import reactor
from twisted.internet.reactor import callLater
from twisted.internet.defer import inlineCallbacks

from smac.modules.imodule import IModule
from smac.amqp.routing import Address
from smac.api.ttypes import GeneralModuleInfo, InvalidTask
from smac.api.logger.constants import LOGGER_ROUTING_KEY
from smac.contrib.twisted.log import TxAMQPLoggingObserver
from smac.util.hooks import register
from smac.tasks import ITask, ThriftTaskAdapter
from smac.conf import settings

class Handler(object):
    def teardown(self, ):


class ModuleBase(Handler):
    __metaclass__ = abc.ABCMeta
    
    implements(IModule)
    
    def __init__(self, id):
        self.id = id
        self.tasks = dict()
        self.channel = None
        self.client_factory = None
        self.queues = None
        
        self.special = False
    
    
    def add_task(self, task):
        task = ITask(task)
        
        assert task.id not in self.tasks, "Task already added to the tasks register"
        
        task.module = self.address
        task.add_observer(self.task_updated_callback)
        self.tasks[task.id] = task
        
        self.task_updated_callback(task)
        
    def remove_task(self, task):
        assert task.id in self.tasks, "Task is not present in the tasks register"
        
        task.remove_observer(self.task_updated_callback)
        del self.tasks[task.id]
    
    def task_updated_callback(self, task, *args, **kwargs):
        address = Address(self.namespace, 'Controller')
        
        def update(client):
            client.update_task(ThriftTaskAdapter(task))
        
        self.client_factory.build_client(address, 'broadcast').addCallback(update)
    
    def get_task(self, task_id):
        try:
            return ThriftTaskAdapter(self.tasks[task_id])
        except KeyError:
            raise InvalidTask(task_id)
    
    def get_tasks(self):
        return [ThriftTaskAdapter(task) for task in self.tasks.values()]
    
    @property
    def interface(self):
        return self._iface if self.special else str(list(providedBy(self))[0].__module__).split('.')[-1]
    
    @property
    def implementation(self):
        return self._impl if self.special else str(self.__class__.__name__).split('.')[-1]
    
    @property
    def namespace(self):
        return settings.amqp.namespace
    
    @property
    def address(self):
        return Address(
            namespace=self.namespace,
            interface=self.interface,
            implementation=self.implementation,
            instance_id=self.id
        )
    
    @register('pre_startup')
    @inlineCallbacks
    def retrieve_info(self):
        hostname = socket.gethostname()
        address = self.address.to_module_address()
        
        self.info = GeneralModuleInfo(hostname=hostname, address=address, ip_address=None)
        self.info.ip_address = yield reactor.resolve(socket.gethostname())
    
    @register('post_startup')
    def start_log_streaming(self):
        if (settings.stream_logs):
            routing_key = LOGGER_ROUTING_KEY.format(**self.address._asdict())
            address = Address(self.namespace, 'logger', key=routing_key)
            
            def start(client):
                TxAMQPLoggingObserver(client, self.address).start()
                
            self.client_factory.build_client(address).addCallback(start)
    
    @register('post_startup')
    def do_announce(self, client=None):
        import time
        
        if client is None:
            from smac.amqp import client
            
            #channel = yield client.channel(2)
            #yield channel.channel_open()
            
            factory = self.client_factory
            #factory = AMQClientFactory(client, 2)
            
            factory.build_client(Address(self.namespace)).addCallback(self.do_announce)
            return
        
        client.announce(self.info, time.time())
        
        if self.address.interface == 'Recorder':
            print "SENT", time.time(), id(self)
        
        callLater(settings.ping_interval, self.do_announce, client)
    
    def announce(self, info, timestamp):
        pass
        
    def ping(self):
        print "Ping"

