
from twisted.internet import defer

from smac import amqp, api
from smac.session.setup import AcquisitionSetup
from smac.session import tasks
from smac.session.remote import Handler

__all__ = ('AcquisitionSession', 'AcquisitionSetup', 'Handler')


class AcquisitionSession(object):
    """
    A class which abstracts and handles the session task handling process,
    from acquisition to publishing.
    """
    
    def __init__(self, model):
        """
        Initializes a new C{Session} object using the data contained in a
        persistent storage object (normally managed by C{axiom}).
        """
        self.model = model
        """Session model used to save tha chanhes"""
        
        self.setup = AcquisitionSetup(model.setup)
        """The setup to use for this acquisiton session."""
        
        self.tasks= {}
        """Mapping of C{CompoundTasks} for this acquisiton session"""
    
    def configure(self):
        """
        Initializes the acquistion session on all involved modules by calling
        the C{configure_session} service method.
        
        Once the deferred returned by this method fires, all modules are
        supposed to be ready to receive session specific commands on the AMQP
        channel defined by the session ID.
        
        @todo: Catch C{thrift.transport.TTransport.TTransportException}
               exceptions to handle offline modules.
        """
        def configure(client, session):
            return client.configure_session(session)
        
        factory = amqp.build_client
        handler = api.base.SessionModule
        
        modules = (amqp.models.IAddress(m) for m in self.setup.modules())
        deferreds = (factory(m, handler) for m in modules)
        results = (d.addCallback(configure, self.model) for d in deferreds)
        
        return defer.gatherResults(list(results))
    
    def record(self):
        """
        Starts the acquisition of the current session and returns a
        C{smac.tasks.CompoundTask} instance to manage the process.
        """
        self.tasks['recording'] = tasks.Acquisition(sessid=self.model.id)
        self.tasks['recording'].start()
        return self.tasks['recording']
    
    def archive(self):
        """
        Starts the archivation of the current session and returns a
        C{smac.tasks.CompoundTask} instance to manage the process.
        """
        self.tasks['archiving'] = tasks.Archivation(sessid=self.model.id)
        self.tasks['archiving'].start()
        return self.tasks['archiving']
    
    def analyze(self):
        pass
    
    def publish(self):
        pass
    




