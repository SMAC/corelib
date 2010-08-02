# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
The main command line interface to all SMAC development and deployment
utilities.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

COMMANDS_PKG = 'smac.core.management.commands'

import smac.core.management.commands
from smac.core.management import BaseOptions

from twisted.python import usage, reflect

import os.path
import sys

def find_commands(command_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    
    This function was borrowed from Django (http://djangoproject.com)
    """
    try:
        return [f[:-3] for f in os.listdir(command_dir)
                if not f.startswith(('_', '.')) and f.endswith('.py')]
    except OSError:
        return []
    
def load_command_class(command_name):
    """
    Given a command name returns the Command class.
    """
    return reflect.namedAny('%s.%s.Command' % (COMMANDS_PKG, command_name))
    
def create_subcommands_definition():
    """
    Loads all the C{twisted.python.usage.Option} subclasses contained in the
    C{commands} package and creates the list to be used in the main command
    line parser configuration.
    """
    directory = os.path.dirname(smac.core.management.commands.__file__)
    commands = find_commands(directory)
    classes =  [(c, load_command_class(c)) for c in commands]
    definition = [(c[0], None, c[1].config, c[1].__doc__) for c in classes]
    
    return definition

class Options(BaseOptions):
    """
    Main command line parser configuration class.
    """
    
    subCommands = create_subcommands_definition()
    
    def postOptions(self):
        if not self.subCommand:
            self.opt_help()
    
    def opt_version(self):
        import smac
        print "SMAC core version: %s" % smac.get_version()
        sys.exit(0)

def run(args=None):
    """
    Runs the command specified by the arguments in the args tuple or given at
    the command line.
    
    @param args: The arguments to parse to run the command.
    @type  args: A C{Tuple} of strings.
    """
    
    if args is None:
        args = sys.argv[1:]
        
    config = Options()
    
    try:
        config.parseOptions(args)
    except usage.UsageError as errortext:
        cmd = sys.argv[0]
        help = "--help"
    
        if config.subCommand:
            cmd += " %s" % config.subCommand
            help = "%s %s" % (config.subCommand, help)
    
        print '%s: %s' % (cmd, errortext)
        print "%s: Try 'smac %s' for usage details.\n" % (cmd, help)
        sys.exit(1)

    load_command_class(config.subCommand)().execute(**config.subOptions)