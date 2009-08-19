#!/usr/bin/python

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
A simple cleanup python script which removes:

 * All thrift generated files from smac/api
 * All sphinx builds from docs/_build
 * All epydoc builds from docs/_api
 * All thrift docs from docs/_thrift

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
@organization: EIA-FR <http://www.eia-fr.ch>
@copyright: 2005-2009 MISG/ICTI/EIA-FR
@license: GPLv3
"""
import os
import sys

def empty_dir(path_to_dir, exclude=()):
    excluded = map(lambda f: os.path.join(path_to_dir, f), exclude)
    
    for root, dirs, files in os.walk(path_to_dir, topdown=False):
        for name in files:
            f = os.path.join(root, name)
            
            if f in excluded:
                continue
                
            os.remove(f)
        
        for name in dirs:
            f = os.path.join(root, name)
            
            if f in excluded:
                continue
            
            os.rmdir(f)

if __name__ == '__main__':
    print ""
    print "CAUTION: This script will remove various files from the project."
    print "If it is misplaced it's possible that other files are removed too."
    print ""
    
    response = raw_input("Continue execution [N/y]? ")
    
    if not response.lower().startswith('y'):
        print "Cancelling execution"
        print ""
        sys.exit(0)
    
    basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    
    apidir = os.path.join(basedir, 'smac', 'api')
    empty_dir(apidir)
    
    sphinxdir = os.path.join(basedir, 'docs', '_build')
    empty_dir(sphinxdir)
    
    epydocdir = os.path.join(basedir, 'docs', '_api')
    empty_dir(epydocdir)
    
    thriftdir = os.path.join(basedir, 'docs', '_thrift')
    empty_dir(thriftdir)
    
    
    