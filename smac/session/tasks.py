

from twisted.internet import defer

from smac import tasks, amqp, api


class SessionTask(tasks.CompoundTask):
    def build_client(self):
        key = "sessions.{0}.commands".format(self.sessid)
        address = amqp.models.Address(routing_key=key)
        return amqp.build_client(address, api.session.SessionListener,
                distribution='sessions')

class Acquisition(SessionTask):
    @defer.inlineCallbacks
    def run(self):
        self.client = yield self.build_client()
        yield self.client.record(self.id)


class Archivation(SessionTask):
    @defer.inlineCallbacks
    def run(self):
        self.client = yield self.build_client()
        yield self.client.archive(self.id)

