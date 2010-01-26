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
include "logger.thrift"

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
service Controller extends base.Module {
    
    #############################################################
    # Controller - Web client interface                         #
    #############################################################
    
    list<base.GeneralModuleInfo> module_list(),
    
    void request_log_streaming(1: base.ModuleAddress module) throws (1: base.InvalidModule no_module),
    
    list<logger.LogFile> get_log_list(1: base.ModuleAddress logger),
    
    string get_log(1: base.ModuleAddress logger, 2: logger.LogFile logfile),
    
    list<base.Task> get_tasks(),
    
    
    #############################################################
    # Controller - Modules interface                            #
    #############################################################
    
    /**
     * Used when the controller registers itself on the services exchange to
     * stream a log to the client.
     */
    oneway void receive_startup_log(1: base.ModuleAddress sender, 2: string entries),
    oneway void receive_log_entry(1: base.ModuleAddress sender, 2: string entry),
    oneway void receive_shutdown_log(1: base.ModuleAddress sender, 2: string entries),
    
    /**
     * Callback used by the modules to notify a task update to the controller.
     */
    oneway void update_task(1: base.Task task),
    
}