# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
A twisted application configuration file used by smac to start up new module
instances using the twisted application infrastructure.
This file is passed as argument to a emulated call to the C{twistd}
command line application runner.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from twisted.application import service, internet

from smac.core.management.commands.run import startup_registry
from smac.util import merge_queues
from smac.conf import settings
from smac.python import log
from smac.amqp.service import AMQService, ThriftAMQService
from smac.rpc.service import ThriftRPCService


if startup_registry['__name__'] == '__main__': # Set by the 'smac run' command
    
    class FactorySetter(service.Service):
        def startService(self):
            from smac import amqp
            amqp._client_factory = self.parent.client_factory
            amqp._server_factory = self.parent.server_factory
            log.info("Global factories setted")
    
    # Twisted application
    application = service.Application("SMAC module")
    serviceCollection = service.IServiceCollection(application)

    processor = startup_registry['amqp_processor']
    handler = startup_registry['handler'](startup_registry['instance_id'])

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
    
    FactorySetter().setServiceParent(amqp_service)

    # AMQP Thrift service
    #merge_queues(settings.additional_bindings)
    thrift_service = ThriftAMQService(processor, handler)
    thrift_service.setServiceParent(amqp_service)

    # RPC Thrift service
    try:
        processor = startup_registry['rpc_processor']
    except KeyError:
        pass
    else:
        rpc_service = ThriftRPCService(settings.rpc.port, processor, handler)
        rpc_service.setServiceParent(serviceCollection)

    # @todo: Use POSIX Local IPC Sockets for local-local communication
