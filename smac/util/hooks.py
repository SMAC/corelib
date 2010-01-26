import inspect

def execute_hook(klass, name, *args, **kwargs):
    def registered(f):
        try:
            return f.__func__.hook == name
        except AttributeError:
            return False
    
    [m(*args, **kwargs) for _, m in inspect.getmembers(klass, registered)]

def register(hook):
    def inner(func):
        func.hook = hook
        return func
    
    return inner