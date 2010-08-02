from zope.interface import Interface, implements

class IObservable(Interface):
    def subscribe(method, signal=None):
        """Adds an observer to this instance"""
    
    def unsubscribe(method, signal=None):
        """Removes the specified observer from the instance"""
    
    def notify(signal=None, *args, **kwargs):
        """Notifies all registered observers of a change to the class"""
    
class Observable(object):
    implements(IObservable)
    
    observers = {}
    
    def subscribe(self, callback, signal=None):
        if signal is None:
            signal = 'global'
        
        if signal not in self.observers:
            self.observers[signal] = set()
        
        self.observers[signal].add(callback)
    
    def unsubscribe(self, callback, signal=None):
        if signal is None:
            signal = 'global'
        
        if signal not in self.observers:
            return
        
        self.observers[signal].discard(callback)
    
    def notify(self, signal=None, *args, **kwargs):
        if signal is None:
            signal = 'global'
        
        if signal not in self.observers:
            return
        
        map(lambda o: o(self, signal, *args, **kwargs), self.observers[signal])
