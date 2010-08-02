from twisted.python import log
import logging

def _log(func, level, *message, **kw):
    defaults = {
        'logLevel': level,
    }
    defaults.update(kw)
    func(*message, **defaults)

def failure(msg, failure=None, **kwargs):
    log.err(failure, msg, **kwargs)
fail = failure

def critical(msg, **kwargs):
    _log(log.msg, logging.CRITICAL, msg, **kwargs)
crit = critical

def error(msg, **kwargs):
    _log(log.msg, logging.ERROR, msg, **kwargs)
err = error

def warning(msg, **kwargs):
    _log(log.msg, logging.WARNING, msg, **kwargs)
warn = warning
    
def info(msg, **kwargs):
    _log(log.msg, logging.INFO, msg, **kwargs)

def debug(msg, **kwargs):
    _log(log.msg, logging.DEBUG, msg, **kwargs)