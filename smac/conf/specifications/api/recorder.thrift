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

include "types.thrift"
include "base.thrift"

namespace py smac.api.recorder

enum StreamType {
    VIDEO,
    AUDIO,
    MUXED
}

struct Stream {
    1: string id,
    2: StreamType type,
}

struct AcquisitionDevice {
    1: string id,
    2: string name,
    3: list<Stream> streams,
}

exception InvalidConfiguration {
    1: string message,
    2: string configuration,
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
    
    /**
     * Lists all acquisition devices available on this recorder. Each device in
     * the list contains the list of its streams.
     */
    list<AcquisitionDevice> get_acquisition_devices(),
    
    /**
     * Creates a new acquisition session coupled to this module with the given
     * configuration (in JSON format).
     * 
     * @return: The ID of the newly created acquisition session 
     * @raise:  InvalidConfiguration if the configuration can't be correctly
     *          applied to the current hardware setup
     *
     * NOTE: The API for this method is going to change in the future and to
     * deprecate the JSON format for the exchange of the configuration.
     * The signature will change as soon as the real needs for the details about
     * the devices and their properties are known, in order to establish a 
     * proper and complete API.
     */
    i32 create_local_acquisition_session(1: string configuration) throws (1: InvalidConfiguration invalid),
    
    /**
     * Starts the recording of a particular (configured) acquisition session.
     *
     * @raise:  InvalidSessionID if the given session_id was not previously
     *          configured with `create_local_acquisition_session`
     * @raise:  AlreadyRecording if a capture session is already running
     */
    void start_recording(1: i32 session_id) throws (1: InvalidSessionID invalid, 2: AlreadyRecording busy),
    
    /**
     * Stops the recording of a particular (running) acquisition session.
     *
     * @raise:  InvalidSessionID if the given session_id was not previously
     *          configured with `create_local_acquisition_session`
     * @raise:  NotRecording if the given session_id is not currently running
     */
    void stop_recording(1: i32 session_id) throws (1: InvalidSessionID invalid, 2: NotRecording free),
    
    /**
     * Utility method to get the ID of the currently running acquisition session.
     *
     * @return: The ID of the currently running session, if one is running
     * @raise:  A NotRecording exception with the session_id attribute set to 0
     */
    i32 running_session() throws (1: NotRecording free),
}