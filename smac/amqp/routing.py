from collections import namedtuple
from smac.api.base.ttypes import ModuleAddress

class Address(namedtuple('Address', 'namespace, interface, implementation, instance_id, key')):
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
    
    #def __str__(self):
    #    return self.routing_key()

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