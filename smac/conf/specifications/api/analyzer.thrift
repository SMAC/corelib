#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "base.thrift"

namespace py smac.api.analyzer

service Analyzer extends base.SessionModule {
    void analyze(1: i32 contrib_id)
}
