# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Programmatic definition of the AMQP topology to use overall the inter-module
communication.

It is possible to create exchanges and queues with the following syntax:
 - exchange(name, type)
 - queue(name, bindings, extra)

The bindings argument is a tuple of (name, routing_key) tuples.

Inside the all 'name' and 'routing_key' arguments, some string substitutions
took place:
 - {namespace} is replaced with the namespace of the system (usually 'smac')
 - {interface} is replaced with the actual interface of the module
 - {implementation} is replaced with the actual implementation of the module
 - {instance} is replaced with the actual id of the module instance

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

def exchange(name, type='direct'):
    return {
        'name': name,
        'type': type
    }

def queue(name, bindings, extra=None):
    if extra is None:
        extra = {}
    extra.update({
        'name': name,
        'bindings': bindings,
    })
    
    return extra

def binding(exchange, routing_key):
    return (exchange, routing_key)

exchanges = {
    'responses': exchange('amq.direct'),
    'unicast': exchange('{namespace}.unicast'),
    'broadcast': exchange('{namespace}.broadcast'),
    'services': exchange('{namespace}.services', 'topic'),
    'tasks': exchange('{namespace}.tasks', 'topic'),
    'transfers': exchange('{namespace}.transfers', 'direct'),
    'sessions': exchange('{namespace}.sessions', 'direct'),
}

queues = (
    queue('{namespace}.unicast.interface.{interface}', (
        binding('unicast', '{namespace}.{interface}'),
    ), extra={
        'auto_delete': True
    }),
    queue('{namespace}.unicast.implementation.{interface}.{implementation}', (
        binding('unicast', '{namespace}.{interface}.{implementation}'),
    ), extra={
        'auto_delete': True
    }),
    queue('', (
            binding('unicast', '{namespace}.{interface}.{implementation}.{instance}'),
            binding('broadcast', '{namespace}'),
            binding('broadcast', '{namespace}.{interface}'),
            binding('broadcast', '{namespace}.{interface}.{implementation}'),
        ), extra={
            'exclusive': True,
            'auto_delete': True
        }
    ),
)