#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "types.thrift"
include "task.thrift"
include "session.thrift"

namespace py smac.api.base

service AMQPService {}
service RPCService {}

service BaseModule extends AMQPService {
    /**
     * Synchronous ping to be used to check that a module is still online.
     */
    void ping(),
    
    types.GeneralModuleInfo info(),
    
    /**
     * Asynchronous reverse ping to be broadcasted.
     */
    oneway void announce(1: string address),
}


service TaskModule extends BaseModule {
    /**
     * Returns a list of all task actually running on this module
     */
    list<types.TaskID> tasks(),
}


service SessionModule extends TaskModule {
    /**
     * Configures a new session listener for the given section and prepares the
     * module for the needed steps to perform the interface specific handling.
     *
     * This method can be called as many times as wanted and shall not cause
     * collateral effects.
     */
    void configure_session(1: session.Session session),
}