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
An interface to the thrift, sphinx and epydoc command line utilities with
settings already adapted to the project to generate the following files:

 * Sphinx HTML documentation
 * Sphinx PDF documentation
 * Epydoc HTML documentation
 * Epydoc PDF documentation
 * Thrift HTML documentation
 * Thrift python code

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
    if len(sys.argv) < 2:
        print "Usage:"
        print "%s all" % sys.argv[0]
        print "%s [sphinxhtml] [sphinxpdf] [epydochtml] [epydocpdf] [thrifthtml] [thriftpython] [thriftdjango]" % sys.argv[0]
        sys.exit(1)
    
    args = sys.argv[1:]
    runall = 'all' in args
    
    basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.environ['PYTHONPATH'] = "%s:%s" % (basedir, os.environ.get('PYTHONPATH', ''))
    
    if runall or 'thriftpython' in args:
        os.system('thrift --gen py:new_style,twisted -r -o "%s" "%s"' % (os.path.join(basedir, 'smac'), os.path.join(basedir, 'smac', 'conf', 'specifications', 'api', 'all.thrift')))
        empty_dir(os.path.join(basedir, 'smac', 'api'))
        os.rename(os.path.join(basedir, 'smac', 'gen-py', 'smac', 'api'), os.path.join(basedir, 'smac', 'api'))
        empty_dir(os.path.join(basedir, 'smac', 'gen-py'))
        os.rmdir(os.path.join(basedir, 'smac', 'gen-py'))
    
    if runall or 'epydochtml' in args:
        empty_dir(os.path.join(basedir, 'docs', '_api'))
        os.system("epydoc --html -o \"%s/docs/_api\" --name \"SMAC Core library\" --url http://smac.webhop.org --graph all --inheritance grouped -v smac" % basedir)
    
    if runall or 'epydocpdf' in args:
        os.system("epydoc --pdf -o \"%s/docs/_api\" --name \"SMAC Core library\" --url http://smac.webhop.org --graph classtree --inheritance grouped -v smac" % basedir)
    
    if runall or 'sphinxhtml' in args:
        os.chdir(os.path.join(basedir, 'docs'))
        empty_dir(os.path.join(basedir, 'docs', '_build', 'html'))
        os.system('make html')
        
    if runall or 'sphinxpdf' in args:
        os.chdir(os.path.join(basedir, 'docs'))
        empty_dir(os.path.join(basedir, 'docs', '_build', 'latex'))
        os.system('make latex')
        
        os.chdir(os.path.join(basedir, 'docs', '_build', 'latex'))
        os.system('make all-pdf')
    
    if runall or 'thrifthtml' in args:
        os.system('thrift --gen html -r -o "%s" "%s"' % (os.path.join(basedir, 'docs'), os.path.join(basedir, 'smac', 'conf', 'specifications', 'api', 'all.thrift')))    
        empty_dir(os.path.join(basedir, 'docs', '_thrift'))
        os.rename(os.path.join(basedir, 'docs', 'gen-html'), os.path.join(basedir, 'docs', '_thrift'))
    
    if args[0] == 'thriftdjango':
        output_dir = args[1]
        new_ns = args[2]
        output_dir = os.path.realpath(output_dir)
        
        print ""
        print "CAUTION: This script will remove all files in the '%s' directory." % output_dir
        print ""

        response = raw_input("Continue execution [N/y]? ")

        if not response.lower().startswith('y'):
            print "Cancelling execution"
            print ""
            sys.exit(0)

        empty_dir(os.path.join(output_dir))
        os.system('thrift -r -o "%s" --gen py:new_style "%s"' % (output_dir, os.path.join(basedir, 'smac', 'conf', 'specifications', 'api', 'all.thrift')))
        os.system('mv %s %s' % (os.path.join(output_dir, 'gen-py', 'smac', 'api', '*'), output_dir))
        empty_dir(os.path.join(output_dir, 'gen-py'))
        os.rmdir(os.path.join(output_dir, 'gen-py'))
        
        # Replace all namespaces!
        old_ns = 'smac.api'
        
        for root, dirs, files in os.walk(output_dir):
            for name in files:
                f = os.path.join(root, name)

                fh = open(f, 'r')
                s = fh.read().replace(old_ns, new_ns)
                fh.close()
                
                fh = open(f, 'w+')
                fh.write(s)
                fh.close()
