from connection import *
class WAMP:
    def __init__(self,localPort, serverIP, serverPort):
        print('Wamp')
        self.localConnection = Connection('local',handler=self.handleMessage)
        self.localConnection.connect()
    def run(self):
        pass
    def handleMessage(self, message):
        pass
    def stop(self):
        pass
