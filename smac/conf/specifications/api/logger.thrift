#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "types.thrift"
include "base.thrift"

namespace py smac.api.logger

const string LOGGER_ROUTING_KEY = '{namespace}.{interface}.{implementation}.{instance_id}.log'

struct LogFile {
    1: types.ModuleAddress module,
    2: string filename
}

service Logger extends base.TaskModule {
    oneway void receive_startup_log(1: types.ModuleAddress sender, 2: string entries),
    oneway void receive_log_entry(1: types.ModuleAddress sender, 2: string entry),
    oneway void receive_shutdown_log(1: types.ModuleAddress sender, 2: string entries),
    
    list<LogFile> get_log_list(),
    string get_log(1: LogFile logfile),
}