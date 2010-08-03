# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Runs a module.
The configuration is read from the settings.json file in the current
working directory or from the location specified by the --settings
parameter.
"""
"""
@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


import os
import sys
import inspect

from twisted.python import usage, runtime
from zope.interface import implements, implementedBy

from smac.core.management import ICommand, BaseOptions
from smac import conf
from smac.api.base import AMQPService, RPCService


startup_registry = {
    '__name__': __name__
}

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
        
        def amqp_service(interface):
            return interface.extends(AMQPService.Iface)
        
        def rpc_service(interface):
            return interface.extends(RPCService.Iface)
        
        amqp_interface = filter(amqp_service, list(implementedBy(handler)))[0]
        amqp_processor = utils.get_module_for_interface(amqp_interface)
        
        try:
            rpc_interface = filter(rpc_service, list(implementedBy(handler)))[0]
        except IndexError:
            pass
        else:
            rpc_processor = utils.get_module_for_interface(rpc_interface)
            startup_registry['rpc_processor'] = rpc_processor
        
        # Save the necessary variables in the global registry to be used by
        # the runner called by twisted.runApp()
        startup_registry['amqp_processor'] = amqp_processor
        startup_registry['handler'] = handler
        startup_registry['instance_id'] = id
        startup_registry['__name__'] = '__main__'
        
        runner = os.path.join(os.path.dirname(base.__file__), 'runner.py')
        
        # Initialize basic configuration of the twisted application runner
        # @TODO: Move this to the `smac run` command
        from twisted.scripts import twistd
        
        config = twistd.ServerOptions()
        options = ['-noy', runner]
        if runtime.platformType != "win32":
            options.append('--pidfile={0}.pid'.format(id))
        config.parseOptions(options)
        
        # Set the terminal title
        print "\x1b]2;SMAC Module - {0} {1}\x07".format(handler.__name__, id)
        
        print "Initialization succeded, passing control to twistd\n"
        
        # Run the selected module
        twistd.runApp(config)
    

