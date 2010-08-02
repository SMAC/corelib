
from twisted.internet import defer
from zope.interface import implements

from smac.amqp.models import Address
from smac.api.session import SessionListener
from smac.conf.topology import queue, binding
from smac.python import log
from smac.tasks.base import ITask


class SessionListener(object):
    
    implements(SessionListener.Iface)
    
    queues = (queue('', (
        binding('sessions', 'sessions.{routing_key}.commands'),
    ), extra={
        'exclusive': True,
        'auto_delete': True
    }),)
    
    def __init__(self, host, session):
        self.session = session
        self.host = host
    
    def recording_start(self, task):
        pass
    
    def recording_stop(self, task):
        pass
    
    def archive(self, task):
        pass
    
    def analyze(self, task):
        pass
    
    def publish(self, task):
        pass
    