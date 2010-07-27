from fabric.api import env, local, prompt
from fabric.context_managers import cd

import os.path as p
import os

env.base = p.dirname(__file__)

def _rm(file):
    """
    Removes the specified directory and all its content without asking for
    confirmation.
    """
    local("rm -rf {0}".format(file))
    
def _builddir(format):
    """
    Given a thrift format specification returns the directory which thrift
    will append to the defined output directory during the build phase.
    """
    format = format.replace('new_style', '')
    builddir = format.split(':')
    
    if len(builddir) is 1 or not builddir[1]:
        builddir = builddir[0]
    else:
        builddir = '.'.join((builddir[0], builddir[1].split(',')[-1]))
        
    builddir = 'gen-{0}'.format(builddir)
    
    return builddir

def api(default=False):
    """
    Builds all APIs (core and frontend).
    """
    
    coreapi()
    frontendapi(default=default)

def frontendapi(idlfile='controller.thrift frontend.thrift', format='py:new_style', default=False):
    """
    Generates the api for the frontend from the thrift IDL sources.
    """
    builddir = p.join(env.base, _builddir(format), 'smac', 'api')
    
    # Ask for the destination directory, but provide a default
    destdir = p.join(p.dirname(env.base), 'smac-controller-frontend', 'frontend', 'api')
    
    if not default:
        destdir = prompt("Please specify the frontend API location:", default=destdir)
    
    # Remove current builddir
    _rm(builddir)
    
    # Generate API
    for f in idlfile.split():
        apifile  = p.join(env.base, 'smac', 'conf', 'specifications', 'api', f)
        local("thrift --gen {0} -r -o {1} {2}".format(format, env.base, apifile))
    
    # Update all namespaces
    oldns = 'smac.api'
    newns = 'frontend.api'
    
    for root, dirs, files in os.walk(builddir):
        for name in files:
            f = p.join(root, name)
            
            with open(f, 'r+') as fh:
                s = fh.read().replace(oldns, newns)
                fh.seek(0)
                fh.write(s)
    
    # Move each subdirectory to the destination, asking permission to
    # overwrite an existing file or directory
    for d in os.listdir(builddir):
        if not d == '__init__.py':
            dest = p.join(destdir, d)
            pr = "Overwrite existing directory {0}? [Y/n]".format(dest)
            
            def confirm(res):
                return res.lower() in ('', 'y', 'yes', 'ok', '1')
            
            if default or not p.exists(dest) or prompt(pr, validate=confirm):
                _rm(dest)
                os.rename(p.join(builddir, d), dest)
    
    # Remove build directory
    _rm(p.dirname(p.dirname(builddir)))

def coreapi(idlfile='all.thrift', format='py:new_style,twisted'):
    """
    Generates the api for the corelib from the thrift IDL sources.
    """
    
    builddir = p.join(env.base, _builddir(format), 'smac', 'api')
    destdir  = p.join(env.base, 'smac', 'api')
    
    # Remove current builddir
    _rm(builddir)
    
    # Generate API
    for f in idlfile.split():
        apifile  = p.join(env.base, 'smac', 'conf', 'specifications', 'api', f)
        local("thrift --gen {0} -r -o {1} {2}".format(format, env.base, apifile))
    
    # Remove old build
    _rm(destdir)
    
    # Move into new location
    os.rename(builddir, destdir)
    
    # Remove build directory
    _rm(p.dirname(p.dirname(builddir)))