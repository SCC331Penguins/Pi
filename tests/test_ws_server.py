import unittest, random, time
from pi import WSServerFactory, Cache, Pi
from json import dumps
def randFloat(limit=1.0):
    return random.uniform(0.0,limit)
class TestWSServer(unittest.TestCase):
    def test_onMessageToDB(self):
        p = Pi([])
        p.start(start_wamp_client=False, cacheName='onMessageTest')
        total =  random.randint(0,30)
        device_id = 'TESTDEVICEID'
        j = 0
        while j<total:
            data = {
                'SENSORID':device_id,
                'light':randFloat(),
                'sound':randFloat(),
                'UV':randFloat(),
                'IR':randFloat(),
                'humid':randFloat(),
                'temp':randFloat(),
                'tiltX':randFloat(),
                'tiltY':randFloat(),
                'tiltZ':randFloat(),
            }
            # this is the function onMessage calls to add to DB
            p.addToDB(device_id,data)
            j=j+1
        time.sleep(10) # i know this is bad practise but when running irl the main thread is in a loop
        c = Cache('onMessageTest')
        self.assertEqual(len(c.getSensorDataFromID(device_id)),total)
