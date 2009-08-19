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
Collection of classes and utilities to assure the whole AMQP connection
handling, including authentication, queue creation and so on.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

class Dispatcher(object):
    """
    The Dispatcher handles the AMQP connection, authentication and queues
    consuming. Each received message is redirected to the client created
    during the startup phase to be dispatched to the correct thrift service
    method.
    
    Basically this class is only a Facade pattern to a more complex calling
    sequence over different Twisted and txAMQP members.
    """
    
    def __init__(self, spec, delegate):
        """
        Istantiates a new Dispatcher to be subsequently used with an
        L{IModule} provider.
        
        @param spec: The version of the AMQP specification to be used.
        @type  spec: L{txamqp.spec.Spec}
        
        @param delegate: The 
        """