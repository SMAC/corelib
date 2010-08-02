# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
The main package of the SMAC Core python library.
This package contains the full version of the actual release and a utility
class and method to access all of it's properties.

G{packagetree}

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

VERSION = "2.0.0.1"
"""
The full version of this release. The scheme represented by the version
number is defined as follows: I{C{major.minor.build.revision}}
For more information about the various build values look at the constants
defined by the L{Version} class.
"""

class Version(object):
    """
    A simple wrapper around the version string which allows programmatic
    access to every single property.
    """
    
    MAJOR, MINOR, BUILD, REVISION = range(4)
    """
    The meaning of the single numbers appearing in the full version number.
    
     * MAJOR: The major version number of the release
     * MINOR: The minor version number of the release
     * BUILD: The actual build number of the release
     * REVISION: The current revision number for the release
     
    @group: MAJOR, MINOR, BUILD, REVISION
    """
    
    DEVELOPMENT, ALPHA, BETA, CANDIDATE, PUBLIC = range(5)
    """
    The various build values.
    
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
    The string representation of the build statuses defined by the class.
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
        
        assert 0 <= self._scheme[Version.BUILD] < len(Version.BUILD_STRINGS), \
                'Invalid build ID'
    
    @property
    def major(self):
        """Major version number"""
        return self._scheme[Version.MAJOR]
    
    @property
    def minor(self):
        """Minor version number"""
        return self._scheme[Version.MINOR]
    
    @property
    def build(self):
        """Build ID (0 to 4)"""
        return self._scheme[Version.BUILD]
    
    @property
    def revision(self):
        """Revision number"""
        return self._scheme[Version.REVISION]
    
    @property
    def build_string(self):
        """Long build string representation"""
        return Version.BUILD_STRINGS[self._scheme[Version.BUILD]][1]
    
    @property
    def build_abbr(self):
        """Short build string representation"""
        return Version.BUILD_STRINGS[self._scheme[Version.BUILD]][0]
    
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