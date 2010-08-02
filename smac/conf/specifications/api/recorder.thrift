#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "types.thrift"
include "base.thrift"
include "task.thrift"
include "session.thrift"

namespace py smac.api.recorder

enum StreamType {
    VIDEO
    AUDIO
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
    1: string session_id,
}

exception AlreadyRecording {
    1: string session_id,
    2: string running_session_id,
}

exception NotRecording {
    1: string session_id
}

exception NotYetRecorded {
    1: string session_id
}

service Recorder extends base.SessionModule {
    
    /**
     * Lists all acquisition devices available on this recorder. Each device in
     * the list contains the list of its streams.
     */
    list<AcquisitionDevice> acquisition_devices(),
    
    /**
     * Creates a new acquisition session coupled to this module with the given
     * configuration (in JSON format).
     * 
     * @return: The ID of the newly created acquisition session 
     * @raise:  InvalidConfiguration if the configuration can't be correctly
     *          applied to the current hardware setup
     */
    void session_configure(1: types.SessionID sessid, 2: types.Setup setup) throws (1: InvalidConfiguration invalid),
    
    /**
     * Starts the recording of a particular (configured) acquisition session.
     *
     * @raise:  InvalidSessionID if the given session_id was not previously
     *          configured with `create_local_acquisition_session`
     * @raise:  AlreadyRecording if a capture session is already running
     */
    void session_recording_start(1: types.SessionID sessid, 2: types.TaskID parent) throws (1: InvalidSessionID invalid, 2: AlreadyRecording busy),
    
    /**
     * Stops the recording of a particular (running) acquisition session.
     *
     * @raise:  InvalidSessionID if the given session_id was not previously
     *          configured with `create_local_acquisition_session`
     * @raise:  NotRecording if the given session_id is not currently running
     */
    void session_recording_stop(1: types.SessionID session_id) throws (1: InvalidSessionID invalid, 2: NotRecording free),
    
    void session_archive(1: types.SessionID sessid, 2: types.TaskID parent) throws (1: InvalidSessionID invalid, 2: NotYetRecorded free),
}