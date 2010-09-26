# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
A twisted application configuration file used by smac to start up new module
instances using the twisted application infrastructure.
This file is passed as argument to a emulated call to the C{twistd}
command line application runner.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from twisted.application import service

from smac.core.management.commands.run import startup_registry
#from smac.util import merge_queues
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
            amqp._delegate = self
            log.info("Global factories setted")
        
        def processing_error(self, failure):
            log.error("An error occurred while processing a message!")
            log.error(failure)
        
        def queue_closed(self, failure):
            pass
        
        def queue_error(self, failure):
            log.error("Queue error!")
            log.error(failure)
    
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
    # @todo: merge_queues(settings.additional_bindings)
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
    
    
    #from twisted.internet import reactor
    #from twisted.cred import portal, checkers
    #from twisted.conch import manhole, manhole_ssh
    #
    #def createShellServer( ):
    #    print 'Creating shell server instance'
    #    print 'Listening on port 2222'
    #    reactor.listenTCP(2222, getManholeFactory(globals(), admin='aaa'))
    #
    #def getManholeFactory(namespace, **passwords):
    #    realm = manhole_ssh.TerminalRealm() 
    #    def getManhole(_):
    #        return manhole.Manhole(namespace) 
    #    
    #    realm.chainedProtocolFactory.protocolFactory = getManhole
    #    p = portal.Portal(realm) 
    #    p.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
    #    f = manhole_ssh.ConchFactory(p)
    #    return f
    #reactor.callWhenRunning( createShellServer )

    # @todo: Use POSIX Local IPC Sockets for local-local communication
