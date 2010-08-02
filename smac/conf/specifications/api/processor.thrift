#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "types.thrift"
include "archiver.thrift"

namespace py smac.api.processor

service Processor extends archiver.FileReceiver {
    void process(1: string filename),
    void archive(2: string filename),
}