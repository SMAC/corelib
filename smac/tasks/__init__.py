# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

"""
Task management framework for SMAC systems.

@author: Jonathan Stoppani <jonathan.stoppani@edu.hefr.ch>
"""


from smac.tasks.register import TaskRegister
from smac.tasks.base import Task, ITask, CompoundTask, ICompoundTask


__all__ = ('TaskRegister', 'Task', 'ITask', 'CompoundTask', 'ICompoundTask')