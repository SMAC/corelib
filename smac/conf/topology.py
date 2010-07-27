# Copyright (C) 2005-2009  MISG/ICTI/EIA-FR
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
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
}

queues = (
    queue('{namespace}.unicast.interface.{interface}', (
        binding('unicast', '{namespace}.{interface}'),
    )),
    queue('{namespace}.unicast.implementation.{interface}.{implementation}', (
        binding('unicast', '{namespace}.{interface}.{implementation}'),
    )),
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