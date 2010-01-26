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

namespace py smac.api.recorder

enum StreamType {
    VIDEO,
    AUDIO,
    MUXED
}

struct Stream {
    1: string ID,
    2: StreamType type,
}

struct AcquisitionDevice {
    1: string ID,
    2: string name,
    3: list<Stream> streams,
}

exception InvalidSessionID {
    1: i32 session_id,
}

exception AlreadyRecording {
    1: i32 session_id,
    2: i32 running_session_id,
}

exception NotRecording {
    1: i32 session_id
}

service Recorder extends base.Module {
    list<AcquisitionDevice> get_acquisition_devices(),
    
    // Returns the session ID
    i32 create_local_acquisition_session(),
    
    void start_recording(1: i32 session_id) throws (1: InvalidSessionID invalid, 2: AlreadyRecording busy),
    void stop_recording(1: i32 session_id) throws (1: InvalidSessionID invalid, 2: NotRecording free),
    
    void add_stream(1: string sessions_id, 2: string stream_id)
}