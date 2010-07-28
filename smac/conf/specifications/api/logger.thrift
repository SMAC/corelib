#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
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
include "base.thrift"

namespace py smac.api.logger

const string LOGGER_ROUTING_KEY = '{namespace}.{interface}.{implementation}.{instance_id}.log'

struct LogFile {
    1: types.ModuleAddress module,
    2: string filename
}

service Logger extends base.Module {
    oneway void receive_startup_log(1: types.ModuleAddress sender, 2: string entries),
    oneway void receive_log_entry(1: types.ModuleAddress sender, 2: string entry),
    oneway void receive_shutdown_log(1: types.ModuleAddress sender, 2: string entries),
    
    list<LogFile> get_log_list(),
    string get_log(1: LogFile logfile),
}