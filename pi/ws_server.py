from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from json import loads, dumps
import logging
logger = logging.getLogger()


class WSProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        # in here maybe append payload to a structure for analysis and run analysis
        if isBinary:
            return
        data = loads(payload)
        SENSORID = data['SENSORID']
        button = data.get('button')
        alert = data.get('alert')
        if button is None and alert is None:
            if SENSORID == "GAME":
                self.factory.gameClients.append(self)
                return
            if(data['motion'] == True and self.cache.getCurrentStatus()['userlocation'] == SENSORID):
                self.factory.alert(1)
                self.factory.broadcast('alert:'+alert)
            self.factory.addToDB(SENSORID,data)
            if SENSORID in self.factory.dataChannels:
                for channel in self.factory.dataChannels[SENSORID]:
                    self.factory.sendMQTTMessage('DATA',data,channel)
            self.factory.broadcastToGame(payload)
        elif button is not None:
            # button is the number that got pressed
            command = self.factory.cache.getButtonConfig()[button]
            if command is not None:
                self.factory.pushCommand(command)
        elif alert is not None:
            self.factory.broadcast('alert:'+alert)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class WSServerFactory(WebSocketServerFactory):

    """autobahn websocket 400 origin header invalid
    Simple websocket server.with broadcast functionality
    """

    def __init__(self, addToDB, cacheName):
        WebSocketServerFactory.__init__(self, u"ws://127.0.0.1:8000")
        self.clients = []
        self.gameClients = []
        self.tickcount = 0
        self.cache = Cache(cacheName)
        self.protocol = WSProtocol
        self.addToDB = addToDB
        self.sendMQTTMessage = None
        self.dataChannels = {}
    def register(self, client):
        if client not in self.clients:
            logger.info("registered client {}".format(client.peer))
            self.clients.append(client)
    def addAlertDB(self, alert, db):
        self.alert = alert
        self.db = db
    def unregister(self, client):
        if client in self.clients:
            logger.info("unregistered client {}".format(client.peer))
            self.clients.remove(client)
    def addMQTTCallback(self,sendMQTTMessage):
        self.sendMQTTMessage = sendMQTTMessage
    def addDataChannel(self, SENSORID, channel):
        if self.dataChannels.get(SENSORID) is None:
            self.dataChannels[SENSORID] = []
        self.dataChannels[SENSORID].append(channel)

    def removeDataChannel(self, SENSORID, channel):
        if self.dataChannels.get(SENSORID) is None:
            self.dataChannels[SENSORID] = []
        if channel in self.dataChannels[SENSORID]:
            self.dataChannels[SENSORID].remove(channel)

    def broadcast(self, msg):
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
    def broadcastToGame(self, msg):
        for c in self.gameClients:
            c.sendMessage(msg.encode('utf8'))
