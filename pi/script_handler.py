import logging
from Queue import Queue
from threading import Thread
from .cache import *

logger = logging.getLogger()
DATA_COUNT_BEFORE_REFRESH = 100

def toValidScript(script):
    return urllib.unquote_plus(script)

class ScriptHandler:
    """
    This Handles the Queue which The Worker pulls from in order to determine what Scripts get updated
    """
    def __init__(self, cacheName, actHandler):
        self.cacheName = cacheName
        self.queue = Queue()
        self.workers = []
        self.actHandler = actHandler
    def push(self,dataAr):
        self.queue.put(dataAr)

    def pull(self):
        return self.queue.get()

    def addWorkerThread(self):
        t = ScriptWorker(self, self.actHandler)
        t.daemon = True
        self.workers.append(t)
        t.start()

    def start(self):
        self.addWorkerThread()

class ScriptWorker(Thread):
    """
    This Worker updates Scripts
    """
    def __init__(self,ctx, actHandler):
        Thread.__init__(self)
        self.data = {}
        self.count = 0
        self.cacheName = ctx.cacheName
        self.handler = ctx
        self.actHandler = actHandler
    def run(self):
        self.cache = Cache(self.cacheName)
        logger.info('Script Thread Started')
        while True:
            self.scripts = self.cache.getScripts()
            while self.count < DATA_COUNT_BEFORE_REFRESH:
                newData = self.handler.pull()
                self.data.update(newData)
                self.evaluateData()
                self.count += 1
            self.count = 0
    def evaluateData(self):
        actuators = actHandler.getActuators()
        for script in self.scripts:
            try:
                exec(toValidScript(script), {'sensors': self.data, 'actuators':actuators})
            except:
                pass
