#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "types.thrift"
include "task.thrift"
include "recorder.thrift"

namespace py smac.api.frontend

service Modules {
    void announced(1: types.GeneralModuleInfo module),
    void recorder_announced(1: types.GeneralModuleInfo module, 2: list<recorder.AcquisitionDevice> devices),
    void gone(1: types.ModuleAddress addr),
}

service Tasks {
    void update(1: task.Task task),
    void update_all(1: list<task.Task> tasks),
}