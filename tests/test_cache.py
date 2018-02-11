import unittest, os
from threading import Thread
from pi import Cache
class TestCache(unittest.TestCase):
    def test_CacheInitial(self):
        c = Cache("testingCache", new=True)
        # c.init(debug=True)
        data = {'light':0.8, 'sound':10}
        # allows valid data
        self.assertTrue(c.addSensorData("TESTDEVICEID",data))
        data2 = {'light':'}99-=odfs=sdfj', 'sound':True}
        # disallows invalid data
        self.assertFalse(c.addSensorData("TESTDEVICEID",data2))
    def test_CacheGET(self):
        data2 = {'light':'lll', 'sound':True}
        c = Cache("testingCache")
        c.getSensorDataFromID("TESTDEVICEID",Limit=10)
        c.getSensorDataFromID("TESTDEVICEID")
        self.assertRaises(ValueError,c.getSensorDataFromID,"TESTDEVICEID",Limit=0)
        self.assertFalse(c.addSensorData("TESTDEVICEID",data2))
    def test_Cache(self):

        c = Cache("testingCache")
        threads = []
        i = 0
        data = {'light':0.8, 'sound':10}
        while i<10:
            c.addSensorData('TESTDEVICEID',data)
            c.getSensorDataFromID("TESTDEVICEID")
            i=i+1
        c.getSensorDataFromID("TESTDEVICEID",Limit=10)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        c.getSensorDataFromID("TESTDEVICEID",Limit=10)
