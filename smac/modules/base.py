# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
The base class for a SMAC module implementation. This class offers many
already implemented methods and is thus advised to extend from this class for
a new implementation.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from smac.modules.task import TaskModule


class ModuleBase(TaskModule):
    pass
    
    
    #def start_log_streaming(self):
    #    if (settings.stream_logs):
    #        routing_key = LOGGER_ROUTING_KEY.format(**self.address._asdict())
    #        address = Address(self.namespace, 'logger', key=routing_key)
    #        
    #        def start(client):
    #            TxAMQPLoggingObserver(client, self.address).start()
    #            
    #        self.client_factory.build_client(address).addCallback(start)