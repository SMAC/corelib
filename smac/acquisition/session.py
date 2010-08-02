
import uuid

from twisted.internet import defer


class AcquisitionSession(object):
    """
    This class offers complete management of an acquisition session based on
    an XML acquisition setup.
    """
    
    def __init__(self, client_factory, setup, id=None):
        """
        Creates a new acquisition session based on the given setup.
        
        @param setup: A valid AcquisitionSetup instance.
        """
        
        assert setup.is_valid()
        
        self.client_factory = client_factory
        self.setup = setup
        self.id = id or str(uuid.uuid1())
    
    @defer.inlineCallbacks
    def _call_recorders(self, method, *args, **kwargs):
        yield self.setup.is_available(self.client_factory, True)
        
        clients = [self.client_factory for c in self.setup.recorders()]
        
        deferreds = []
        
        for module in self.setup.recorders():
            client = self.client_factory(module)
            client.addCallback(getattr, method)
            client.addCallback(lambda m: m(*args, **kwargs))
            deferreds.append(client)
        
        r = yield defer.DeferredList(deferreds)
        defer.returnValue(r)
    
    def configure(self):
        return self._call_recorders('setup_session', self.id, self.setup.toxmlstring())
    
    def start_recording(self, delay=None):
        if delay:
            # @todo
            pass
        
        return self._call_recorders('start_recording', self.id)
    
    def stop_recording(self, delay=None):
        if delay:
            # @todo
            pass
        
        return self._call_recorders('stop_recording', self.id)
    
    def archive(self):
        return self._call_recorders('archive', self.id)
            