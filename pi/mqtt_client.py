from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from json import dumps
from twisted.internet.defer import inlineCallbacks
from twisted.application.internet import ClientService, backoffPolicy
import json,time,jwt, logging
from .cache import *
logger = logging.getLogger()
dumps({},ensure_ascii=False)
from .utils import type_check
WiFiCreds = {
    "ssid":"SCC33X_2",
    "password": "!studiox?56"
}
def UPDATE_SENSORS(self, message):
    bmsg = ''
    for sensor in message['payload']:
        bmsg = bmsg + 'id:'+sensor['id']+' config:'+str(sensor['config'])+', '
    bmsg = bmsg[:-2]
    self.cb(bmsg)
def SET_WIFI_CREDS(ctx, message):
    WiFiCreds = message.payload

def SCRIPTS_UPDATE(self, message):
    logger.debug('Scripts Updating')
    try:
        self.updateScripts(message['payload'])
    except Exception as e:
        print(e)
def COMMAND(self, message):
    payload = message['payload']
    self.doCommand(payload['command'], payload['type'], payload['MAC'])

typeDic = {
# 100:PING,
# 21:ACTIVE_SENSORS,
# 33:DATA,
# 91:REG_ACT,
20:UPDATE_SENSORS,
8:SCRIPTS_UPDATE,
3:SET_WIFI_CREDS,
64:COMMAND,
}
def err(err):
    print(err)

class MQTTService(ClientService):
    def __init__(self, endpoint, factory):
        ClientService.__init__(self, endpoint, factory, retryPolicy=backoffPolicy())
        self.cb = None
        self.updateScripts = None
        self._config = json.load(
            open('id.json')
        )
        self.generate_token()
        self.channels = ['SCC3312']
        logger.info('WAMP Server Setup')

    def startService(self):
        logger.info("starting MQTT Client Subscriber Service")
        # invoke whenConnected() inherited method
        self.whenConnected().addCallback(self.connectToBroker)
        ClientService.startService(self)

    @inlineCallbacks
    def connectToBroker(self, protocol):
        '''
        Connect to MQTT broker
        '''
        self.protocol                 = protocol
        self.protocol.onPublish       = self.onPublish
        self.protocol.onDisconnection = self.onDisconnection
        # We are issuing 3 publish in a row
        # if order matters, then set window size to 1
        # Publish requests beyond window size are enqueued
        self.protocol.setWindowSize(1)
        try:
            yield self.protocol.connect(self._config['RouterID']+'-Router', keepalive=60)
            yield self.subscribe()
        except Exception as e:
            logger.error("Connecting to {broker} raised {excp!s}",
               broker="f", excp=e)
        else:
            print('yolo')
            reactor.callLater(1,self.do_ping)
            logger.info("Connected to MQTT Server")
        self.sendMsg(100,0,topic='SCC331')
    def subscribe(self):
        for channel in self.channels:
            self.protocol.subscribe(channel, 1 )

    def set_broadcast(self, cb, scripts):
        logger.info('WAMP now has broadcast ability')
        self.updateScripts = scripts
        self.cb = cb

    def generate_token(self):
        self.token = (jwt.encode({"id":self._config['RouterID']},self._config['SharedSecretKey'], algorithm="HS256"))

    # def onOpen(self):
    #     logger.info('Connected to WS Server')
    #     # self.subscribe(self.onEvent,self._config['RouterID'])
    #     reactor.callLater(1,self.do_ping)

    def sendMsg(self, typeInt, payload, topic=None, msgObject={}):
        if(topic == None):
            topic = self._config['RouterID']
        msgObject[u'type'] = typeInt
        msgObject[u'payload'] = payload
        msgObject[u'token'] = self.token
        self.publish(topic,json.dumps(msgObject,ensure_ascii=False).encode())

    def do_ping(self):
        logger.info('sent Ping')
        # self.publish(u"SCC33102_R01",{"source": 0, "token": 0, "type": 8, "payload": ["print%28%27hi+script%27%29", "print%28%27hi+script%27%29"]})
        self.sendMsg(100,None)
        reactor.callLater(10,self.do_ping)

    def onPublish(self, topic, payload, qos, dup, retain, msgId):
        print payload
        print str(payload)
        msg = json.loads(str(payload))
        logger.info('received'+ payload)
        print(type(msg))
        type_check(msg,dict)
        # type_check(message['type'],long)
        s= typeDic.get(msg['type'])
        s(self, msg)

    def publish(self, topc, msg, q=1):
        self.protocol.publish(topic="SCC331", qos=1, message=msg)

    def onDisconnection(self, reason):
        logger.info('Disconnected from WS Server ')
        self.whenConnected().addCallback(self.connectToBroker)