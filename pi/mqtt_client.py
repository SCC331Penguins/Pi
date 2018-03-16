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

def ARM(ctx, message):
    ctx.armed = message['payload']
    ctx.db.setStatus({'armed':ctx.armed})
def PHOLOC(ctx, message):
    ctx.userlocation = message['payload']
    logger.info('Phone Location is ' + ctx.userlocation)
    ctx.db.setStatus({'userlocation':ctx.userlocation})

def CONFIB(ctx, message):
    logger.debug(message['payload'])
    ctx.configButtons = message['payload']
    ctx.db.push({
    'type':'SETBUTTONCONFIG',
    'data':message['payload']
    })

def UPDATE_SCRIPTS(self, message):
    logger.debug('Scripts Updating')
    try:
        logger.info('UPDATE_SCRIPTS')
        self.updateScripts(message['payload'])
    except Exception as e:
        logger.error(e)

def COMMAND(self, message):
    payload = message['payload']
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
    self.pushCommand(pythonCode)

def NEW_CHANNEL(self, message):
    channelName = message['payload']
    self.addChannel(channelName)
    time.sleep(3)
    self.sendMsg('YOPHO',{},topic=channelName)
def GIVE_DATA(self, message):
    payload = message['payload']
    self.addDataChannel(payload['sensor_id'], payload['channel_id'])
def STOP_DATA(self, message):
    self.removeDataChannel(payload['sensor_id'], payload['channel_id'])
def RSTART(self, message):
    self.restart()
    reactor.stop()

def SHTDWN(self, message):
    reactor.stop()
def SLPPHN(self, message):
    print self.cache.getSensorIDs()[0]
    sensors = self.cache.getSensorIDs()
    # for sensor in sensors:
    #     logger.info('id:{},Sleep:1600'.format(sensor['SENSORID']))
    #     time.sleep(1)
    self.cb('id:{};id:{};id:{},Sleep:1600'.format(sensors[0]['SENSORID'],sensors[1]['SENSORID'],sensors[2]['SENSORID']))
    pass

typeDic = {
# 'PING':PING,
# 'ACTSEN':ACTIVE_SENSORS,
# 'DATA':DATA,
# 'REGACT':REG_ACT,
'UPDSEN':UPDATE_SENSORS,
'UPDSCR':UPDATE_SCRIPTS,
'WIFICR':SET_WIFI_CREDS,
'COM':COMMAND,
'NCHAN':NEW_CHANNEL,
'GDATA':GIVE_DATA,
'SDATA':STOP_DATA,
'PHOLOC':PHOLOC,
'CONFIB':CONFIB,
'RSTART':RSTART,
'SHTDWN':SHTDWN,
'SLPPHN':SLPPHN,
}
def err(err):
    logger.error(err)

class MQTTService(ClientService):
    def __init__(self, endpoint, factory):
        ClientService.__init__(self, endpoint, factory, retryPolicy=backoffPolicy())
        self.cb = None
        self.updateScripts = None
        self._config = json.load(
            open('id.json')
        )
        self.generate_token()
        self.channels = ['SCC33102_R01']
        self.cache = Cache('Penguins')
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
            reactor.callLater(1,self.do_ping)
            self.doDBUpdate()
            logger.info("Connected to MQTT Server")

    def addChannel(self, channel):
        logger.info(self.channels)
        self.channels.append(channel)
        self.protocol.subscribe(str(channel))
    def set_rs_callback(self, cb):
        self.restart = cb;
    def subscribe(self):
        for channel in self.channels:
            self.protocol.subscribe(channel)

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

    def sendMsg(self, typeStr, payload, topic=None, msgObject={}):
        if(topic == None):
            topic = self._config['RouterID']
        msgObject[u'type'] = typeStr
        msgObject[u'payload'] = payload
        msgObject[u'token'] = self.token
        self.publish(topic,json.dumps(msgObject,ensure_ascii=False).encode())

    def do_ping(self):
        logger.info('sent Ping')
        logger.error('ggg')
        # self.publish(u"SCC33102_R01",{"source": 0, "token": 0, "type": 8, "payload": ["print%28%27hi+script%27%29", "print%28%27hi+script%27%29"]})
        self.sendMsg('PING',None)
        reactor.callLater(10,self.do_ping)

    def doDBUpdate(self):
        self.db.updateSensorData()
        reactor.callLater(60,self.doDBUpdate)

    def onPublish(self, topic, payload, qos, dup, retain, msgId):
        msg = json.loads(str(payload))
        type_check(msg,dict)
        # type_check(message['type'],long)
        s= typeDic.get(msg['type'])
        logger.info('received message of type: ' + msg['type']);
        if s is not None:
            s(self, msg)
    def addDataChannelHandlers(self, addDataChannel, removeDataChannel, pushCommand, db):
        self.addDataChannel = addDataChannel
        self.db = db
        self.removeDataChannel = removeDataChannel
        self.pushCommand = pushCommand
    def publish(self, topc, msg, q=2):
        self.protocol.publish(topic=topc, qos=1, message=msg)

    def onDisconnection(self, reason):
        logger.info('Disconnected from WS Server ')
        self.whenConnected().addCallback(self.connectToBroker)
