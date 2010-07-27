import inspect
from twisted.internet.defer import maybeDeferred, DeferredList

def execute_hook(klass, name, *args, **kwargs):
    def registered(f):
        try:
            return f.__func__.hook == name
        except AttributeError:
            return False
    
    hooks = inspect.getmembers(klass, registered)
    
    return DeferredList([maybeDeferred(m, *args, **kwargs) for _, m in hooks])

def register(hook):
    def inner(func):
        func.hook = hook
        return func
    
    return inner