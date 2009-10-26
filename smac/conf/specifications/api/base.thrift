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

namespace py smac.api.base

struct ModuleAddress {
    1: string instance_id
    2: string implementation
    3: string iface
    4: string ns
}

struct GeneralModuleInfo {
    1: ModuleAddress address
    2: string ip_address
    3: string hostname
}

/**
 * The base external API for each module
 */
service Module {
    /**
     * Asynchronous ping to be used by a broadcast message
     */
    oneway void announce(1: GeneralModuleInfo info)
}


    /**
     * Gets the status of the current service offered by the module.
     * The current implementation returns a struct with the load average.
     */
    //Status get_status(),
    
    /**
     * Gets the status of the task identified by the task_id parameter or the
     * current task if not provided
     */
    //TaskStatus get_task_status(1: i32 task_id=0) throws (1: UnknownTask e),
    
    /**
     * Stops the task identified by the task_id parameter or the current task
     * if not provided
     */
    //void stop_task(1: i32 task_id=0) throws (1: UnknownTask e),
    
    /**
     * Restarts the module.
     */
    //void restart(),
    
    /**
     * Starts the log streaming to the logs exchange, adding the id to the
     * subscribers list.
     */
    //void start_log_streaming(1: string stream_id),
    
    /**
     * Stops the log streaming for the given id. When the subscribed id
     * list reaches 0 length, the stop_log_streaming commands effectively
     * stops the streaming.
     */
    //void stop_log_streaming(1: string stream_id),
//}
/*
struct Status {
    1: double load_average1
    2: double load_average5
    3: double load_average15
    4: i32 uptime
}

struct DetailedModuleInfo {
    1: GeneralModuleInfo general
    2: Status status
    3: map<string,string> additional
}

struct TaskStatus {
    1: i32 task_id
    2: i16 percent_completed
    3: i32 time_elapsed
    4: i32 time_expected
    5: string message
}

exception UnknownTask {
    1: i32 task_id
}

exception UnknownModule {
    1: ModuleAddress module
}

exception NotYetReady {
    1: i16 suggested_retry_delay
}

exception StreamingNotStarted {}*/
