#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

namespace py smac.api

typedef string UUID
typedef string TaskID
typedef string SessionID
typedef string Setup
typedef i64 Timestamp
typedef string Speaker

#############################################################
# Date/Time related types                                   #
#############################################################

struct Time {
    // @TODO    
}

struct Date {
    1: i16 year
    2: i16 month
    3: i16 day
}

struct Datetime {
    1: Date date
    2: Time time
}

/**
 * An object representing the difference between two date, time or datetime objects.
 * The name and ordering of the attributes is compatible with the python datetime.timedelta
 * internal class structure.
 */
struct TimeDelta {
    1: optional i32 days
    2: optional i32 seconds
    3: optional i32 microseconds
}

#############################################################
# Module addressing and information                         #
#############################################################

struct ModuleAddress {
    1: string ns
    2: string iface
    3: string implementation
    4: string instance_id
}

struct GeneralModuleInfo {
    1: ModuleAddress address
    2: string ip_address
    3: string hostname
}

exception InvalidModule {
    1: ModuleAddress module
}

#############################################################
# Acquisition                                               #
#############################################################

exception InvalidSetup {
}
exception SetupNotReady {
}