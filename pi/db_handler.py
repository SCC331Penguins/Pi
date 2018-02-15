import logging
from Queue import Queue
from threading import Thread
from .cache import *

logger = logging.getLogger()

class DBHandler:
    """
    This Handles the Queue which The Worker pulls from in order to determine what DB inserts to DO
    """
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
    def updateScripts(self, scripts):
        self.queue.put(['updateScripts',scripts])
    def start(self):
        self.addWorkerThread()

class DBWorker(Thread):
    """
    This uses the Cache class to INSERT into the DB
    """
    def __init__(self,cacheName, db):
        Thread.__init__(self)
        self.db = db
        self.cacheName = cacheName
    def run(self):
        self.cache = Cache(self.cacheName)
        logger.info('DB Thread Started')
        while True:
            dataAr = self.db.pull()
            if(dataAr[0]=='updateScripts'):
                self.cache.updateScripts(dataAr[1])
            else:
                self.cache.addSensorData(dataAr[0],dataAr[1])
            logger.debug('Added data for ' + dataAr[0])
