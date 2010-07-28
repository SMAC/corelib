# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR.
# See LICENSE for details.

"""
Starts a new module.
A new directory containing the basic file structure to develop a new module is
created.
After the execution of this command and having 'cd' into the newly created
directory, it is possible to run the module using the 'smac run <id>' command.
"""
"""
@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2010 MISG/ICTI/EIA-FR
@license: GPLv3
"""

from twisted.python import usage
from zope.interface import implements, Attribute
from zope.interface.interface import Method
from smac.core.management import ICommand, BaseOptions
from smac import conf

import os, shutil

TEMPLATE_DIR = 'module_template'
INDENT = "    "

class Options(BaseOptions):
    longdesc = __doc__
    
    def parseArgs(self, interface, implementation):
        self['interface'] = interface.lower()
        self['implementation'] = implementation
    
    def postOptions(self):
        # Get the interface class
        module = "smac.api.{0}.{1}".format(self['interface'], self['interface'].capitalize())
        
        try:
            module = __import__(module, fromlist=['Iface'], level=0)
        except ImportError:
            print ""
            print "No such interface '{0}'.\n".format(self['interface'].capitalize())
            print "Run 'smac list_interfaces' to list all available interfaces\n"\
                  "on this platform.\n"
            raise usage.UsageError("Provide a valid interface")
        
        self['interface_class'] = getattr(module, 'Iface')

class Command(object):
    implements(ICommand)
    
    config = Options
    
    def execute(self, interface, interface_class, implementation):
        """
        @TODO: Check file and directory for existence, rollback in case of
               failure and general consistency increment.
        """
        
        # Get path to the template directory
        template = os.path.join(os.path.dirname(conf.__file__), TEMPLATE_DIR)
        
        # Begin substitution
        with open(os.path.join(template, 'method.py')) as f:
            method = f.read()
        
        # Create methods declarations
        methods = ""
        # Get only methods defined by the interface and not by its parents
        for item in interface_class.names():
            if isinstance(interface_class[item], Method):
                signature = interface_class[item].getSignatureString()
                
                if len(signature) > 2:
                    signature = '(self, {0}'.format(signature[1:])
                else:
                    signature = '(self)'
                
                methods += method.format(**{
                    'name': item,
                    'signature': signature,
                    'doc': interface_class[item].__doc__ or "\n    "
                })
        
        methods = "\n".join([INDENT + l for l in methods.split("\n")]).strip()
        
        # Begin substitution
        with open(os.path.join(template, 'implementation.py')) as f:
            impl = f.read().format(**{
                'interface_capitalized': interface.capitalize(),
                'interface_lower': interface,
                'implementation': implementation,
                'methods': methods,
            })
        
        # Copy template dir into place
        destination = './smac-' + implementation.lower()
        shutil.copytree(template, destination, ignore=lambda d, l: 'method.py')
        
        # Write changes to disk
        with open(os.path.join(destination, 'implementation.py'), 'w') as f:
            f.write(impl)



