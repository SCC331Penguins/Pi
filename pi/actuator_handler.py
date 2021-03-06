import logging
from Queue import Queue
from threading import Thread
from .cache import *
from .Actuator import *

logger = logging.getLogger()

class ActuatorHandler:
    """
    This Handles the Queue which The Worker pulls from in order to determine what Actuators are on the network
    """
    def __init__(self, cacheName):
        self.cacheName = cacheName
        self.queue = Queue()
        self.workers = []
        self.actuators = []
    def push(self):
        self.queue.put(1)
    def pull(self):
        return self.queue.get();
    def getActuators(self):
        return self.actuators
    def setActuators(self, actuators):
        self.actuators = actuators
    def addWorkerThread(self):
        t = ActuatorWorker(self.cacheName, self)
        t.daemon = True
        self.workers.append(t)
        t.start()
        self.push()
    def start(self):
        self.addWorkerThread()

class ActuatorWorker(Thread):
    """
    This uses the Actuators class to determine what Actuators are on the network this takes a long time so it is on its own thread
    """
    def __init__(self,cacheName, db):
        Thread.__init__(self)
        self.db = db
        self.cacheName = cacheName
    def run(self):
        self.cache = Cache(self.cacheName)
        logger.info('Actuator Thread Started')
        while True:
            var = self.db.pull()
            if(var == 1):
                actuators = findDevices()
                this.db.setActuators(actuators)
            logger.info('Added Actuators')
