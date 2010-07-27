from collections import namedtuple
from smac.api.ttypes import ModuleAddress
from zope.interface import Interface, implements
from twisted.python import components

class IAddress(Interface):
    pass

class Address(namedtuple('Address', 'namespace, interface, implementation, instance_id, key')):
    implements(IAddress)
    
    def distribution_label(self):
        return self.distribution()
    
    def distribution(self):
        if self.is_domain:
            return 'broadcast'
        
        if self.is_instance:
            return 'unicast'
        
        if self.is_service:
            return 'services'
    
    def chunks(self):
        return (self.namespace, self.interface, self.implementation,
                self.instance_id)
    
    def routing_key(self):
        return self.key or '.'.join((str(x) for x in self.chunks() if x is not None))
    
    def is_service(self):
        return self.key is not None
    
    def is_domain(self):
        return self.key is None and self.interface is None
    
    def is_interface(self):
        return self.key is None and self.interface is not None and self.implementation is None
    
    def is_implementation(self):
        return self.key is None and self.implementation is not None and self.instance_id is None
    
    def is_instance(self):
        return self.key is None and self.instance_id is not None
    
    def to_module_address(self):
        return ModuleAddress(
            ns=self.namespace,
            iface=self.interface,
            implementation=self.implementation,
            instance_id=self.instance_id
        )
    
    def __str__(self):
        return u'.'.join((c for c in self.chunks() if c))

default_address = Address(None, None, None, None, None)

def Address(namespace, interface=None, implementation=None, instance_id=None, key=None):
    return default_address._replace(**locals())

def from_module_address(module_address):
    return Address(
        module_address.ns,
        module_address.iface,
        module_address.implementation,
        module_address.instance_id
    )

Address.from_module_address = from_module_address

from smac.util.proxy import Proxy

class StrToAddress(Proxy):
    implements(IAddress)
    
    def __init__(self, original):
        chunks = original.split('.')
        
        if len(chunks) not in (3, 4):
            raise ValueError('Only complete addresses can be automatically converted from string: %s' % original)
        
        super(StrToAddress, self).__init__(Address(*chunks))
    
class ModAddrToAddress(Proxy):
    implements(IAddress)
    
    def __init__(self, original):
        super(ModAddrToAddress, self).__init__(Address(
            original.ns,
            original.iface,
            original.implementation,
            original.instance_id
        ))

components.registerAdapter(
    StrToAddress, 
    basestring, 
    IAddress)

components.registerAdapter(
    ModAddrToAddress, 
    ModuleAddress, 
    IAddress)

#class Address(object):
#    def __init__(self, namespace, interface=None, implementation=None, instance_id=None, key=None):
#        self._namespace = namespace
#        self._interface = interface
#        self._implementation = implementation
#        self._instance_id = instance_id
#        self._key = self.key
#    
#    @property
#    def namespace(self):
#        return self._namespace
#    
#    @property
#    def interface(self):
#        return self._interface
#    
#    @property
#    def implementation(self):
#        return self._implementation
#    
#    @property
#    def instance_id(self):
#        return self._instance_id
#    
#    @property
#    def key(self):
#        return self._key
#    
#    @property
#    def chunks(self):
#        return (self.namespace, self.interface, self.implementation,
#                self.instance_id)
#    
#    @property
#    def routing_key(self):
#        return self.key or '.'.join((str(x) for x in self.chunks() if x is not None))
#    
#    @property
#    def is_service(self):
#        return self.key is not None
#    
#    @property
#    def is_domain(self):
#        return self.key is None and self.interface is None
#    
#    @property
#    def is_interface(self):
#        return self.key is None and self.interface is not None and self.implementation is None
#    
#    @property
#    def is_implementation(self):
#        return self.key is None and self.implementation is not None and self.instance_id is None
#    
#    @property
#    def is_instance(self):
#        return self.key is None and self.instance_id is not None
#    
#    def to_module_address(self):
#        return ModuleAddress(
#            ns=self.namespace,
#            iface=self.interface,
#            implementation=self.implementation,
#            instance_id=self.instance_id
#        )
