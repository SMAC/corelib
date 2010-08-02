# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Interfaces and base classes to extend to implement service handlers with task
support.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

from twisted.internet import defer
from zope.interface import Attribute, Interface, implements

from smac.api.base import TaskModule as TTaskModule
from smac.modules.amqp import AMQModule
from smac.tasks import TaskRegister


class ITaskRegisterProvider(Interface):
    """
    Each object implementing this interface should be able to accept and
    register a new task and offering means to access and manage them.
    """
    
    task_register = Attribute("""
        An C{TaskRegister} instance with an active AMQ client to broadcast
        updates.
        """)
    

class TaskModule(AMQModule):
    """
    Basic implementation of the C{ITaskRegisterProvider} and
    C{smac.api.base.TaskModule.Iface} interfaces.
    """
    
    implements(ITaskRegisterProvider, TTaskModule.Iface)
    
    @defer.inlineCallbacks
    def amq_start(self, *args, **kwargs):
        yield super(TaskModule, self).amq_start(*args, **kwargs)
        
        self.task_register = TaskRegister(self.amq_server, self.amq_client)
    
    def tasks(self):
        return [t.id for t in self.task_register.all()]
    

    