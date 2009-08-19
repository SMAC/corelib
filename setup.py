##
# Some (yeh, pretty much really) of the code included in this script is
# borrowed from Django's setup.py file.
#
# Django project homepage: http://djangoproject.com
##

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import os
import sys
from smac import get_version

version = get_version()

def get_download_url(version):
    release = "SMAC_Core-%s.tar.gz" % version
    return 'http://smac.webhop.org/releases/%s' % release

class osx_install_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin": 
    cmdclasses = {'install_data': osx_install_data} 
else: 
    cmdclasses = {'install_data': install_data}

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
smac_dir = 'smac'

for dirpath, dirnames, filenames in os.walk(smac_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name='SMAC_Core',
    version='.'.join((str(version.major), str(version.minor), str(version.build))),
    description='Python library to develop and deploy SMAC modules',
    author='Jonathan Stoppani',
    author_email='<jonathan.stoppani@edu.hefr.ch',
    url='http://smac.hefr.ch',
    download_url=get_download_url(version),
    packages = packages,
    package_data = {'smac.conf': ['specifications/api/*','specifications/amqp/standard/*', 'specifications/amqp/qpid/*']},
    scripts = ['smac/bin/smac'],
    requires=('twisted (>=8.2.0)',),
    provides=('smac.core (%d.%d)' % (version.major, version.minor),),
    license='GPLv3',
    classifiers = ['Development Status :: 1 - Planning',
                   'Environment :: Console',
                   'Environment :: Web Environment',
                   'Environment :: No Input/Output (Daemon)',
                   'Framework :: Twisted',
                   'Intended Audience :: Education',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Intended Audience :: Telecommunications Industry',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Communications :: Conferencing',
                   'Topic :: Education',
                   'Topic :: Education :: Computer Aided Instruction (CAI)',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Multimedia :: Graphics :: Capture',
                   'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
                   'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
                   'Topic :: Multimedia :: Graphics :: Presentation',
                   'Topic :: Multimedia :: Graphics :: Viewers',
                   'Topic :: Multimedia :: Sound/Audio',
                   'Topic :: Multimedia :: Sound/Audio :: Analysis',
                   'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
                   'Topic :: Multimedia :: Video',
                   'Topic :: Multimedia :: Video :: Capture',
                   'Topic :: Multimedia :: Video :: Conversion',
                   'Topic :: Multimedia :: Video :: Display',
                   'Topic :: Scientific/Engineering :: Human Machine Interfaces',
                   'Topic :: Scientific/Engineering :: Image Recognition',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Text Processing :: Indexing',
                   'Topic :: Text Processing :: Markup :: XML',
                   ],
)