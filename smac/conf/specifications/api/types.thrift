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

namespace py smac.api

#############################################################
# Date/Time related types                                   #
#############################################################

struct Time {
    // @TODO    
}

struct Date {
    // @TODO
}

struct Datetime {
    // @TODO
}

/**
 * An object representing the difference between two date, time or datetime objects.
 * The name and ordering of the attributes is compatible with the python datetime.timedelta
 * internal class structure.
 */
struct TimeDelta {
    1: optional i32 days
    2: optional i32 seconds
    3: optional i32 microseconds
}

#############################################################
# Module addressing and information                         #
#############################################################

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

exception InvalidModule {
    1: ModuleAddress module
}

#############################################################
# Task handling                                             #
#############################################################
 
typedef i64 TaskID

enum TaskType {
    DETERMINED
    UNDETERMINED
}

enum TaskStatus {
    RUNNING
    FAILED
    PAUSED
    CANCELLED
    COMPLETED
}

struct Task {
    1: TaskID id,
    2: TaskType type,
    3: TaskStatus status,
    4: string status_text,
    5: ModuleAddress module,
    6: optional double completed,
    7: optional TimeDelta remaining,
}

exception InvalidTask {
    1: TaskID task_id
}

#############################################################
# Base services                                             #
#############################################################

struct Task {
    1: TaskID id,
    2: TaskType type,
    3: TaskStatus status,
    4: string status_text,
    5: ModuleAddress module,
    6: optional double completed,
    7: optional TimeDelta remaining,
}