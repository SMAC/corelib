import copy

from lxml import etree

from smac.conf.specifications.schemata import setup_structure

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
            self.setup = etree.Element('{%s}setup' % self.NAMESPACE, nsmap={
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
    
    def modules(self):
        """
        Returns a set of all modules used in this setup.
        @todo: Add processors to the result.
        """
        if 'modules' not in self._cache:
            self._cache['modules'] = set(self.recorders() | self.archivers())
        
        return self._cache['modules']
    
    def recorders(self):
        """
        Returns a set containing all recorder modules used in this acquisition
        setup.
        """
        if 'recorders' not in self._cache:
            query = '/s:setup/s:use/@recorder'
            
            self._cache['recorders'] = set(self.setup.xpath(query, namespaces={
                's': self.NAMESPACE,
            }))
        
        return self._cache['recorders']
    
    def processors(self):
        """
        Returns a set of all processors used in this acquisition setup.
        @todo: Implement this
        """
        raise NotImplementedError()
    
    def archivers(self, stream=None):
        """
        Returns a set of all archivers used in this acquisition setup.
        If the stream ID is given, then select all archivers AND processors
        which receive this stream.
        """
        if stream:
            processor_ids = '/s:setup/s:connect[s:source/@target=\'%s\'][s:destination/@signal]/s:destination/@target' % stream
            processors = '/s:setup/s:instantiate[@as=%s]/@class' % processor_ids
            archivers = '/s:setup/s:connect[s:source/@target=\'%s\'][not(s:destination/@signal)]/s:destination/@target' % stream
            query = '%s | %s' % (processors, archivers)
            
            return set(self.setup.xpath(query, namespaces={
                's': self.NAMESPACE,
            }))
        
        if 'archivers' not in self._cache:
            query = '/s:setup/s:connect/s:destination[not(@signal)]/@target'
            self._cache['archivers'] = set(self.setup.xpath(query, namespaces={
                's': self.NAMESPACE,
            }))
            
        return self._cache['archivers']
    
    def streams(self, recorder=None, device=None):
        """
        Returns a set of all streams in this acquisiton setup, optionally
        filtered by recorder and device.
        """
        assert not device or recorder
        
        query = '/s:setup/s:use'
        
        if recorder:
            query += '[@recorder=\'%s\']' % recorder
            
            if device:
                query += '[@device=\'%s\']' % device
                
        uses = self.setup.xpath(query, namespaces={
            's': self.NAMESPACE,
        })
        
        return set((u.get('recorder'), u.get('device'), u.get('stream'), u.get('as')) for u in uses)
    
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


    #def devices(self, recorder=None):
    #    query = '/s:setup/s:use'
    #    
    #    if recorder:
    #        query += '[@recorder=\'%s\']' % recorder.routing_key
    #    
    #    uses = self.setup.xpath(query, namespaces={
    #        's': self.NAMESPACE,
    #    })
    #    uses = ((u.get('recorder'), u.get('device')) for u in uses)
    #    uses = set(uses)
    #    
    #    return tuple((IAddress(rec), device) for rec, device in uses)
    #
    
    
