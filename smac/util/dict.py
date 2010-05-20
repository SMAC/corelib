from twisted.internet.reactor import callLater
from observer import Observable

class TimedDict(dict, Observable):
    """
    A dictionary which holds values only for the given timeout. When the time
    elapses, the value is deleted and the observers fired.
    
    Each time a value is added, the timeout for the given key is resetted. If
    a value for the given key is already present and the new value strictly
    differs (is not), then an 'upated' event is fired.
    """
    
    def __init__(self, timeout, *args, **kwargs):
        self.timeout = timeout
        self.removers = {}
        
        super(TimedDict, self).__init__(*args, **kwargs)
    
    def __delitem__(self, key):
        # Save the current value
        value = self[key]
        
        # Remove from the dict
        super(TimedDict, self).__delitem__(key)
        
        # Remove the remover callback
        if self.removers[key].active():
            self.removers[key].cancel()
        del self.removers[key]
        
        # Notify the observers
        self.notify_observers('removed', key, value)
    
    def __setitem__(self, key, value):
        updated = added = False
        
        if key in self:     # If the key is present, reset the timeout
            self.removers[value].reset(self.timeout)
            
            # If the values differs, set the updated flag to true
            if self[key] is not value:
                updated = True
        else:               # Else set a new delayed call
            added = True
            r = callLater(self.timeout, self.__delitem__, key)
            self.removers[key] = r
        
        # Commit the changes
        super(TimedDict, self).__setitem__(key, value)
        
        # If needed, notify the observers
        if updated:
            self.notify_observers('updated', key, value)
        elif added:
            self.notify_observers('added', key, value)
    
    def breathe(self, key):
        """
        Resets the timeout for the given key without changing the value or
        firing any event.
        """
        self.removers[key].reset(self.timeout)
            