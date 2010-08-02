# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
An RPC service for thrift modules.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from thrift.transport.TTwisted import ThriftServerFactory
from twisted.application import service, internet
from twisted.internet import defer, reactor, protocol

from smac.python import log
from smac.modules.rpc import IRPCServiceHandler


class ThriftRPCService(internet.TCPServer, object):
    def __init__(self, port, processor, handler):
        self.processor = processor
        self.handler = IRPCServiceHandler(handler)
        
        factory = ThriftServerFactory(processor.Processor(handler), TBinaryProtocolFactory())
        super(ThriftRPCService, self).__init__(port, factory)
    
    def startService(self):
        super(ThriftRPCService, self).startService()
        log.info("ThriftRPCService started, notifying handler")
        self.handler.rpc_start(self)
    
    @defer.inlineCallbacks
    def stopService(self):
        log.info("ThriftRPCService stopping, notifying handler")
        yield self.handler.rpc_stop()
        log.info("ThriftRPCService handler shutdown procedure terminated, stopping service")
        super(ThriftRPCService, self).stopService()
    


