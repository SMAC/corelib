from twisted.python import log

def log_calls(func):
    def decorated(*args, **kwargs):
        log.msg("{0}.{1} called".format(args[0].__class__.__name__, func.__name__))
        return func(*args, **kwargs)
    
    return decorated