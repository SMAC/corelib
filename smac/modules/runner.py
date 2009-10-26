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
A twisted application configuration file used by smac to start up new module
instances using the twisted application infrastructure.
This file is passed as argument to a emulated call to the C{twistd}
command line application runner.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

from twisted.application import service, internet

from thrift.transport.TTwisted import ThriftServerFactory
from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory

from smac.core.management.commands.run import startup_registry
from smac.amqp.factory import AMQServerFactory
from smac.utilities import merge_queues

Processor = startup_registry['processor']
handler = startup_registry['handler']
s = startup_registry['settings']

##
# Thrift processor
##
handler.settings = s
handler.id = startup_registry['instance_id']
processor = Processor(handler)

##
# Twisted application
##
application = service.Application("SMAC module")
serviceCollection = service.IServiceCollection(application)

##
# AMQP Client
##
merge_queues(s.additional_bindings)

factory = AMQServerFactory(
    processor,
    s.amqp.spec,
    s.amqp.vhost,
    s.amqp.user,
    s.amqp.password
)
amqp_service = internet.TCPClient(s.amqp.host, s.amqp.port, factory)
amqp_service.setServiceParent(serviceCollection)

##
# RPC Server
##
if s.rpc.run_server:
    factory = ThriftServerFactory(processor, TBinaryProtocolFactory())
    rpc_service = internet.TCPServer(s.rpc.port, factory)
    rpc_service.setServiceParent(serviceCollection)

##
# @TODO
# Use POSIX Local IPC Sockets for local-local communication
##
