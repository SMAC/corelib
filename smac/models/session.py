
import uuid, itertools
from epsilon.extime import Time
from axiom import item, attributes
from twisted.python import components
from zope.interface import Interface, implements

import smac.api.session.ttypes as thrift_session_model
import smac.api.tasks.ttypes as thrift_task_model
from smac.util.text import force_string


def uuid_factory():
    return str(uuid.uuid1())


class Event(item.Item):
    timestamp = attributes.timestamp()
    message = attributes.text()
    category = attributes.bytes()
    source = attributes.reference()
    level = attributes.integer()


class IThriftTask(Interface):
    pass


class Task(item.Item):
    uuid = attributes.bytes(defaultFactory=uuid_factory)
    name = attributes.text()
    status_text = attributes.text()
    parent = attributes.reference()  # Can be a Session, a Module or another Task
    status = attributes.integer()
    completed = attributes.ieee754_double()
    started = attributes.timestamp()
    ended = attributes.timestamp()
    
    @property
    def subtasks(self):
        return list(self.store.query(Task, Task.parent == self))


class ThriftTaskAdapter(thrift_task_model.Task):
    implements(IThriftTask)
    
    def __init__(self, original):
        self.original = original
    
    @property
    def id(self):
        return self.original.uuid
    
    @property
    def parent(self):
        return self.original.parent.uuid if isinstance(self.original.parent, Task) else None
    
    @property
    def sessid(self):
        return self.original.parent.uuid if isinstance(self.original.parent, Session) else None
    
    @property
    def name(self):
        return force_string(self.original.name)
    
    @property
    def type(self):
        if self.original.completed is None:
            return thrift_task_model.TaskType.UNDETERMINED
        else:
            return thrift_task_model.TaskType.DETERMINED
    
    @property
    def status(self):
        return self.original.status
    
    @property
    def status(self):
        return self.original.status
    
    @property
    def status_text(self):
        return force_string(self.original.status_text)
    
    @property
    def completed(self):
        return self.original.completed
    
    @property
    def started(self):
        return self.original.started.asPOSIXTimestamp()
    
    @property
    def remaining(self):
        if self.started and self.completed:
            return (Time().asPOSIXTimestamp() - self.started) / self.completed - self.started


class Location(item.Item):
    label = attributes.text()
    geocode = attributes.text()
    latitude = attributes.point10decimal()
    longitude = attributes.point10decimal()


class IThriftSession(Interface):
    pass


class Session(item.Item):
    uuid = attributes.bytes(defaultFactory=uuid_factory)
    title = attributes.text()
    description = attributes.text()
    _start = attributes.timestamp()
    _end = attributes.timestamp()
    auto_timing = attributes.boolean(default=True)
    setup = attributes.bytes()
    status = attributes.bytes(default='waiting')
    location = attributes.reference()
    speakers = attributes.textlist()
    
    @property
    def start(self):
        if self.auto_timing:
            task = self.store.findFirst(Task, Task.parent == self and Task.name == u'Acquisition')
            return task.started if task else None
        
        return self._start
    
    @start.setter
    def set_start(self, value):
        self.auto_timing = False
        self._start = value
    
    @property
    def end(self):
        if self.auto_timing:
            task = self.store.findFirst(Task, Task.parent == self and Task.name == u'Acquisition')
            return task.ended if task else None
        
        return self._end
    
    @end.setter
    def set_end(self, value):
        self.auto_timing = False
        self._end = value
    
    @property
    def tasks(self):
        return list(self.store.query(Task, Task.parent == self))
    
    @property
    def alltasks(self):
        return itertools.chain(self.tasks, *map(lambda t: t.subtasks, self.tasks))
    

def ThriftSessionAdapter(original):
    session = thrift_session_model.Session()
        
    def meta(original):
        timing = thrift_session_model.Timing(original.auto_timing)
        
        try:
            timing.start = original.start.asPOSIXTimestamp()
            timing.end = original.stop.asPOSIXTimestamp()
        except AttributeError:
            pass
        
        loc = original.location
        location = thrift_session_model.Location()
        
        if loc:
            location.label = force_string(loc.label)
            location.coords = thrift_session_model.Coordinates(loc.latitude, loc.longitude)
            location.geocode = force_string(loc.geocode)
        else:
            location.coords = thrift_session_model.Coordinates()
        
        return thrift_session_model.Meta(
            force_string(original.title),
            force_string(original.description),
            timing,
            location,
            set(map(force_string, original.speakers or ()))
        )
    
    session.id = original.uuid
    session.meta = meta(original)
    session.setup = original.setup
    session.status = original.status
    session.tasks = dict((t.uuid, IThriftTask(t)) for t in original.alltasks)
    session.history = {}
    
    return session

components.registerAdapter(ThriftSessionAdapter, Session, IThriftSession)
components.registerAdapter(ThriftTaskAdapter, Task, IThriftTask)

