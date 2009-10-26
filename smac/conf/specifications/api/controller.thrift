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

namespace py smac.api.controller

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
    
    #####################################
    # Controller - Web client interface #
    #####################################
    
    list<base.GeneralModuleInfo> module_list(),
    
    list<base.ModuleAddress> get_log_list(1: base.ModuleAddress logger),
    
    string get_log(1: base.ModuleAddress logger, 2: base.ModuleAddress module),
    
    
    ##################################
    # Controller - Modules interface #
    ##################################
    
    #oneway void receive_log_entry(1: base.ModuleAddress module,
    #    2: string log_entry),
    #
    #list<string> get_module_log_stream(
    #    1: base.ModuleAddress module,
    #    2: i16 timeout, 3: i32 offset) throws (1: base.UnknownModule unknown),
    
}