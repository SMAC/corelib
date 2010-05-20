from zope.interface import Attribute, implements
from smac.util.observer import IObservable, Observable

from smac.api.ttypes import TaskType, TaskStatus, TimeDelta, Task as ThriftTask

from twisted.python import components

"""
NOTE: An adapter for a task should implement the hash method to compare equal to other instances of
the adapter with the same task instances.

__hash__ + __eq__ || __cmp__
"""

class ITask(IObservable):
    """An interface for Tasks to be executed remotely by SMAC modules."""
    
    id = Attribute("""The ID of this task""")
    status = Attribute("""The status of this class, a value of smac.api.base.ttypes.TaskStatus""")
    status_text = Attribute("""A small label to describe the current task status""")
    module = Attribute("""A module address instance""")
    remaining = Attribute("""An integer value indicating the estimated remaining time, in seconds""")
    completed = Attribute("""A float value indicating the completed % of the task (0...1)""")
    
    def run(*args, **kwargs):
        """Starts to run the task"""
        
    def pause():
        """Temporarly pause the task"""
        
    def resume():
        """Resume the task (after a call to pause)"""
        
    def fail(msg=None):
        """Stops executing the task and mark it as failed"""
        
    def complete():
        """Stops executing the task and mark it as completed"""

class Task(Observable):
    implements(ITask)
    
    def __init__(self, id, status=TaskStatus.PAUSED, status_text="",
            remaining=None, completed=None):
        self.id = id
        self.status = status
        self.status_text = status_text
        self.remaining = remaining
        self.completed = completed
    
    @property
    def type(self):
        if self.completed is not None:
            return TaskType.DETERMINED
        else:
            return TaskType.UNDETERMINED
        
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def resume(self):
        raise NotImplementedError

    def fail(self, msg=None):
        raise NotImplementedError

    def complete(self):
        raise NotImplementedError

def ThriftTaskAdapter(task):
    remaining, completed = None, None
    
    task = ITask(task)
    
    if task.type == TaskType.DETERMINED:
        completed = task.completed
        
        if task.remaining:
            remaining = TimeDelta(task.remaining.days, task.remaining.seconds, task.remaining.microseconds)
    
    return ThriftTask(id=task.id, status=task.status, status_text=task.status_text, type=task.type,
            module=task.module.to_module_address(), remaining=remaining, completed=completed)

