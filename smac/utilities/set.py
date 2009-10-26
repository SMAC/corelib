from twisted.internet.reactor import callLater

class TimedSet(set):
    """docstring for TimedSet"""
    
    def __init__(self, timeout):
        self.timeout = timeout
        self.removers = {}
    
    def add(self, value):
        if value in self:
            self.removers[value].reset(self.timeout)
        else:
            super(TimedSet, self).add(value)
            r = callLater(self.timeout, self.discard, value)
            self.removers[value] = r
        