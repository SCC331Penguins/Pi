import sys, jwt, logging
from twisted.internet import protocol, reactor
from autobahn.twisted.wamp import ApplicationRunner
logger = logging.getLogger()
from .db_handler import *
# from .actuator_handler import *
from .cache import *
from .actuator_handler import *
from .script_handler import *
from .wamp_client import *
from .ws_server import *
class Pi:
    """
    This is the main class this handles the main Thread but when started fires off some daemons to handle other features such as Database, Actuators and Scripts
    """
    def __init__(self, args):
        pass
    def start(self, start_websocket_server=True, start_wamp_client=True, websocket_port=8000, wamp_port=8080, cacheName='Penguins'):
        # this function deals with most of the specifics that the pi can use
        if(not isValidCache(cacheName)):
            Cache(cacheName)
        self.cacheName  = cacheName
        self.createDB()
        self.createActuators()
        self.createScript()
        logger.info("Starting Pi services...")
        if start_websocket_server:
            self.create_websocket_server(websocket_port)
        if start_wamp_client:
            self.create_wamp_client(wamp_port)
        logger.info("Started  All Pi services")

    def createDB(self):
        # this creates the DB Thread and adds the handler to the Pi
        logger.info("Initiaizing Pi DB Queue...")
        self.db = DBHandler(self.cacheName)
        self.db.start()
        logger.info("Initiaized Pi DB Queue")

    def createActuators(self):
        # this creates the Actuator Thread and adds the handler to the Pi
        logger.info("Initiaizing Pi Actuators...")
        self.actHandler = ActuatorHandler(self.cacheName)
        self.actHandler.start()
        logger.info("Initiaized Pi Actuators")

    def createScript(self):
        # this creates the Script Thread and adds the handler to the Pi
        logger.info("Initiaizing Pi Scripts Queue...")
        self.scripts = ScriptHandler(self.cacheName,self.actHandler)
        self.scripts.start()
        logger.info("Initiaized Pi Scripts Queue")

    def run(self):
        reactor.run()
        # you are here when Ctrl C is pressed

    def addToDB(self, device_id, data):
        self.db.push([device_id,data])

    def create_websocket_server(self, port):
        # creates WS Server
        logger.info("Starting websocket server...")
        self.ws_server = WSServerFactory(self.addToDB)
        self.ws_server.protocol = WSProtocol
        reactor.listenTCP(port,self.ws_server)
        logger.info("Started websocket server")

    def create_wamp_client(self, port=8080, path=u'ws', realm=u'default', ip='127.0.0.1'):
        # creates WAMP Server
        logger.info("Starting WAMP client...")
        wamp = WAMP()
        url = u'ws://'+ip+':'+str(port)+'/'+path
        s = ApplicationRunner(url, realm).run(wamp, start_reactor=False)
        def help(gg):
            self.wamp_client = wamp
            self.wamp_client.set_broadcast(self.ws_server.broadcast,self.db.updateScripts)
            self.wamp_client.protocol = gg

            logger.info("Started WAMP client")
        s.addCallback(help)
