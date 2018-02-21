from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession
from json import dumps
from twisted.internet.defer import inlineCallbacks
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
20:UPDATE_SENSORS,
8:SCRIPTS_UPDATE,
3:SET_WIFI_CREDS,
}
def err(err):
    print(err)

class WAMP(ApplicationSession):
    def __init__(self):
        ApplicationSession.__init__(self)
        self.cb = None
        self.updateScripts = None
        self._config = json.load(
            open('id.json')
        )
        self.generate_token()
        logger.info('WAMP Server Setup')

    def set_broadcast(self, cb, scripts):
        logger.info('WAMP now has broadcast ability')
        self.updateScripts = scripts
        self.cb = cb

    def generate_token(self):
        self.token = (jwt.encode({"id":self._config['RouterID']},self._config['SharedSecretKey'], algorithm="HS256"))

    def onJoin(self, details):
        logger.info('Connected to WAMP router')
        self.subscribe(self.onEvent,self._config['RouterID'])
        reactor.callLater(1,self.do_ping)

    def do_ping(self):
        logger.info('sent Ping')
        # self.publish(u"SCC33102_R01",{"source": 0, "token": 0, "type": 8, "payload": ["print%28%27hi+script%27%29", "print%28%27hi+script%27%29"]})
        self.publish(self._config['RouterID'],{u'type':100,u'token':self.token, u'payload':0})
        reactor.callLater(10,self.do_ping)

    def onEvent(self, message, evt=None):
        logger.info('received'+ dumps(message))
        type_check(message,dict)
        # type_check(message['type'],long)
        s= typeDic.get(message['type'])
        s(self, message)

    def connectionLost(self, reason):
        logger.info('Disconnected from WAMP router')
        pass
