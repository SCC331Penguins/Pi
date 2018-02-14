import logging
from Queue import Queue
from threading import Thread
from .cache import *

logger = logging.getLogger()

class ActuatorHandler:
    def __init__(self, cacheName):
        self.cacheName = cacheName
        self.queue = Queue()
        self.workers = []
    def push(self,dataAr):
        self.queue.put(dataAr)
    def pull(self):
        return self.queue.get();
    def addWorkerThread(self):
        t = DBWorker(self.cacheName, self)
        t.daemon = True
        self.workers.append(t)
        t.start()
    def updateScripts(scripts):
        self.queue.push(['updateScripts',html.unescape(script)])
    def start(self):
        self.addWorkerThread()

class ActuatorWorker(Thread):
    def __init__(self,cacheName, db):
        Thread.__init__(self)
        self.db = db
        self.cacheName = cacheName
    def run(self):
        self.cache = Cache(self.cacheName)
        logger.info('Actuator Thread Started')
        while True:
            dataAr = self.db.pull()
            if(dataAr[0]=='updateScripts'):
                self.cache.updateScripts(dataAr[1])
            else:
                self.cache.addSensorData(dataAr[0],dataAr[1])
            logger.debug('Added sensor data for ' + dataAr[0])
class ActuatorWatcher(Thread):
    def __init__(self, db):
        Thread.__init__(self)
        self.db = db
