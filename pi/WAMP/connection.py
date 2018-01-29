from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

class Connection(ApplicationSession):
    def __init__(self, name, events=[], procedures=[], handler=None):
        ApplicationSession.__init__(self,None)
        print('Connection')
        self.name = name
        self.events = events
        self.procedures = procedures
        self.handler = handler
        pass
    def connect(self):
        run = ApplicationRunner(
            u"ws://127.0.0.1:8080/ws",
            u"realm1"
        )
        run.run(self)
    def onJoin(self, details):
        print('{}'.format(details))
        for evt in self.events:
            yield self.subscribe(lambda m: self.onEvent(evt,m))
        pass
    def onEvent(self, evt, msg):
        msg.evt = evt
        msg.connection = self.name
        # print("Got event: {}".format(msg))
        if(self.handler):
            self.handler()
        pass
    def sendEvent(self, evt, message):
        self.publish(evt, message)
        pass
