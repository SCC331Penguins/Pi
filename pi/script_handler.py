import logging, time
from Queue import Queue
from threading import Thread
from .cache import *
from Actuator import ActuatorFunctions
logger = logging.getLogger()
DATA_COUNT_BEFORE_REFRESH = 100

def toValidScript(script):
    return urllib.unquote_plus(script)

class ScriptHandler:
    """
    This Handles the Queue which The Worker pulls from in order to determine what Scripts get updated
    """
    def __init__(self, cacheName, actHandler, mqttClient):
        self.cacheName = cacheName
        self.queue = Queue()
        self.workers = []
        self.actHandler = actHandler
        self.mqttClient = mqttClient
    def push(self,dataAr):
        self.queue.put(dataAr)
    def pushCommand(self,script):
        self.queue.put(script)
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
        self.data = {"430032000f47353136383631":{"light":1.2}}
        self.count = 0
        self.cacheName = ctx.cacheName
        self.handler = ctx
        self.queue = Queue()
        self.actHandler = actHandler
    def run(self):
        self.cache = Cache(self.cacheName)
        logger.info('Script Thread Started')
        time.sleep(10)
        while True:
            self.scripts = []
            self.scripts = self.cache.getScripts()
            while self.count < DATA_COUNT_BEFORE_REFRESH:
                # self.data.update(self.cache.getSensorData())
                self.evaluateData()
                self.count += 1
            self.count = 0
    def removeScript(self, script):
        def remove():
            self.scripts.remove(script)
        return remove

    def evaluateData(self):
        actuators = self.actHandler.getActuators()
        stateData = {'sensors': self.data, "actuators":actuators}

        stateData.update(ActuatorFunctions)
        if self.handler.queue.qsize() > 0:
            logger.info('executing....')
            logger.info(actuators)
            exec(self.handler.queue.get(),stateData)
        for script in self.scripts:
            try:
                # turnOnKettle("192.168.0.102")
                # send_message_lights("420","AC:CF:23:A1:FB:38")
                exec(toValidScript(script), stateData,{"ret":self.removeScript(script)})
            except Exception as e:
                logger.error(e)
                pass
