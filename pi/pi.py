import sys, jwt, logging, time
from twisted.internet import protocol, reactor
from mqtt.client.factory import MQTTFactory
from twisted.internet.endpoints import clientFromString
# from Twitter import send_direct_message
logger = logging.getLogger()
from .db_handler import *
# from .actuator_handler import *
from .cache import *
from .actuator_handler import *
from .script_handler import *
from .mqtt_client import *
from .ws_server import *
class Pi:
    """
    This is the main class this handles the main Thread but when started fires off some daemons to handle other features such as Database, Actuators and Scripts
    """
    def __init__(self, args):
        self.restart = False
        pass
    def start(self, start_websocket_server=True, start_mqtt_client=True, websocket_server_port=8000, mqtt_client_port=1883, cacheName='Penguins'):
        # this function deals with most of the specifics that the pi can use
        if(not isValidCache(cacheName)):
            Cache(cacheName)
        self.cacheName  = cacheName
        self.start_websocket_server = start_websocket_server
        self.start_mqtt_client = start_mqtt_client
        logger.info("Starting Pi services...")
        if start_mqtt_client:
            self.create_mqtt_client(mqtt_client_port)
        if start_websocket_server:
            self.create_websocket_server(websocket_server_port)
        self.createDB()
        # self.createActuators()
        self.createScript()
        logger.info("Started  All Pi services")

    def createDB(self):
        # this creates the DB Thread and adds the handler to the Pi
        logger.info("Initiaizing Pi DB Queue...")
        self.db = DBHandler(self.cacheName, self.mqtt_service.sendMsg)
        self.db.start()
        logger.info("Initiaized Pi DB Queue")

    def createActuators(self):
        # this creates the Actuator Thread and adds the handler to the Pi
        logger.info("Initiaizing Pi Actuators...")
        sendMsg = None
        if(self.start_mqtt_client):
            sendMsg =  self.mqtt_service.sendMsg
        self.actHandler = ActuatorHandler(self.cacheName,sendMsg)
        self.actHandler.start()
        logger.info("Initiaized Pi Actuators")

    def createScript(self):
        # this creates the Script Thread and adds the handler to the Pi
        logger.info("Initiaizing Pi Scripts Queue...")
        self.scripts = ScriptHandler(self.cacheName,self.actHandler, self.mqtt_service)
        self.scripts.start()
        if(self.start_websocket_server):
            self.ws_server.addPushCommand(self.scripts.pushCommand)
        logger.info("Initiaized Pi Scripts Queue")

    def run(self):
        self.link_client_to_server()
        reactor.run()
        while(self.restart):
            self.restart = False
            print('---===Restarting===---')
            time.sleep(2)
            os.execl(sys.executable, sys.executable, *sys.argv)
        # you are here when Ctrl C is pressed
    def doRestart(self):
        self.restart = True
    def test(self):
        cache = Cache(self.cacheName)
        try:
            print('testing')
            scripts = cache.getScripts()
            print cache.getSensorData()
            while True:
                self.scripts.pushCommand('print "hello33"')
                raw_input('waiting')
        except Exception as e:
            print e
    def addToDB(self, device_id, data):
        self.db.push({
            'type':'SENSORDATA',
            'device_id':device_id,
            'data':data,
        })
    def alert(self, zone):
        sensors = ['240042000b51353432383931',
        '1b002a001247343438323536',
        '1e0025001147353230333635']

        alertConfig = [
            {"type":'Kettle', "command":"turnOn"},
            {"type":'Lights', "command":"g"+str(sensors.index(zone)+1)+"LightsOn"},
            {"type":'Plug', "command":"turn_on_plug"},
        ]
        for conf in alertConfig:
            code = """for item in actuators:
            if item['type'] == '{}':
                {}(item,'{}')
            """.format(conf['type'],conf['command'])
            self.scripts.pushCommand(code)
            # send_direct_message("An alarm in your house was triggered.", 'EduardSchlotter')

    def create_websocket_server(self, port):
        # creates WS Server
        logger.info("Starting websocket server...")
        self.ws_server = WSServerFactory(self.addToDB, self.cacheName)
        if(self.start_mqtt_client):
            self.ws_server.addMQTTCallback(self.mqtt_service.sendMsg)
        self.ws_server.protocol = WSProtocol
        reactor.listenTCP(8000,self.ws_server)
        logger.info("Started websocket server")

    def create_mqtt_client(self, port=1883, path=u'ws', realm=u'default', ip='localhost'):
        # creates WAMP Server
        url = 'tcp:'+ip+':'+str(port)
        logger.info('mqtt://'+url)
        logger.info("Starting MQTT client...")
        self.mqtt_client = MQTTFactory(profile=MQTTFactory.PUBLISHER | MQTTFactory.SUBSCRIBER)
        self.mqtt_service = MQTTService(clientFromString(reactor,url),self.mqtt_client)
        self.mqtt_service.startService()
        self.createActuators()
        logger.info("Started MQTT client")
    def link_client_to_server(self):
        self.mqtt_service.set_rs_callback(self.doRestart)
        self.mqtt_service.set_broadcast(self.ws_server.broadcast,self.db.updateScripts)
        self.ws_server.addAlertDB(self.alert, self.db)
        self.mqtt_service.addDataChannelHandlers(self.ws_server.addDataChannel, self.ws_server.removeDataChannel, self.scripts.pushCommand, self.db)
