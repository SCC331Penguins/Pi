import logging
from Queue import Queue
from threading import Thread
from .cache import *

logger = logging.getLogger()

class DBHandler:
    def __init__(self, cacheName):
        self.cacheName = cacheName
        self.queue = Queue()
        self.workers = []
    def push(self,dataAr):
        logger.debug('adding To Q')
        self.queue.put(dataAr)
    def pull(self):
        logger.debug('getting item')
        return self.queue.get();
    def addWorkerThread(self):
        t = DBWorker(self.cacheName, self)
        t.daemon = True
        self.workers.append(t)
        t.start()
    def start(self):
        self.addWorkerThread()

class DBWorker(Thread):
    def __init__(self,cacheName, db):
        Thread.__init__(self)
        self.db = db
        self.cacheName = cacheName
    def run(self):
        self.cache = Cache(self.cacheName)
        print('Started')
        while True:
            dataAr = self.db.pull()
            logger.debug('adding To DB')
            self.cache.addSensorData(dataAr[0],dataAr[1])
            logger.debug('done')
class DBWatcher(Thread):
    def __init__(self, db):
        Thread.__init__(self)
        self.db = db
