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
The main package of the SMAC Core python library.
This package contains the full version of the actual release and a utility
class and method to access all of it's properties.

G{packagetree}

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""

VERSION = "2.0.0.1"
"""The full version of this release. The scheme represented by the version
number is defined as follows: I{C{major.minor.build.revision}}
For more information about the various build values look at the constants
defined by the L{Version} class."""

class Version(object):
    """
    A simple wrapper around the version string which allows programmatic
    access to every single property.
    """
    
    DEVELOPMENT, ALPHA, BETA, CANDIDATE, PUBLIC = range(5)
    """The various build values.
    
     * DEVELOPMENT: Release intended for developers of the project
     * ALPHA: Release targeted to developers testing
     * BETA: Release targeted to community testing
     * CANDIDATE: Release candidate, soon to be released as public
     * PUBLIC: Stable public release targeted to deployment environments
     
     @group: DEVELOPMENT, ALPHA, BETA, CANDIDATE, PUBLIC
    """
    
    BUILD_STRINGS = (
        ('dev', 'development'),
        ('a', 'alpha'),
        ('b', 'beta'),
        ('rc', 'release candidate'),
        ('', 'public release'),
    )
    """
    The string representation of the build status defined by the class.
    """
    
    def __init__(self, version):
        """
        Parses the version string passed as argument.
        
        @param version: The version string to parse
        @type  version: C{string}
        """
        
        self.version = version
        
        self._scheme = map(int, version.split('.'))
        
        assert len(self._scheme) == 4, 'Invalid scheme'
        
        assert 0 <= self._scheme[2] < 5, 'Invalid build ID'
    
    @property
    def major(self):
        """Major version number"""
        return self._scheme[0]
    
    @property
    def minor(self):
        """Minor version number"""
        return self._scheme[1]
    
    @property
    def build(self):
        """Build ID (0 to 4)"""
        return self._scheme[2]
    
    @property
    def revision(self):
        """Revision number"""
        return self._scheme[3]
    
    @property
    def build_string(self):
        """Long build string representation"""
        return Version.BUILD_STRINGS[self._scheme[2]][1]
    
    @property
    def build_abbr(self):
        """Short build string representation"""
        return Version.BUILD_STRINGS[self._scheme[2]][0]
    
    def __str__(self):
        """Prints the original version string"""
        return self.version
    
    def __repr__(self):
        print 'Version(%d, %d, %d, %d)' % tuple(self._scheme)

def get_version():
    """
    Returns an instance of the L{Version} class which carries the actual
    version of the SMAC Core library
    
    @return: The current version of the library.
    @rtype:  A L{Version} instance.
    """
    
    return Version(VERSION)