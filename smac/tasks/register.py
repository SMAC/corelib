# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Utility classes and functions to manage the whole task lifetime.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from twisted.internet import defer

from smac.amqp.models import Address
from smac.api.tasks import TaskServer, TaskListener
from smac.api.tasks.ttypes import TaskStatus
from smac.conf.topology import queue, binding
from smac.python import log
from smac.tasks.base import ITask, ICompoundTask


class TaskRegister(object):
    """
    A register of tasks to be used by single modules to hold their tasks.
    """
    
    queues = (
        queue('', (
            binding('tasks', 'tasks.{routing_key}.commands'),
        ), extra={
            'exclusive': True,
            'auto_delete': True,
        }),
    )
    
    def __init__(self, server_factory, client_factory):
        self.client_factory = client_factory
        self.server_factory = server_factory
        self.tasks = {}
        self.task_lock = defer.DeferredLock()
    
    @defer.inlineCallbacks
    def add(self, task):
        """
        Adds C{task} to the C{TaskRegister} and creates task client and server
        and assign them to the task.
        
        @todo: Check that the task does not exist yet.
        """
        yield self.task_lock.acquire()
        
        try:
            task = ITask(task)
            
            address = Address(routing_key=task.id)
            yield self.server_factory(address, TaskServer, task, self.queues)
            
            address = Address(routing_key='tasks.{0}.updates'.format(task.id))
            client = yield self.client_factory(address, TaskListener, distribution='tasks')
            
            self.tasks[task.id] = task
            task.subscribe(client)
            
            try:
                task = ICompoundTask(task)
            except TypeError:
                pass
            else:
                # Create server
                log.debug("Starting server for compound task '{0}'".format(task.id))
                address = Address(routing_key='*')
                yield self.server_factory(address, TaskListener, task, task.queues)
        finally:
            self.task_lock.release()
    
    def remove(self, task_id):
        try:
            task = self.tasks[task_id]
        except KeyError:
            raise ValueError("Invalid task ID: '{0}'".format(task_id))
        
        if task.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED,
                TaskStatus.FAILED):
            log.warn("Removing non completed task '{0}'".format(task_id))
        
        del self.tasks[task_id]
    
    def get(self, task_id):
        try:
            return self.tasks[task_id]
        except KeyError:
            raise ValueError("Invalid task ID: '{0}'".format(task_id))
    
    def all(self):
        return self.tasks.values()
    

