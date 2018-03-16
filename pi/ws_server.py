from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from json import loads, dumps
from twisted.internet import reactor

from .cache import Cache
import logging
logger = logging.getLogger()


class WSProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        # in here maybe append payload to a structure for analysis and run analysis
        if isBinary:
            return
        logger.info(payload)
        data = loads(payload)
        button = data.get('button')
        alert = data.get('alert')
        if button is None and alert is None:
            SENSORID = data['SENSORID']
            if SENSORID == "GAME":
                self.factory.gameClients.append(self)
                return
            logger.debug('Hello i am in'+SENSORID)
            logger.debug('Hello1 i am in'+self.factory.cache.getCurrentStatus()['userlocation'])
            logger.debug('Alex The Lion '+str(self.factory.cache.getCurrentStatus()['userlocation'] in SENSORID))
            if( data['motion'] and self.factory.cache.getCurrentStatus()['userlocation'] not in SENSORID):
                logger.info('TRIGGERED BY MOTION AND userlocation in ' + SENSORID)
                self.factory.broadcast('ALARM_ON')
                self.factory.alert(SENSORID)
            self.factory.addToDB(SENSORID,data)
            if SENSORID in self.factory.dataChannels:
                for channel in self.factory.dataChannels[SENSORID]:
                    self.factory.sendMQTTMessage('DATA',data,channel)
            self.factory.broadcastToGame(payload)
        elif button is not None:
            # button is the number that got pressed
            # print self.factory.cache.getButtonConfig()
            command = self.factory.cache.getButtonConfig().get(str(button), None)
            print 666
            print command
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
        self.pushCommand = None
        self.dataChannels = {}
        reactor.callLater(1,self.doAlert)
    def doAlert(self):
        print 'ALERTING';
        self.broadcast('ALARM_ON');
        # reactor.callLater(5,self.doAlert)

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
    def toCommand(self, commandObj):
            payload = commandObj
            pythonCode = ""
            if(payload['command']=='sendNotification'):
                pythonCode = """for item in actuators:
                if item['mac'] == '{}':
                    {}(item,'{}')
                """.format(payload['MAC'],payload['command'], payload['message'])
            else:
                pythonCode = """for item in actuators:
                if item['mac'] == '{}':
                    {}(item)
                """.format(payload['MAC'],payload['command'])
            logger.debug(pythonCode)
            return pythonCode
    def addPushCommand(self, command):
        self.pushCommand = command

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
