
from zope.interface import implements

from smac.api.session import SessionListener
from smac.conf.topology import queue, binding
from smac.session.setup import AcquisitionSetup


class Handler(object):
    
    implements(SessionListener.Iface)
    
    queues = (queue('', (
        binding('sessions', 'sessions.{routing_key}.commands'),
    ), extra={
        'exclusive': True,
        'auto_delete': True
    }),)
    
    def __init__(self, host, session):
        self.session = session
        self.setup = AcquisitionSetup(session.setup)
        self.host = host
    
    def record(self, task):
        pass
    
    def archive(self, task):
        pass
    
    def analyze(self, task):
        pass
    
    def publish(self, task):
        pass
    