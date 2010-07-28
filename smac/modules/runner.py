# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
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
A twisted application configuration file used by smac to start up new module
instances using the twisted application infrastructure.
This file is passed as argument to a emulated call to the C{twistd}
command line application runner.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2010 MISG/ICTI/EIA-FR
@license: GPLv3
"""

from twisted.application import service, internet

from thrift.transport.TTwisted import ThriftServerFactory
from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from smac.core.management.commands.run import startup_registry
from smac.util import merge_queues
from smac.conf import settings
from smac.amqp.service import AMQService, ThriftAMQService


processor = startup_registry['processor']
handler = startup_registry['handler'](startup_registry['instance_id'])

# Twisted application
application = service.Application("SMAC module")
serviceCollection = service.IServiceCollection(application)

# AMQP Client service
amqp_service = AMQService(
    settings.amqp.spec,
    settings.amqp.host,
    settings.amqp.port,
    settings.amqp.vhost,
    settings.amqp.user,
    settings.amqp.password,
    settings.amqp.channel
)
amqp_service.setName("AMQ Connection layer")
amqp_service.setServiceParent(serviceCollection)

# AMQP Thrift service
#merge_queues(settings.additional_bindings)
thrift_service = ThriftAMQService(processor, handler)
thrift_service.setServiceParent(amqp_service)

# RPC Thrift service
# @todo: Create a ThriftRPCService to wrap this
if settings.rpc.run_server:
    factory = ThriftServerFactory(processor.Processor(handler), TBinaryProtocolFactory())
    rpc_service = internet.TCPServer(settings.rpc.port, factory)
    rpc_service.setServiceParent(serviceCollection)

# @todo: Use POSIX Local IPC Sockets for local-local communication
