#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

include "types.thrift"

namespace py smac.api.tasks

enum TaskType {
    DETERMINED
    UNDETERMINED
}

enum TaskStatus {
    WAITING
    RUNNING
    FAILED
    PAUSED
    CANCELLED
    COMPLETED
}

#struct _Task {
#    1: types.TaskID id,
#    2: optional types.TaskID parent,
#    3: optional types.SessionID session
#    4: string name
#    5: TaskType type,
#    6: TaskStatus status,
#    7: string status_text,
#    8: optional double completed,
#    9: optional i32 remaining,
#    10: optional bool children,
#}
struct Task {
    1: types.TaskID id
    2: optional types.TaskID parent
    3: optional types.SessionID sessid
    4: string name
    5: TaskType type
    6: TaskStatus status
    7: string status_text
    8: optional double completed
    9: optional i32 remaining
    10: types.Timestamp started
    #10: optional set<_Task> children,
}

exception InvalidCommand {}

service TaskServer {
    void pause   ()                           throws (1: InvalidCommand invalid),
    void resume  ()                           throws (1: InvalidCommand invalid),
    void cancel  (1: optional string message) throws (1: InvalidCommand invalid),
    void fail    (1: optional string message) throws (1: InvalidCommand invalid),
    void stop(1: optional string message) throws (1: InvalidCommand invalid),
    Task info    (),
    string module(),
}

service TaskListener {
    oneway void update(1: Task task),
}


