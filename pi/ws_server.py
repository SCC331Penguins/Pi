from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from json import loads

class WSProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        # in here maybe append payload to a structure for analysis and run analysis
        if isBinary:
            return
        print payload
        data = loads(payload)
        SENSORID = data['SENSORID']
        self.factory.addToDB(SENSORID,data)
        if SENSORID in self.factory.dataChannels:
            for channel in self.factory.dataChannels:
                self.factory.sendMQTTMessage('DATA',data,channel)
        # handle Photon Messages
        # if not isBinary:
        #     msg = "{} from {}".format(payload.decode('utf8'), self.peer)
        #     print(msg)
        self.factory.broadcast(payload)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class WSServerFactory(WebSocketServerFactory):

    """autobahn websocket 400 origin header invalid
    Simple websocket server.with broadcast functionality
    """

    def __init__(self, addToDB):
        WebSocketServerFactory.__init__(self, u"ws://127.0.0.1:8000")
        self.clients = []
        self.tickcount = 0
        self.protocol = WSProtocol
        self.addToDB = addToDB
        self.sendMQTTMessage = None
        self.dataChannels = {}
    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)
    def addMQTTCallback(self,sendMQTTMessage):
        self.sendMQTTMessage = sendMQTTMessage
    def addDataChannel(self, SENSORID, channel):
        if self.dataChannels.get(SENSORID) is None:
            self.dataChannels[SENSORID] = []
        self.dataChannels.append(channel)

    def removeDataChannel(self, SENSORID, channel):
        if self.dataChannels.get(SENSORID) is None:
            self.dataChannels[SENSORID] = []
        if channel in self.dataChannels[SENSORID]:
            self.dataChannels.remove(channel)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))
