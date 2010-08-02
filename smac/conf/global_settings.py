# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR.
# See LICENSE for details.

"""
The global settings to use throughout the whole SMAC project. This module
defines constants and default settings parameters such as AMQP exchange names
and other system-level defined configuration values.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

import os

reactor = 'default'

amqp = {
    "vhost": "/", 
    "host": "localhost", 
    "password": "guest", 
    "port": 5672, 
    "user": "guest",
    "channel": 1,
    "namespace": 'smac',
    "spec": os.path.join(os.path.dirname(os.path.realpath(__file__)), 'specifications', 'amqp',
            'standard', 'amqp0-8.xml'),
}

rpc = {
    "port": 9090,
}

ping_interval = 3

max_ping_interval = 5 #ping_interval * 3

stream_logs = True

additional_bindings = None