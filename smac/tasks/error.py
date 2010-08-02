# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Errors and exceptions to use when working with tasks.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


class TaskCancelled(Exception):
    """
    An exception which is thrown when a task is cancelled.
    """

class TaskFailed(Exception):
    """
    An exception which is thrown when a task is marked as failed.
    """