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
    def __init__(self, cacheName, send_actuators=None):
        self.cacheName = cacheName
        self.queue = Queue()
        self.workers = []
        self.actuators = []
        self.send_actuators = send_actuators
    def push(self):
        self.queue.put(1)
    def pull(self):
        return self.queue.get();
    def getActuators(self):
        return self.actuators
    def setActuators(self, actuators):
        self.actuators = actuators
    def addWorkerThread(self):
        t = ActuatorWorker(self.cacheName, self, self.send_actuators)
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
    def __init__(self,cacheName, handler, send_actuators):
        Thread.__init__(self)
        self.handler = handler
        self.cacheName = cacheName
        self.send_actuators = send_actuators
    def run(self):
        self.cache = Cache(self.cacheName)
        logger.info('Actuator Thread Started')
        while True:
            # needs to be uncommented before release this makes it constantly refresh the Actuators with is very network heay
            # var = 1
            # var = self.handler.pull()
            # if(var == 1):
            logger.info('doing Scan for Actuators')
            actuators = findDevices()
            logger.info('found Devices')
            if(self.send_actuators is not None):
                pass
                # self.send_actuators('REGACT',actuators)
            print(actuators)
            logger.info('Sent Actuators')
            self.handler.setActuators(actuators)
            logger.info('Added Actuators')
