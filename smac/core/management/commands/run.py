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
Runs a module.
The configuration is read from the settings.json file in the current
working directory or from the location specified by the --settings
parameter.
"""
"""
@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

from twisted.python import usage
from zope.interface import implements
from smac.core.management import ICommand
from smac.conf import Settings
from smac.modules import get_class_instance, base

import os
import sys

class Options(usage.Options):
    longdesc = __doc__
    
    optParameters = [
        ['settings', None, None, "The pathname to the module settings file"],
    ]
    
    def postOptions(self):
        if self['settings'] is None:    
            self['settings'] = os.path.join(os.getcwd(), 'settings.json')
        
        self['settings'] = os.path.realpath(self['settings'])
        
        if os.path.isdir(self['settings']):
            self['settings'] = os.path.join(self['settings'], 'settings.json')
        
        if not os.path.isfile(self['settings']):
            print ""
            print "Settings file not found. Please provide the --settings", \
                  "parameter or make shure a 'settings.json' file is", \
                  "present in the current working directory.\n"
            raise usage.UsageError("Provide a valid path to a settings file")

class Command(object):
    implements(ICommand)
    
    config = Options
    
    def execute(self, settings):
        print "Starting module from %s" % settings
        
        s = Settings.from_file(settings)
        
        sys.path.insert(0, os.path.dirname(settings))
        
        # The module should now be on the path, let's search for it
        instance = get_class_instance(base.ModuleBase)
        
        print "Running: ", instance
        
        
        
