from twisted.web.client import getPage

from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from thrift.transport.TTransport import TTransportBase, TMemoryBuffer

from cStringIO import StringIO

class HTTPTransport(TTransportBase):
    """
    A write only transport which uses a callback on the client to notify that
    a response was received.
    
    @TODO: Add HTTP authentication (basic/digest)
    
    """
    
    def __init__(self, url, iprot_factory):
        self.client = None
        self.url = str(url)
        self._iprot_factory = iprot_factory
        self._buffer = StringIO()
    
    def isOpen(self):
        return not self._buffer.closed
        
    def close(self):
        self._buffer.close()
        
    def write(self, buf):
        self._buffer.write(buf)
        
    def flush(self):
        d = getPage(self.url, method='POST', postdata=self._buffer.getvalue())
        d.addCallbacks(self._handle, self._error)
        self._buffer = StringIO()
        
    def _handle(self, response):
        tr = TMemoryBuffer(response)
        
        iprot = self._iprot_factory.getProtocol(tr)
        fname, mtype, rseqid = iprot.readMessageBegin()
        
        method = getattr(self.client, 'recv_' + fname)
        method(iprot, mtype, rseqid)
        
    def _error(self, failure):
        print "Error!"
        return failure

class HTTPClientFactory(object):
    """
    A client factory used to build a client and the relative HTTP based
    transport layers, which guarantees that a client is usable as returned
    by the `getClient` method.
    
    A new client can be created by calling the factory this way:
    
        f = HTTPClientFactory()
        f.getClient(client_claass, public_url)
    
    """
    
    transport = HTTPTransport
    """
    The default transport class to use
    """
    
    def __init__(self, iprot_factory=None, oprot_factory=None):
        self._iprot_factory = iprot_factory or TBinaryProtocolFactory()
        self._oprot_factory = oprot_factory or TBinaryProtocolFactory()
        
    def getClient(self, client_class, url):
        """
        Returns a client of type `client_class` with the transport bound to
        the given url.
        """
        
        tr = self.transport(url, self._iprot_factory)
        cl = client_class(tr, self._oprot_factory)
        tr.client = cl
        
        return cl