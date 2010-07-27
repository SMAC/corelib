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
The interface which each module implementation has to implement (oug, no?
really? ;-) to be recognized as a SMAC Module.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

from zope.interface import Interface, Attribute

class IModule(Interface):
    channel = Attribute("""The actual AMQP client object used for the data
                           communication with the AMQ broker.
                           This attribute allows the reuse of the actual
                           connection.
                           The attribute is setted by the AMQ Client factory
                           responsible for the setup of the connection.
                           @type: A L{txamqp.protocol.AMQChannel} instance.
                           """)
    
    def set_identifier(id):
        """
        Called by the runner to assign the module id to the instance.
        
        @param id: The implementation-wide unique-ID of this instance.
        @type  id: C{int}.
        """