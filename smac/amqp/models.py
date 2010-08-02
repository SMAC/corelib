# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Object oriented view of various AMQP models such as exchanges or queues.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

from twisted.internet import defer
from twisted.python import components
from zope.interface import Interface, Attribute, implements

from smac.api.ttypes import ModuleAddress
from smac.python import log
from smac.conf import settings


class Exchange(object):
    """
    Object oriented view of an exchange which can either be used as a wrapper
    around its name and type or, when declared, bound to a channel and serve
    as API for exchange operations on the message broker.
    """
    
    def __init__(self, channel, name, type='direct'):
        """
        Creates a new exchange with the given name and type.
        
        C{type} can be one of the built-in AMQP types (such as 'direct',
        'topic', 'fanout', 'headers') or another vendor-specific type as
        supported by the message broker in use.
        """
        self.name = name
        self.original = name
        self.type = type
        self.channel = channel
        
        self.declared = name.split('.', 1)[0] == 'amq'
    
    def __str__(self):
        return self.name
    
    def __copy__(self):
        e = Exchange(self.name, self.type)
        e.original = self.original
        return e
    
    def format_name(self, *args, **kwargs):
        """
        Utility method to format the name with the given arguments. Simple
        wrapper around C{str.format} which reassigns the new value of the
        name.
        """
        self.name = self.original.format(*args, **kwargs)
        
        self.declared = self.name.split('.', 1)[0] == 'amq'
    
    @defer.inlineCallbacks
    def declare(self):
        """
        Declares the exchange on the AMQP message broker using the given
        channel and saving its instance for further use.
        
        @precondition: C{channel} shall already be open.
        
        @return: A deferred which will be fired upon exchange declaration.
        """
        
        if self.declared:
            return
        
        log.debug("Declaring {0} exchange with name '{1}'".format(
                self.type, self.name))
        yield self.channel.exchange_declare(exchange=self.name,
                type=self.type)
        self.declared = True
    


class Queue(object):
    """
    Object oriented view of a queue which can either be used as a wrapper
    around its name or, when declared, bound to a channel and serve as API for
    queue operations on the message broker.
    """
    
    def __init__(self, channel, name='', exclusive=False, auto_delete=False, **extra):
        """
        Creates a new queue with the given name and properties.
        
        The C{name} can be empty to let the message broker choose a unique
        name for this queue. Upon successfull declaration this value will be
        populated with the generated name.
        
        The extra arguments can be C{exclusive}, C{auto_delete} or any
        attribute supported by the broker in use.
        """
        self.name = name
        self.original = name
        self.extra = {}
        self.declared = False
        self.channel = channel
        
        if exclusive:
            self.extra['exclusive'] = True
        
        if auto_delete:
            self.extra['auto_delete'] = True
            
        self.declaring_lock = defer.DeferredLock()
        
        self.extra.update(extra) # Doing an update will copy the values to the
                                 # new dictionary and avoid indirect external
                                 # modifications
    
    def __str__(self):
        return self.name
    
    def format_name(self, *args, **kwargs):
        """
        Utility method to format the name with the given arguments. Simple
        wrapper around C{str.format} which reassigns the new value of the
        name.
        """
        self.name = self.original.format(*args, **kwargs)
    
    @defer.inlineCallbacks
    def declare(self):
        """
        Declares the queue on the AMQP message broker using the given channel
        and saving its instance for further use.
        If the queue is an anonymous queue, then the name property will be
        populated with the server-generated one.
        
        @precondition: C{channel} shall already be open.
        
        @return: A deferred which will be fired upon queue declaration.
        """
        
        yield self.declaring_lock.acquire()
        
        try:
            if self.declared:
                return
        
            if self.name:
                log.debug("Declaring named queue '{0}'".format(self.name))
            else:
                log.debug("Declaring anonymous queue")
        
            queue = yield self.channel.queue_declare(queue=self.name, **self.extra)
            self.name = queue.queue
            self.declared = True
            defer.returnValue(None)
        finally:
            self.declaring_lock.release()
    
    @defer.inlineCallbacks
    def bind(self, exchange, routing_key=None):
        """
        Binds the queue instance with the given exchange and using the
        supplied C{routing_key} (if present).
        
        @precondition: This queue instance shall already be declared (and the
                       channel attribute set).
        
        @return: A deferred which will be fired upon queue binding.
        """
        
        yield self.declare()
        yield exchange.declare()
        
        if routing_key is None:
            routing_key = self.name
        
        log.debug("Binding '{0}' to '{1}' with routing key '{2}'".format(
                self.name, exchange.name, routing_key))
        
        yield self.channel.queue_bind(queue=self.name, exchange=exchange.name,
                routing_key=routing_key)
    
    @defer.inlineCallbacks
    def consume(self):
        """
        Start consuming messages on the queue instance.
        
        @precondition: This queue instance shall already be declared (and the
                       channel attribute set).
        
        @return: A deferred which will be fired upon reply reception, holding
                 the returned consumer_tag as result.
        """
        yield self.declare()
        reply = yield self.channel.basic_consume(queue=self.name)
        defer.returnValue(reply.consumer_tag)
    


class IAddress(Interface):
    """
    Interface used to automatically adapt various objects (such as thrift
    types) to the internal used address format.
    """
    namespace = Attribute("""Namespace for the whole system.""")
    interface = Attribute("""Interface implemented by the targeted module.""")
    implementation = Attribute("""Interface specific implementation of the targeted module.""")
    instance = Attribute("""Instance identifier of the targeted module.""")
    routing_key = Attribute("""Routing key of the targeted module or service""")


class Address(object):
    implements(IAddress)
    
    labels = ('namespace', 'interface', 'implementation', 'instance', 'routing_key')
    
    def __init__(self, interface=None, implementation=None,
            instance=None, routing_key=None, namespace=None):
        self.namespace = namespace or settings.amqp.namespace
        self.interface = interface
        self.implementation = implementation
        self.instance = instance
        self._routing_key = routing_key
    
    def __hash__(self):
        return self.routing_key.__hash__()
    
    def __eq__(self, other):
        return self._routing_key == other._routing_key and self.chunks == other.chunks
    
    def __iter__(self):
        return (i for i in zip(self.labels, self.chunks + (self.routing_key,)))
    
    def __str__(self):
        return self.routing_key
    
    def __repr__(self):
        return "<smac.amqp.models.Address('{0}', '{1}', '{2}', '{3}', routing_key='{rt}')>".format(
            *self.chunks, rt=self._routing_key or ''
        )
    
    @property
    def routing_key(self):
        return self._routing_key or '.'.join(map(str, filter(None, self.chunks)))
    
    @property
    def distribution(self):
        if self.isdomain:
            return 'broadcast'
        
        if self.isinstance:
            return 'unicast'
        
        if self.isservice:
            return 'services'
    
    @property
    def isservice(self):
        return bool(self._routing_key)
    
    @property
    def isdomain(self):
        return all((not self.isservice, not self.interface))
    
    @property
    def isinterface(self):
        return all((not self.isservice, self.interface, not self.implementation))
    
    @property
    def isimplementation(self):
        return all((not self.isservice, self.implementation, not self.instance))
    
    @property
    def isinstance(self):
        return all((not self.isservice, self.instance))
    
    @property
    def chunks(self):
        return (
            self.namespace,
            self.interface,
            self.implementation,
            self.instance
        )
    
    @classmethod
    def from_string(cls, original):
        chunks = original.split('.')
        
        if len(chunks) not in (3, 4):
            raise ValueError('Only complete addresses can be automatically " \
                    "converted from string: {0}'.format(original))
        
        return cls(**dict(zip(cls.labels, chunks)))
    
    @classmethod
    def from_moduleaddress(cls, original):
        return cls(
            original.iface,
            original.implementation,
            original.instance_id,
            original.ns
        )
    
    def to_moduleaddress(self):
        return ModuleAddress(*self.chunks)
    

components.registerAdapter(Address.from_string, basestring, IAddress)
components.registerAdapter(Address.from_moduleaddress, ModuleAddress, IAddress)

