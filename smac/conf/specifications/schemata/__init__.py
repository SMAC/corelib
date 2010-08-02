"""
Ciao
"""

from lxml import etree
from os.path import realpath, dirname, join

__all__ = ('__doc__', 'setup_structure')

def _setup_structure():
    """
    Ciao
    """
    schema = join(dirname(realpath(__file__)), 'setup-structure.xsd')
    return etree.XMLSchema(etree.parse(open(schema)))

setup_structure = _setup_structure()