import unittest, random, uuid, time
from pi import DBHandler, Cache
def getGUID():
    return str(uuid.uuid4())
def randFloat(limit=10.0):
    return random.uniform(0.0,limit)
def randInt(limit=9999):
    return random.randint(0,limit)
def getResponse(device_id, j):
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
        'time':j*30, # needs to be a divisor of 30 because only 2 records a min should be commited to Cache
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
                    'data':getResponse(sensorID,j),
                })
                j+=1
            i+=1
        time.sleep(10) # i know this is bad practise but when running irl the main thread is in a loop
        c = Cache('dddd')
        for sensorID in sensorIDs:
            self.assertEqual(len(c.getSensorDataFromID(sensorID)),NumberOfDataPerSensor)
