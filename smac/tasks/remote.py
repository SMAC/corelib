# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Objects and utilities to work on remote tasks.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from twisted.internet import defer
from zope.interface import implements

from smac.amqp.models import Address
from smac.api.tasks import TaskListener, TaskServer
from smac.conf.topology import queue, binding
from smac.python import log


class TaskManager(object):
    
    implements(TaskListener.Iface)
    
    queues = (
        queue('', (
            binding('tasks', 'tasks.{routing_key}.updates'),
        ), extra={
            'exclusive': True,
            'auto_delete': True,
        }),
    )
    
    def __init__(self, client_factory):
        self.tasks = {}
        self.modules = {}
        self.client_factory = client_factory
    
    def update(self, task):
        """
        Only method required to implement the L{TaskListener.Iface} interface.
        Checks if the updated task is already registered and creates a new one
        if needed. If already present updates the available one.
        """
        if task.id not in self.tasks:
            log.info("New task with ID {0} received".format(task.id))
        else:
            log.debug("Task with ID {0} updated".format(task.id))
            log.debug("Done: {0:.1f}%  Remaining: {1} seconds  Status: {2}  Message: {3}".format(
                    (task.completed or 0) * 100, task.remaining, task.status, task.status_text))
        
        self.tasks[task.id] = task
    
    @defer.inlineCallbacks
    def add(self, task_id):
        address = Address(routing_key='tasks.{0}.commands'.format(task_id))
        client = yield self.client_factory(address, TaskServer, distribution='tasks')
        task = yield client.info()
        self.update(task)
    
    def remove(self, task_id):
        del self.tasks[task_id]
    
    def removeall(self):
        pass
    

