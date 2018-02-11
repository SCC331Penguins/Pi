from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession

from twisted.internet.defer import inlineCallbacks
import json,time,jwt, logging
logger = logging.getLogger()

from .utils import type_check
WiFiCreds = {
    "ssid":"SCC33X_2",
    "password": "!studiox?56"
}
def UPDATE_SENSORS(self, message):
    print('here')
    print(message)
    bmsg = ''
    for sensor in message['payload']:
        print(sensor['id'])
        bmsg = bmsg + 'id:'+sensor['id']+' config:'+str(sensor['config'])+', '
    bmsg = bmsg[:-2]
    print(bmsg)
    self.cb(bmsg)
def SET_WIFI_CREDS(ctx, message):
    WiFiCreds = message.payload
    pass

typeDic = {
# 100:PING,
# 21:ACTIVE_SENSORS,
20:UPDATE_SENSORS,
8:'SCRIPTS_UPDATE',
3:SET_WIFI_CREDS,
}
def err(err):
    print(err)

class WAMP(ApplicationSession):
    def __init__(self,gg=None):
        ApplicationSession.__init__(self,gg)
        self.cb = None
        self._config = json.load(
            open('id.json')
        )
        self.generate_token()
        logger.debug('WAMP Server Setup')
        pass
    def set_broadcast(self,cb):
        logger.debug('WAMP now has broadcast ability')
        self.cb = cb

    def generate_token(self):
        self.token = (jwt.encode({"id":self._config['RouterID']},self._config['SharedSecretKey'], algorithm="HS256"))

    def onJoin(self, details):
        logger.debug('Connected to WAMP router')
        self.subscribe(self.onEvent,self._config['RouterID'])
        reactor.callLater(10,self.do_ping)

    def do_ping(self):
        logger.debug('sent Ping')
        self.publish(self._config['RouterID'],{u'type':100,u'token':self.token})

    def onEvent(self, message, evt=None):
        type_check(message,dict)
        type_check(message['type'],long)
        s= typeDic.get(message['type'])
        s(self, message)

    def connectionLost(self, reason):
        logger.debug('Disconnected from WAMP router')
        pass
