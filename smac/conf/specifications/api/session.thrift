namespace py smac.api.session

include "types.thrift"
include "task.thrift"

struct Timing {
    1: bool auto
    2: types.Timestamp start
    3: types.Timestamp end
}

struct Coordinates {
    1: double latitude
    2: double longitude
}

struct Location {
    1: string label
    2: Coordinates coords
    3: string geocode
}

struct Meta {
    1: string title
    2: string description
    3: Timing timing
    4: Location location
    5: set<types.Speaker> speakers
}

struct Session {
    1: types.SessionID id
    2: Meta meta
    3: types.Setup setup
    4: map<types.TaskID,task.Task> tasks
    5: map<string,types.TaskID> history
    6: string status,
}

struct Basic {
    1: string title,
    2: i16 running_tasks,
    3: string status,
}

service SessionListener {
    oneway void record(1: types.TaskID parent),
    oneway void archive(1: types.TaskID parent),
    oneway void analyze(1: types.TaskID parent),
    oneway void publish(1: types.TaskID parent),
}

