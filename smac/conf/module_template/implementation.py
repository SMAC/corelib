# Copyright (C) <copyright_years> <copyright_holder>.
# See <license_filename> for details.

"""
Implementation and support classes, methods and functions for the
{interface_capitalized} SMAC module interface.

@author: <author_name> <<author_email>>
@organization: <organization_name> <<organization_website>>
@copyright: <copyright_years> <copyright_holder>
@license: <license_type>
"""

from zope.interface import implements

from twisted.python import log

from smac.api.{interface_lower}.{interface_capitalized} import Iface
from smac.api.{interface_lower}.ttypes import *
from smac.modules import base
from smac.util.hooks import register

class {implementation}(base.ModuleBase):
    """
    A SMAC module implementing the {interface_capitalized} interface.
    """
    
    implements(Iface)
    
    def __init__(self, *args, **kwargs):
        """
        Initialize a new {implementation} object.
        
        I have always to call the initialization method of my parent class.
        """
        super({implementation}, self).__init__(*args, **kwargs)
        
        log.msg("Initializing module")
    
    @register('pre_startup')
    def pre_startup_tasks(self):
        """
        I'm executed before the dispatcher connects to the AMQP message broker
        and sets up the exchanges, queues and bindings for this module.
        
        It is possible to define as much decorated methods as needed.
        
        My name is not relevant, only the decorator is.
        """
        
        log.msg("Starting up module")
    
    @register('post_startup')
    def post_startup_tasks(self):
        """
        I'm executed after all the connections are in place and the module is
        ready to be run.
        
        It is possible to define as much decorated methods as needed.
        
        My name is not relevant, only the decorator is.
        """
        
        log.msg("Module ready")
    
    {methods}
    
{interface_lower} = {implementation}()
