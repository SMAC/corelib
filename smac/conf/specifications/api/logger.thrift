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

include "base.thrift"

namespace py smac.api.logger

const string LOGGER_ROUTING_KEY = '{namespace}.{interface}.{implementation}.{instance_id}.log'

service Logger extends base.Module {
    oneway void receive_startup_log(1: base.ModuleAddress sender, 2: string entries),
    oneway void receive_log_entry(1: base.ModuleAddress sender, 2: string entry),
    list<base.ModuleAddress> get_log_list(),
    string get_log(1: base.ModuleAddress module),
}