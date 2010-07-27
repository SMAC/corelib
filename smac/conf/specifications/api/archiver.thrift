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

service Archiver extends base.Module {
    void start_upload(
        1: string transfer_key
        2: i64 size
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
