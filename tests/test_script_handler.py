import unittest, random, uuid, time, string
from pi import ScriptHandler, Cache
def getRandomString():
    return ''.join(random.choice(string.printable) for i in range(350))
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

    def test_ScriptHandler(self):
        pass
        # db = ScriptHandler("dddd")
        # db.start()
        # sh = ScriptHandler("dddd")
        # sh.start()
        # NumberOfDataPerSensor = 10
        # scripts = []
        # while len(scripts) < NumberOfDataPerSensor:
        #     scripts.append(getRandomString())
        # db.push(['updateScripts',scripts])
        # c = Cache('dddd')
        # self.assertEqual(len(c.getScripts()),NumberOfDataPerSensor)
