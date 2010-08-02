#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "types.thrift"
include "base.thrift"
include "logger.thrift"
include "session.thrift"
include "task.thrift"

namespace py smac.api.controller

const i32 LOG_REQUEST_TIMEOUT = 45

/**
 * The controller interface. This class exposes two different typologies of
 * methods:
 * 1) the controller-modules interface, intended to let the controller
 *    communicate with all others modules on the system, and
 * 2) the controller-web client interface, intended to let the web
 *    administration interface interact with the controller (and thus with the
 *    whole system)
 */
service Controller extends base.TaskModule {
    #############################################################
    # Controller - Modules interface                            #
    #############################################################
    
    /**
     * Used when the controller registers itself on the services exchange to
     * stream a log to the client.
     */
    oneway void receive_startup_log(1: types.ModuleAddress sender, 2: string entries),
    oneway void receive_log_entry(1: types.ModuleAddress sender, 2: string entry),
    oneway void receive_shutdown_log(1: types.ModuleAddress sender, 2: string entries),
}



service ControllerFrontend extends base.RPCService {
    map<types.SessionID,session.Basic> session_get_active(),
    types.SessionID session_create(1: string title, 2: types.Setup setup),
    types.SessionID session_create(1: string title, 2: types.Setup setup),
    session.Session session_get(1: types.SessionID sessid),
    void            session_meta_save(1: types.SessionID sessid, 2: session.Meta meta),
    types.TaskID    session_recording_start(1: types.SessionID sessid)
    void            session_recording_stop(1: types.SessionID sessid)
    types.TaskID    session_archive(1: types.SessionID sessid)
    
    
    void request_log_streaming(1: types.ModuleAddress module) throws (1: types.InvalidModule no_module),
    list<logger.LogFile> get_log_list(1: types.ModuleAddress logger),
    string get_log(1: types.ModuleAddress logger, 2: logger.LogFile logfile),
    
    string setup_session(
        1: string session
    ) throws (
        1: types.InvalidSetup invalid,
        2: types.SetupNotReady notready
    ),
    
    void start_recording(1: string session_id),
    void stop_recording(1: string session_id),
    void archive(1: string session_id),
}




