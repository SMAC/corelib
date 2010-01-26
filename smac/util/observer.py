from zope.interface import Interface, implements

class IObservable(Interface):
    def add_observer(method, signal=None):
        """Adds an observer to this instance"""
    
    def remove_observer(method, signal=None):
        """Removes the specified observer from the instance"""
    
    def notify_observers(signal=None, *args, **kwargs):
        """Notifies all registered observers of a change to the class"""
    
class Observable(object):
    implements(IObservable)
    
    observers = {}
    
    def add_observer(self, method, signal=None):
        if signal is None:
            signal = 'global'
        
        if signal not in self.observers:
            self.observers[signal] = set()
        
        self.observers[signal].add(method)
    
    def remove_observer(self, method, signal=None):
        if signal is None:
            signal = 'global'
        
        if signal not in self.observers:
            return
        
        self.observers[signal].discard(method)
    
    def notify_observers(self, signal=None, *args, **kwargs):
        if signal is None:
            signal = 'global'
        
        if signal not in self.observers:
            return
        
        map(lambda o: o(self, signal, *args, **kwargs), self.observers[signal])
