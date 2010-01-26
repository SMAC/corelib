from twisted.internet.reactor import callLater
from observer import Observable
from zope.interface import implements

class TimedSet(set, Observable):
    """docstring for TimedSet"""
    
    def __init__(self, timeout):
        self.timeout = timeout
        self.removers = {}
    
    def remove(self, value):
        super(TimedSet, self).remove(value)
        self.notify_observers('removed', value)
    
    def discard(self, value):
        if value in self:
            self.remove(value)
    
    def add(self, value):
        if value in self:
            self.removers[value].reset(self.timeout)
        else:
            super(TimedSet, self).add(value)
            self.notify_observers('added', value)
            r = callLater(self.timeout, self.discard, value)
            self.removers[value] = r
        