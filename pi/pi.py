import sys, jwt, logging
from twisted.internet import protocol, reactor
from autobahn.twisted.wamp import ApplicationRunner
logger = logging.getLogger()
from .db_handler import *
from .wamp_client import *
from .ws_server import *
class Pi:
    def __init__(self, args):
        pass
    def start(self, start_websocket_server=True, start_wamp_client=True, websocket_port=8000, wamp_port=8080, cacheName='Penguins'):
        logger.debug("Initiaizing Pi DB Queue...")
        self.db = DBHandler(cacheName)
        self.db.start()
        logger.debug("Initiaized Pi DB Queue...")
        logger.debug("Starting Pi services...")
        if start_websocket_server:
            self.create_websocket_server(websocket_port)
        if start_wamp_client:
            self.create_wamp_client(wamp_port)
        logger.debug("Started Pi services")
    def run(self):
        reactor.run()
        # you are here when Ctrl C is pressed
    def addToDB(self, device_id, data):
        self.db.push([device_id,data])
    def create_websocket_server(self, port):
        logger.debug("Starting websocket server...")
        self.ws_server = WSServerFactory(self.addToDB)
        self.ws_server.protocol = WSProtocol
        reactor.listenTCP(port,self.ws_server)
        logger.debug("Started websocket server")

    def create_wamp_client(self, port=8080, path=u'ws', realm=u'default', ip='127.0.0.1'):
        logger.debug("Starting WAMP client...")
        wamp = WAMP()
        url = u'ws://'+ip+':'+str(port)+'/'+path
        s = ApplicationRunner(url, realm).run(wamp,start_reactor=False)
        def help(gg):
            self.wamp_client = wamp
            self.wamp_client.protocol = gg
            self.wamp_client.set_broadcast(self.ws_server.broadcast)
            logger.debug("Started WAMP client")
        s.addCallback(help)
