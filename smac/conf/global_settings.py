# Copyright (C) 2005-2009  MISG/ICTI/EIA-FR.
# See LICENSE for details.

"""
The global settings to use throughout the whole SMAC project. This module
defines constants and default settings parameters such as AMQP exchange names
and other system-level defined configuration values.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

import os

reactor = 'default'

amqp = {
    "vhost": "/", 
    "host": "localhost", 
    "password": "guest", 
    "port": 5672, 
    "user": "guest",
    "namespace": 'smac',
    "spec": os.path.join(os.path.dirname(os.path.realpath(__file__)), 'specifications', 'amqp',
            'standard', 'amqp0-8.xml'),
}

rpc = {
    "run_server": False,
    "port": 9090,
}

ping_interval = 2

max_ping_interval = ping_interval * 3

stream_logs = True

additional_bindings = None