import sys
from WAMP import *
class Pi:
    def __init__(self, args):
        print('Pi')
        self.WAMP = WAMP(8080,"sccug-330-02.lancs.ac.uk",8080);
        pass
    def startupWAMP(self):
        pass
    def startupHTTP(self):
        pass
    def stopWAMP(self):
        pass
    def stopHTTP(self):
        pass

if __name__ == '__main__':
    # default setup
    Pi()
