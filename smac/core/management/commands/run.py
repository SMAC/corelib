# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
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
@copyright: 2005-2010 MISG/ICTI/EIA-FR
@license: GPLv3
"""


import os
import sys
import inspect

from twisted.python import usage
from zope.interface import implements, implementedBy

from smac.core.management import ICommand, BaseOptions
from smac import conf


startup_registry = {}

class Options(BaseOptions):
    longdesc = __doc__
    
    optParameters = [
        ['settings', None, None, "The pathname to the module settings file"],
    ]
    
    def parseArgs(self, ID):
        self['id'] = ID
    
    def postOptions(self):
        if self['settings'] is None:    
            self['settings'] = os.path.join(os.getcwd(), 'settings.json')
        
        self['settings'] = os.path.realpath(self['settings'])
        
        if os.path.isdir(self['settings']):
            self['settings'] = os.path.join(self['settings'], 'settings.json')
        
        if not os.path.isfile(self['settings']):
            print ""
            print "Settings file not found. Please provide the --settings", \
                  "parameter or make sure a 'settings.json' file is", \
                  "present in the current working directory.\n"
            raise usage.UsageError("Provide a valid path to a settings file")
            
        # Change the working directory to the module directory. This allows for
        # relative file references from the module code/configuration.
        os.chdir(os.path.dirname(self['settings']))

class Command(object):
    implements(ICommand)
    
    config = Options
    
    def execute(self, settings, id):
        print "Starting module from {0} with ID {1}".format(settings, id)
        
        conf.settings = conf.Settings.from_file(settings)
        
        # @todo: Install the chosen reactor (look at settings.reactor)
        #from twisted.internet import reactor
        from twisted.internet.selectreactor import install
        reactor = install()
        
        sys.path.insert(0, os.path.dirname(settings))
        
        # The module should now be on the path, let's search for it.
        from smac.modules import base, utils
        
        try:
            # The get_class_instance function loads the 'implementation'
            # module by default. Search for an instance of base.ModuleBase
            # in the 'implementation' module.
            # The 'implementation module should be defined by the SMAC module
            # and thus contained in the directory which we just inserted in
            # the path.
            handler = utils.get_class(base.ModuleBase)
        except ImportError:
            print "The 'implementation' python module was not found."
            sys.exit(1)
            
        if handler is None:
            print "No instances of 'smac.modules.base.ModuleBase' were ", \
                  "found in the 'implementation' python module."
            sys.exit(1)
        
        interface = list(implementedBy(handler))[0]
        processor = utils.get_module_for_interface(interface)
        runner = os.path.join(os.path.dirname(base.__file__), 'runner.py')
        
        # Save the necessary variables in the global registry to be used by
        # the runner called by twisted.runApp()
        startup_registry['processor'] = processor
        startup_registry['handler'] = handler
        startup_registry['instance_id'] = id
        
        # Initialize basic configuration of the twisted application runner
        # @TODO: Move this to the `smac run` command
        from twisted.scripts import twistd
        
        config = twistd.ServerOptions()
        config.parseOptions(['--pidfile={0}.pid'.format(id), '-noy', runner])
        
        # Set the terminal title
        print "\x1b]2;SMAC Module - {0} {1}\x07".format(handler.__name__, id)
        
        print "Initialization succeded, passing control to twistd\n"
        
        # Run the selected module
        twistd.runApp(config)
    

