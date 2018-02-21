import unittest, random, uuid, time
from pi import DBHandler, Cache
def getGUID():
    return str(uuid.uuid4())
def randFloat(limit=10.0):
    return random.uniform(0.0,limit)
def getResponse(device_id):
    return {
        'SENSORID':device_id,
        'light':randFloat(),
        'sound':randFloat(),
        'UV':randFloat(),
        'IR':randFloat(),
        'humid':randFloat(),
        'temp':randFloat(),
        'tiltX':randFloat(),
        'tiltY':randFloat(),
    }
class TestUtils(unittest.TestCase):

    def test_DBHandler(self):
        db = DBHandler("dddd")
        db.start()
        testGoodData = []
        NumberOfSensors = 10
        NumberOfDataPerSensor = 10
        i = 0
        sensorIDs = []
        while i<NumberOfSensors:
            sensorID = getGUID()
            sensorIDs.append(sensorID)
            j=0
            while j < NumberOfDataPerSensor:
                db.push({
                    'type':'SENSORDATA',
                    'device_id':sensorID,
                    'data':getResponse(sensorID),
                })
                j+=1
            i+=1
        time.sleep(10) # i know this is bad practise but when running irl the main thread is in a loop
        c = Cache('dddd')
        for sensorID in sensorIDs:
            self.assertEqual(len(c.getSensorDataFromID(sensorID)),NumberOfDataPerSensor)
