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
A collection of configuration management utilities to be used all over the
SMAC project.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

import json
from os.path import realpath, join, dirname

class Settings(object):
    """
    A lightweight wrapper around the built-in JSON encoder. Provides means to
    load from and write to a configuration file by using different sources.
    
    @group loaders: from_*
    @group writers: to_*
    """
    
    @classmethod
    def from_stream(cls, stream, load_globals=True):
        """
        Creates and returns a new Settings object by loading the configuration
        from the stream parameter.
        
        @param stream: A JSON formatted stream containing the data do decode.
        @type  stream: C{.read()}-supporting file-like object
        
        @param load_globals: Flag to set if the method automatically load the
                             system wide configuration too.
        @type  load_globals: C{boolean}
        
        @return: The newly created C{Settings} object.
        @rtype:  a L{Settings} instance
        """
        settings = json.load(stream, object_hook=Settings) or Settings()
        
        if load_globals:
            settings.load_globals()
        
        return settings
        
    @classmethod
    def from_file(cls, pathname, load_globals=True):
        """
        Creates and returns a new Settings object by loading the configuration
        from the file at the given location.
        
        @param pathname: A pathname to a file containing the JSON formatted
                         data to load.
        @type  pathname: C{string}.
        
        @param load_globals: Flag to set if the method automatically load the
                             system wide configuration too.
        @param load_globals: C{boolean}.

        @return: The newly created C{Settings} object.
        @rtype:  a A L{Settings} instance.
        """
        return cls.from_stream(open(pathname), load_globals)
    
    @classmethod
    def from_dict(cls, dictionary, load_globals=True):
        """
        This method is the same as L{__init__} and is provided for
        coherence with the other from_* methods.
        
        @param load_globals: Flag to set if the method automatically load the
                             system wide configuration too.
        @param load_globals: C{boolean}.
        
        @see: L{__init__} for further details.
        """
        settings = Settings(dictionary)
        
        if load_globals:
            settings.load_globals()

        return settings
        
    @classmethod
    def from_string(cls, string, load_globals=True):
        """
        Creates and returns a new Settings object by decoding the JSON
        formatted string passed as an argument.
        
        @param string: A JSON encoded string.
        @type  string: A C{string}.
        
        @param load_globals: Flag to set if the method automatically load the
                             system wide configuration too.
        @param load_globals: C{boolean}.
        
        @return: The newly created C{Settings} object.
        @rtype:  A L{Settings} instance.
        """
        settings = json.loads(string, object_hook=Settings) or Settings()
            
        if load_globals:
            settings.load_globals()
            
        return settings
    
    def __init__(self, dictionary={}):
        """
        Creates and returns a new Settings object by loading the configuration
        from the given dictionary object.
        
        @see: L{from_dict}
        
        @attention: No additional type checking is done by the class over the
                    dictionary argument, the caller must ensure that all
                    objects are correctly serializable by the json encoder if
                    he intends to save the configuration to a file.
        
        @param dictionary: A dictionary containing the configuration values.
        @type  dictionary: A C{dict} object.
        """
        def val(value):
            if isinstance(value, dict):
                value = Settings(value)
            
            return value
        
        # Map the dictionary to a Settings instance
        self.__dict__ = dict((k, val(v)) for k, v in dictionary.iteritems())
        
        self._base = None
    
    def get_base(self):
        """
        Returns the original configuration dictionary as defined in the
        global_settings module.
        
        This method can be called by all child dictionary entries to retrieve
        only the original value of the current level.
        E.g. the overwritten directive C{user} of the dictionary C{amqp} can
        be retrieved by calling C{settings_instance.get_base().amqp.user} or
        C{settings_instance.amqp.get_base().user}. Either one produce the same
        result.
        
        @attention: This method does not return the original value of a
                    given directive but his parent dictionary.
        
        @return: The setting instance of the original configuration.
        @rtype:  A L{Settings} instance
        """
        
        return self._base or Settings()
    
    def load_globals(self, global_settings=None):
        """
        Loads the SMAC globals and default configuration values as defined in
        the L{global_settings} module.
        If the load_globals method has already been called it simply returns,
        is it thus safe to call the method more than one time to ensure that
        the default configuration is loaded.
        """
        if self._base:
            return
        
        if not global_settings:
            import smac.conf.global_settings as sett
            
            valid = (s for s in dir(sett) if not s.startswith(('_', '.')))
            global_settings = Settings(dict((s, getattr(sett, s)) for s in valid))
        
        self._base = global_settings
        
        for k, v in self.__dict__.iteritems():
            if isinstance(v, Settings) and hasattr(self._base, k) and not k.startswith('_'):
                v.load_globals(getattr(self._base, k))
    
    def __getattr__(self, name):
        """
        Gets the requested configuration directive from the global
        configuration if loaded.
        
        @raise AttributeError: If the configuration directive does not exist
                               either in the local or in the global config or
                               if the global was not loaded.
        """
        try:
            if name.startswith('_'):
                return self.__dict__[name]
            return getattr(self._base, name)
        except (KeyError, AttributeError):
            raise AttributeError("'%s' configuration directive not defined" % name)
    
    def to_dict(self):
        """
        Maps the Settings instance to a dictionary and returns it.
        
        @return: A C{dict} instance containing all serialized items.
        @rtype:  A C{dict} instance.
        """
        def val(value):
            if isinstance(value, Settings):
                value = value.to_dict()
            
            return value
        
        return dict((k, val(v)) for k, v in self.__dict__.iteritems() \
            if not k.startswith('_'))
    
    def to_stream(self, stream, indent=4):
        """
        Writes a JSON encoded version of the Settings instance to the given
        stream.
        
        @param stream: The stream to write the JSON encoded data to.
        @type  stream: Any C{.write()}-supporting file-like object.
        
        @param indent: The number of spaces to use to indent the output.
        @type  indent: C{int} or C{None}
        
        @see: the U{python json
              module<http://docs.python.org/library/json.html#basic-usage>}
              documentation for further information about the indent level.
        """
        json.dump(self.to_dict(), stream, indent=indent)
    
    def to_file(self, pathname, indent=4):
        """
        Writes a JSON encoded version of the Settings instance to the file
        at the location identified by the given pathname.
        
        @param pathname: The pathname of the file to write the JSON encoded
                         data to.
        @type  pathname: A C{string}
        
        @param indent: The number of spaces to use to indent the output.
        @type  indent: C{int} or C{None}
        
        @see: the U{python json
              module<http://docs.python.org/library/json.html#basic-usage>}
              documentation for further information about the indent level.
        """
        f = open(pathname, 'w')
        self.to_stream(f, indent)
    
    def to_string(self, indent=4):
        """
        Returns a JSON encoded version of the Settings instance as a string.
        
        @param indent: The number of spaces to use to indent the output.
        @type  indent: C{int} or C{None}
        
        @return: A JSON encoded string representing the Settings instance.
        @rtype:  C{string}
        
        @see: the U{python json
              module<http://docs.python.org/library/json.html#basic-usage>}
              documentation for further information about the indent level.
        """
        return json.dumps(self.to_dict(), indent)
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return repr(self.__dict__)

