# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Various, general purpose, text manipulation utilities.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""

import re

def camelcase_to_underscore(string):
    """
    Converts a CamelCasedName in an underscore_separated_name.
    """
    return re.sub(r'([a-z])([A-Z]+)', r'\1_\2', string).lower()