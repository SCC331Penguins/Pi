import logging
from Queue import Queue
from threading import Thread
from .cache import *

logger = logging.getLogger()

class DBHandler:
    """
    This Handles the Queue which The Worker pulls from in order to determine what DB inserts to DO
    """
    def __init__(self, cacheName, sendMsg):
        self.cacheName = cacheName
        self.queue = Queue()
        self.sendMsg = sendMsg
        self.workers = []
    def push(self,evt):
        self.queue.put(evt)
    def pull(self):
        return self.queue.get();
    def addWorkerThread(self):
        t = DBWorker(self.cacheName, self)
        t.daemon = True
        self.workers.append(t)
        t.start()
    def updateScripts(self, scripts):
        self.queue.put({
            'type':'UPDATESCRIPTS',
            'data':scripts,
        })
    def updateSensorData(self):
        self.queue.put({
            'type':'UPDATESENSORS',
        })
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
            evt = self.db.queue.get()
            print(evt)
            if(evt['type'] == 'UPDATESCRIPTS'):
                self.cache.updateScripts(evt['data'])
                logger.debug('Updated Scripts')
            elif evt['type'] == 'SENSORDATA':
                self.cache.addSensorData(evt['device_id'], evt['data'])
                logger.debug('Added data for ' + evt['device_id'])
            elif evt['type'] == 'UPDATESENSORS':
                data = self.cache.getSensorData()
                self.db.sendMsg('DATA',data)
            else:
                logger.debug('invalid evt')
            self.db.queue.task_done()
