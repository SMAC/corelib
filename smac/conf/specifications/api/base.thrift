#!/usr/bin/thrift --gen py:twisted

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

include "types.thrift"

namespace py smac.api.base

service Module {
    /**
     * Synchronous ping to be used to check that a module is still online.
     */
    void ping(),
    
    /**
     * Asynchronous ping to be used by a broadcast message
     */
    oneway void announce(1: types.GeneralModuleInfo info, 2: i32 timestamp),
    
    /**
     * Getter for informations about a specific task
     */
    types.Task get_task(1: types.TaskID id) throws (1: types.InvalidTask invalid),
    
    /**
     * Returns a list of all task actually running on this module
     */
    list<types.Task> get_tasks(),
}