# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Various utility functions to work with the SMAC modules.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


import inspect

from zope.interface import providedBy


def get_class(klass, module=None):
    """
    Returns the first found instance of C{klass} from the module C{module}
    or in the C{implementation} module if no module is passed as argument.
    
    @param klass: The class to search an instance for
    @type  klass: A C{class}
    
    @param module: The module containing the searched instance
    @type  module: A C{module}
    """
    if not module:
        import implementation as module
    
    try:
        issub = lambda v: inspect.isclass(v) and issubclass(v, klass)
        return inspect.getmembers(module, issub)[0][1]
    except IndexError:
        return None


def get_module_for_interface(interface):
    """
    Returns the thrift processor class for the given interface. This allows to
    retrieve the Processor of a defined handler on runtime by introspecting
    his interface.
    
    @param interface: The interface for which to retrieve the C{Processor}
    @type  interface: A C{zope.interface.Interface} class
    """
    return __import__(interface.__module__, fromlist=['Processor', 'Client'], level=0)


def get_interface_from_instance(instance, predicate=None):
    """
    Returns the interface name of the given instance by looking at the
    implemented interfaces.
    
    A note of care should be taken with modules which implement more than one
    interface, as this function only takes account of the last implemented one.
    
    @todo: Add a filter on the modules to exclude interfaces outside of the
           C{smac.api} package, interfaces not named C{Iface} and located too
           deep in the modules structure.
    """
    
    interfaces = list(providedBy(instance))
    
    def namespace(interface):
        return interface.__module__.startswith('smac.api')
    
    def name(interface):
        return interface.__name__ == 'Iface'
    
    def count(interface):
        return len(interface.__module__.split('.')) == 4
    
    interfaces = filter(namespace, interfaces)
    interfaces = filter(name, interfaces)
    interfaces = filter(count, interfaces)
    
    if predicate:
        interfaces = filter(predicate, interfaces)
    
    if not interfaces:
        raise ValueError("No valid interfaces where found")
    
    return interfaces[0].__module__.rsplit('.', 1)[-1]


def get_implementation_from_instance(instance):
    """
    Returns the implementation name of the given instance simply by lookig at
    its class name.
    """
    return instance.__class__.__name__


def get_module_from_address(address):
    """
    Tries to guess the module by looking at the interface property of the
    given L{Address} instance.
    
    @raise ValueError: If the interface attribute is not set or if the module
                       cannot be imported.
    """
    i = address.interface
    
    if not i:
        raise ValueError('Can\'t guess module from a domain level address.')
    
    module = 'smac.api.{0}.{1}'.format(i.lower(), i.capitalize())
    
    try:
        return __import__(module, fromlist=['Processor', 'Client'], level=0)
    except ImportError:
        raise ValueError('Inexistent interface: {0}'.format(module))
    


