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
The global settings to use throughout the whole SMAC project. This module
defines constants and default settings parameters such as AMQP exchange names
and other system-level defined configuration values.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

import os

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

max_ping_interval = ping_interval * 1.5

stream_logs = True

additional_bindings = None