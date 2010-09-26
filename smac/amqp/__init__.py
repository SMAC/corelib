# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Collection of AMQP utilities such as connectors, interfaces, factories and 
adapters to be used throughout the whole SMAC core library.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


_client_factory = None
_server_factory = None
_delegate = None


def build_client(*args, **kwargs):
    global _client_factory
    return _client_factory.build_client(*args, **kwargs)


def build_server(address, processor, handler, queues=None, delegate=None):
    global _server_factory
    global _delegate
    
    if delegate is None:
        delegate = _delegate
    
    return _server_factory.build_server(delegate, processor, handler, address, queues)


__all__ = ('build_client', 'build_server')