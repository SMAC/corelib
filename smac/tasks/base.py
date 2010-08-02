# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Base classes and interfaces to work with tasks which automatically update
throughout the whole SMAC system.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>

@todo: Create a ITask adapter for thrift tasks types which adds the Task base
       class through mix-in.
        1) Is this really needed?
        2) There are some values which have to be set manually?
        3) How do add a mix-in to an instance? We could monkey patch the
           Thrift base class to include it at already creation time.
        4) See http://www.linuxjournal.com/article/4540
"""


import uuid
import time

from twisted.internet import defer
from twisted.python import components
from zope.interface import Attribute, Interface, implements

from smac import amqp
from smac.conf.topology import queue, binding
from smac.api.tasks import ttypes as types, TaskServer, TaskListener
from smac.tasks import error


class ITask(Interface):
    """
    @todo: Documentation
    """
    
    id = Attribute("""The ID of this task""")
    type = Attribute("""The type of this task, a value of smac.api.base.ttypes.types.TaskType""")
    status = Attribute("""The status of this class, a value of smac.api.base.ttypes.types.TaskStatus""")
    status_text = Attribute("""A small label to describe the current task status""")
    remaining = Attribute("""An integer value indicating the estimated remaining time, in seconds""")
    completed = Attribute("""A float value indicating the completed % of the task (0...1)""")
    
    def __eq__(other):
        """
        """
    
    def __hash__():
        """
        """
    
    def subscribe(client):
        """Sets the client to which the task instance should send the updates"""
    
    def run(*args, **kwargs):
        """Starts to run the task"""
        
    def pause():
        """Temporarly pause the task"""
        
    def resume():
        """Resume the task (after a call to pause)"""
        
    def cancel(msg=None):
        """Stops executing the task and mark it as cancelled"""
        
    def fail(msg=None):
        """Stops executing the task and mark it as failed"""
        
    def complete():
        """Stops executing the task and mark it as completed"""
    

def taskAdapter(task):
    class HashableTask(task.__class__):
        implements(ITask)

        def __eq__(self, other):
            if not other:
                return

            return self.id == other.id

        def __hash__(self):
            return hash(self.id)
    
    task.__class__ = HashableTask
    return task
    
components.registerAdapter(taskAdapter, types.Task, ITask)

class ICompoundTask(ITask, TaskListener.Iface):
    pass

class Task(types.Task):
    
    implements(ITask, TaskServer.Iface)
    
    def __init__(self, id=None, parent='', sessid='', name=None,
            status=types.TaskStatus.WAITING, status_text="", remaining=None,
            completed=None):
        self._task_client = None
        self.id = id or str(uuid.uuid1())
        self.parent = parent
        self.name = name or self.__class__.__name__
        self.sessid = sessid
        self._status = status
        self._status_text = status_text
        self._completed = completed
        self._started = -1
        self.finished = defer.Deferred()
    
    def __eq__(self, other):
        if not other:
            return
        
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def subscribe(self, client):
        self._task_client = client
        self.notify()
    
    def notify(self):
        if not self._task_client or self.status is None:
            return defer.succeed(None)
        return self._task_client.update(self)
    
    @property
    def started(self):
        # Allow overriding in subclass
        return self._started
    
    @property
    def type(self):
        return types.TaskType.UNDETERMINED if self.completed is None else types.TaskType.DETERMINED
    
    @property
    def elapsed(self):
        return int(time.time() - self.started)
    
    @property
    def remaining(self):
        if self._status is types.TaskStatus.COMPLETED:
            return 0
        elif not self.completed:
            return -1
        
        elapsed = self.elapsed
        return int(1.0 / self.completed * elapsed) - elapsed
    
    def status():
        def fget(self):
            return self._status
        
        def fset(self, status):
            if status is not self._status:
                self._status = status
                self.notify()
        
        return locals()
    status = property(**status())
    
    def status_text():
        def fget(self):
            return self._status_text
        
        def fset(self, status_text):
            if status_text != self._status_text:
                self._status_text = status_text
                self.notify()
        
        return locals()
    status_text = property(**status_text())
    
    def completed():
        def fget(self):
            return min(self._completed, 1)
        
        def fset(self, completed):
            if not self._completed or completed // 0.01 > self._completed // 0.01:
                self._completed = completed
                self.notify()
            else:
                self._completed = completed
        
        return locals()
    completed = property(**completed())
    
    def start(self, *args, **kwargs):
        assert self.status is types.TaskStatus.WAITING, "Task already started"
        self._started = time.time()
        d = defer.maybeDeferred(self.run, *args, **kwargs)
        self.status = types.TaskStatus.RUNNING
        return d
    
    def finish(self):
        return self.finished
    
    def run(self, *args, **kwargs):
        raise NotImplementedError
    
    def info(self):
        return self
        
    def module(self):
        return str(self.owner.address)
    
    def pause(self):
        if self.status is not types.TaskStatus.RUNNING:
            raise ValueError("Can't resume a non running task.")
        
        self.status = types.TaskStatus.PAUSED
    
    def resume(self):
        if self.status is not types.TaskStatus.PAUSED:
            raise ValueError("Can't resume a non paused task.")
        
        self.status = types.TaskStatus.RUNNING
    
    def cancel(self, msg=None):
        if self.status == types.TaskStatus.CANCELLED:
            return
        
        if msg:
            self._status_text = msg
        self.status = types.TaskStatus.CANCELLED
        self.finished.errback(error.TaskCancelled(msg))
    
    def fail(self, msg=None):
        if self.status == types.TaskStatus.FAILED:
            return
        
        if msg:
            self._status_text = msg
        self.status = types.TaskStatus.FAILED
        self.finished.errback(error.TaskFailed(msg))
    
    def complete(self, msg=None):
        if self.status == types.TaskStatus.COMPLETED:
            return
        
        if msg:
            self._status_text = msg
        self.completed = 1
        self.status = types.TaskStatus.COMPLETED
        self.finished.callback(self)
    

class CompoundTask(Task):
    
    implements(ICompoundTask)
    
    queues = (
        queue('', (
            binding('tasks', 'tasks.{routing_key}.updates'),
        ), extra={
            'exclusive': True,
            'auto_delete': True,
        }),
    )
    
    def __init__(self, *args, **kwargs):
        super(CompoundTask, self).__init__(*args, **kwargs)
        self.children = {}
        self.clients = {}
        self.tasks = ()
        self.add_lock = defer.DeferredLock()
    
    @defer.inlineCallbacks
    def update(self, task):
        if task.id == self.id:
            return
        
        if task.parent != self.id:
            return
        
        yield self.add(task)
        
        #if self.completed is 1 and self.status is not types.TaskStatus.COMPLETED:
        #    self.complete()
    
    @property
    def type(self):
        undet = types.TaskType.UNDETERMINED
        
        if not self.tasks or filter(lambda t: t.type is undet, self.tasks):
            return undet
        
        return types.TaskType.DETERMINED
    
    @property
    def status(self):
        statuses = [0 for i in range(7)]
        
        if not self.tasks:
            return types.TaskStatus.WAITING
        
        for t in self.tasks:
            statuses[t.status] += 1
        
        for status in (types.TaskStatus.RUNNING, types.TaskStatus.PAUSED,
                types.TaskStatus.WAITING, types.TaskStatus.FAILED,
                types.TaskStatus.COMPLETED, types.TaskStatus.CANCELLED):
            if statuses[status]:
                break
        
        return status
    
    @property
    def completed(self):
        det = 0
        completed = 0
        
        for t in self.tasks:
            if t.type is types.TaskType.DETERMINED:
                det += 1
                completed += t.completed
        
        return completed*1.0 / det if det else None
    
    @property
    def started(self):
        return min([t.started for t in self.tasks]) if self.tasks else -1
    
    @defer.inlineCallbacks
    def add(self, task):
        assert task.parent == self.id
        
        yield self.add_lock.acquire()
        
        try:
            if task not in self.children:
                address = amqp.models.Address(routing_key='tasks.{0}.commands'.format(task.id))
                self.clients[task.id] = yield amqp.build_client(address, TaskServer, distribution='tasks')
            
            self.children[task.id] = ITask(task)
            self.tasks = self.children.values()
        finally:
            self.add_lock.release()
    
    def complete(self, msg=None):
        for c in self.clients.values():
            c.complete(msg)
        
        if msg:
            self.status_text = msg
    
    def start(self, *args, **kwargs):
        pass


