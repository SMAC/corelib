import copy

from lxml import etree
from twisted.internet import defer, reactor

from smac.conf.specifications.schemata import setup_structure
from smac.acquisition.errors import ModuleNotAvailable
from smac.amqp.models import IAddress
from smac.python import log

class AcquisitionSetup(object):
    """
    Represents an acquisition setup and offers methods to operate on it.
    The model is based on an XML instance.
    """
    
    NAMESPACE = 'http://smac.hefr.ch'
    PASSTHROUGH = 'Processor.Passthrough'
    
    def __init__(self, setup=None):
        """
        Creates a new acquisition session from scratch or from a provided XML
        string or document.
        
        @param setup: An XML string or an XML document instance describing the
                      acquisition setup.
        """
        
        if setup is None:
            self.setup = etree.Element('{%s}setup' % self.namespace, nsmap={
                'smac': self.NAMESPACE
            })
        elif isinstance(setup, basestring):
            self.setup = etree.fromstring(setup)
        elif isinstance(setup, etree.Element):
            self.setup = copy.deepcopy(setup)
            
        self._cache = {}
    
    def is_valid(self):
        """
        Validates the setup document against the business rules.
        """
        return setup_structure.validate(self.setup)
    
    def is_available(self, client_factory, recorders_only=False):
        """
        Checks whether all assets needed for the complete acquisition process
        are available.
        
        If the C{recorders_only} flag is set to true, then this method checks
        only if all recorders are available. Useful to begin an acquisition
        as soon as all recorders are available, without worrying about other
        assets.
        """
        
        modules = self.recorders()
        
        if not recorders_only:
            modules += self.processors + self.archivers
        
        deferreds = []
        
        for m in modules:
            deferreds.append(client_factory(m).addCallback(lambda m: m.ping() or m))
        
        pings = defer.DeferredList(deferreds)
        
        def timeout(deferred):
            log.warn("Some modules are not available.")
            deferred.errback(ModuleNotAvailable())
        
        def callback(result, delayed):
            if delayed.active():
                delayed.cancel()
            return result
        
        def errback(failure, delayed):
            if delayed.active():
                delayed.cancel()
            return failure
        
        delayed = reactor.callLater(3, timeout, pings)
        pings.addCallback(callback, delayed)
        pings.addErrback(errback, delayed)
        
        return pings
    
    def recorders(self):
        """
        A tuple containing all recorder modules used in this acquisition setup.
        """
        
        if 'recorders' not in self._cache:
            query = '/s:setup/s:use/@recorder'
        
            recorders = set(self.setup.xpath(query, namespaces={
                's': self.NAMESPACE,
            }))
        
            self._cache['recorders'] = map(IAddress, recorders)
        
        return self._cache['recorders']
    
    def devices(self, recorder=None):
        query = '/s:setup/s:use'
        
        if recorder:
            query += '[@recorder=\'%s\']' % recorder.routing_key
        
        uses = self.setup.xpath(query, namespaces={
            's': self.NAMESPACE,
        })
        uses = ((u.get('recorder'), u.get('device')) for u in uses)
        uses = set(uses)
        
        return tuple((IAddress(rec), device) for rec, device in uses)
    
    def streams(self, recorder=None, device=None):
        query = '/s:setup/s:use'
        
        if recorder:
            query += '[@recorder=\'%s\']' % recorder.routing_key
            
            if device:
                query += '[@device=\'%s\']' % device
        
        uses = self.setup.xpath(query, namespaces={
            's': self.NAMESPACE,
        })
        uses = ((u.get('recorder'), u.get('device'), u.get('stream')) for u in uses)
        uses = set(uses)
        
        return tuple((IAddress(rec), device, stream) for rec, device, stream in uses)
    
    def processors(self):
        """
        A list of all processors used in this acquisition setup.
        """
        
        return tuple()
    
    def archivers(self, stream=None):
        """
        A list of all archivers used in this acquisition setup.
        """
        if stream:
            if not isinstance(stream, basestring):
                # Find out the stream ID
                r, d, s = stream
                query = '/s:setup/s:use'
                query += '[@recorder=\'%s\']' % r.routing_key
                query += '[@device=\'%s\']' % d
                query += '[@stream=\'%s\']' % s
                query += '/@as'
                
                stream = self.setup.xpath(query, namespaces={
                    's': self.NAMESPACE,
                })[0]
            
            target = '/s:setup/s:connect[s:source/@target=\'%s\']/s:destination/@target' % stream
            processor = '/s:setup/s:instantiate[@as=%s][@class!=\'%s\']/@class' % (target, self.PASSTHROUGH)
            passth = '/s:setup/s:instantiate[@as=%s][@class=\'%s\']/@as' % (target, self.PASSTHROUGH)
            archiver = '/s:setup/s:connect[s:source/@target=%s]/s:destination/@target' % (passth)
            
            query = '%s | %s' % (processor, archiver)
            
            archivers = set(self.setup.xpath(query, namespaces={
                's': self.NAMESPACE,
            }))
            
            return tuple(IAddress(address) for address in archivers)
        else:
            # @todo
            raise NotImplementedError
    
    def toxmlstring(self):
        """
        Returns an XML representation of the acquisition setup.
        """
        return etree.tostring(self.setup)
    
    def toxmldoc(self):
        """
        Returns an XML document containing the acquisition setup.
        """
        return copy.deepcopy(self.setup)
    
