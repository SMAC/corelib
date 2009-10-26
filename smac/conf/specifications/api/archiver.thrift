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

namespace py smac.api.archiver

exception FileAlreadyExists {
    1: string filename
}

exception DataTransferNotYetStarted {
    1: i32 transfer_id
}

exception InvalidFilename {
    1: string filename
}

exception AlreadyUploading {
    1: string filename
}

service Archiver extends base.Module {
    i32 start_upload(1: string filename, 2: bool overwrite, 3: binary checksum, 4: i64 size) throws (1: FileAlreadyExists exists, 2: InvalidFilename invalid, 3: AlreadyUploading uploading),
    
    void send_data_chunk(1: i32 transfer_id, 2: binary data, 3: i64 offset) throws (1: DataTransferNotYetStarted e),
    
    //binary receive_data_chunk(1: i32 transfer_id) throws (1: DataTransferNotYetStarted e),
}
