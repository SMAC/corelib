#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "base.thrift"
include "types.thrift"

namespace py smac.api.archiver

const string TRANSFER_ROUTING_KEY = '{key}.transfer'

exception AlreadyUploading {
    1: string tranfer_key
}

exception InvalidChecksum {
    1: string transfer_key
}


service FileReceiver  {
    oneway void send_data_chunk(
        1: binary data,
    ),
}

service Archiver extends base.TaskModule {
    void start_upload(
        1: string transfer_key
        2: string name
        3: i64 size
        4: string parent
    ) throws (
        1: AlreadyUploading busy,
    ),
    
    void finalize_upload(
        1: string transfer_key,
        2: binary checksum
    ) throws (
        1: InvalidChecksum invalid
    ),
}
